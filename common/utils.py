from PyQt5.QtCore import QRunnable, QThreadPool
from functools import wraps

pool = QThreadPool()
pool.setMaxThreadCount(3)


class ZShellRunner(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        super(ZShellRunner, self).__init__()

    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            import traceback
            traceback.print_exc()


def do_in_thread(fn):
    @wraps(fn)
    def _inner_(*args, **kwargs):
        t = ZShellRunner(fn, *args, **kwargs)
        pool.start(t)

    return _inner_
