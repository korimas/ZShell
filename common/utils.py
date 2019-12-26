from PyQt5.QtCore import QRunnable, QThreadPool
from functools import wraps

pool = QThreadPool()
pool.setMaxThreadCount(10)


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


class SingletonMetaClass(type):

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__call__(*args, **kwargs)  # __call__ here is __init__ of new object
        return cls._instance


class Singleton(metaclass=SingletonMetaClass):
    pass
