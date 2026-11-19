"""Run a native writer only after the UI has accepted and tracked its launch."""
from contextlib import contextmanager
from threading import Event


@contextmanager
def tracked_native_write(executor, writer, /, *args, **kwargs):
    ready = Event()
    authorized = False

    def guarded_write(*writer_args, **writer_kwargs):
        ready.wait()
        if authorized:
            return writer(*writer_args, **writer_kwargs)

    try:
        # submit() may enqueue the callable before a thread-start error.
        # Do not let it write until the caller has installed its completion poll.
        yield executor.submit(guarded_write, *args, **kwargs)
        authorized = True
    finally:
        ready.set()
