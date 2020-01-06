import os
import time
import errno


class FileLockException(Exception):
    pass


class FileLock(object):

    def __init__(self, file_name, timeout=60, delay=.1):
        self._delay = delay
        self._fd = None
        self._lockfile = os.path.join(os.getcwd(), file_name)
        self._timeout = timeout

    def __enter__(self):
        start_time = time.time()
        while True:
            try:
                self._fd = os.open(self._lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if self._timeout is None:
                    raise FileLockException("Resource temporarily unavailable")
                if (time.time() - start_time) >= self._timeout:
                    raise FileLockException("Exceeded specified timeout.")
                time.sleep(self._delay)

    def __exit__(self, *args):
        os.close(self._fd)
        os.unlink(self._lockfile)
