"""V34-019/041/047 native UI read-only job coordination.

A single worker executes disk/ZIP inspection and PNG selection. Tkinter and all
UI mutations remain on the main thread. Results from obsolete generations
must never be displayed. No ComfyUI/torch, server, network or project writes.
"""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Generic, TypeVar

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

    def submit(self, path: str) -> tuple[int, Future[T]]:
        if self._closed:
            raise RuntimeError("NATIVE_JOB_QUEUE_CLOSED")
        self._version += 1
        if self._future is not None:
            self._future.cancel()  # queued future only; worker is cooperative
        self._future = self._pool.submit(self._read, path)
        return self._version, self._future

    def current(self, version: int) -> bool:
        return not self._closed and version == self._version

    def close(self) -> None:
        self._closed = True
        self._version += 1
        if self._future is not None:
            self._future.cancel()
        self._pool.shutdown(wait=False, cancel_futures=True)
