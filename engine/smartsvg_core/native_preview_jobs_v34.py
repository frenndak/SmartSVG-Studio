"""V34-019/041/047 native UI read-only job coordination.

A single worker executes disk/ZIP inspection and PNG selection. Tkinter and all
UI mutations remain on the main thread. Results from obsolete generations
must never be displayed. No ComfyUI/torch, server, network or project writes.
"""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Generic, TypeVar
from threading import Event, Lock

T = TypeVar("T")


class LatestOnlyJob(Generic[T]):
    """Bounded single-worker queue for interactive preview requests.

    A new request cancels the previous queued future, invalidates running
    results and schedules at most one additional request. An already running
    computation may finish, but its generation is stale. Never process UI
    callbacks from this class: poll futures from the Tk main thread.
    """

    def __init__(self, read: Callable[[str], T]):
        self._read = read
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="smartsvg-readonly")
        self._version = 0
        self._future: Future[T] | None = None
        self._closed = False
        self._lock = Lock()
        self._pending: tuple[str, Future[T]] | None = None
        self._draining = False

    def submit(self, path: str) -> tuple[int, Future[T]]:
        with self._lock:
            if self._closed:
                raise RuntimeError("NATIVE_JOB_QUEUE_CLOSED")
            previous = self._future
            displaced = self._pending
            previous_version = self._version
            self._version += 1
            version = self._version
            future: Future[T] = Future()
            self._future = future
            self._pending = (path, future)
            if not self._draining:
                self._draining = True
                # submit may enqueue a drain and still raise while starting a
                # worker. Gate it so an abandoned attempt cannot steal a later
                # selection, and roll back the unfinished generation.
                launch_gate = Event()
                authorized = [False]
                def guarded_drain():
                    launch_gate.wait()
                    if authorized[0]:
                        self._drain()
                try:
                    self._pool.submit(guarded_drain)
                except Exception:
                    launch_gate.set()
                    self._draining = False
                    self._future = previous
                    self._pending = displaced
                    self._version = previous_version
                    self._pool.shutdown(wait=False, cancel_futures=True)
                    self._pool = ThreadPoolExecutor(
                        max_workers=1, thread_name_prefix="smartsvg-readonly")
                    raise
                authorized[0] = True
                launch_gate.set()
        # Future.cancel invokes arbitrary callbacks synchronously. Publishing
        # the new state first, then cancelling outside the lock, also permits
        # callbacks to submit a newer selection without deadlock or overwrite.
        if previous is not None:
            previous.cancel()
        if displaced is not None:
            # The drain never claimed this removed slot. As its executor we
            # must notify wait()/as_completed() after cancelling it, exactly
            # once. A claimed request remains the drain's responsibility.
            displaced[1].set_running_or_notify_cancel()
        return version, future

    def _drain(self) -> None:
        while True:
            with self._lock:
                if self._closed or self._pending is None:
                    self._draining = False
                    return
                path, future = self._pending
                self._pending = None
            if not future.set_running_or_notify_cancel():
                continue
            try:
                result = self._read(path)
            except BaseException as exc:
                future.set_exception(exc)
            else:
                future.set_result(result)

    def current(self, version: int) -> bool:
        with self._lock:
            return not self._closed and version == self._version

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._version += 1
            future = self._future
            displaced = self._pending
            self._pending = None
        if future is not None:
            future.cancel()
        if displaced is not None:
            displaced[1].set_running_or_notify_cancel()
        self._pool.shutdown(wait=False, cancel_futures=True)
