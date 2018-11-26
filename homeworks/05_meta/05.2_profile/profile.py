from functools import wraps
from time import time, sleep
from types import FunctionType


def _decorator(func, klass=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if klass is None:
            name = func.__name__
        else:
            name = f"{klass.__name__}.{func.__name__}"
        print(f"`{name}` started")
        t_start = time()
        result = func(*args, **kwargs)
        print(f"`{name}` finished in {time() - t_start:.2f}s")
        return result
    return wrapper


def profile(obj):
    """Decorate all class methods and functions for time count"""
    if isinstance(obj, FunctionType):
        """Decorate a function"""
        return _decorator(obj)
    else:
        """Decorate class methods"""
        for attr_name in [func for func in obj.__dict__ if callable(getattr(obj, func))]:
            setattr(obj, attr_name, _decorator(getattr(obj, attr_name), obj))
        return obj


@profile
def foo_func(cnt):
    print('### __foo_func__ works ###')
    sleep(cnt)


@profile
class MyClass:
    def __init__(self):
        sleep(0.1)
        print(f'### {self.__class__.__name__} __init__ works ###')

    @classmethod
    def cls(cls):
        sleep(0.2)
        print(f'### {cls.__name__} __classmethod__ works ###')

    @staticmethod
    def sta():
        sleep(0.3)
        print(f'### MyClass __staticmethod__ works ###')

    def abc(self):
        sleep(0.4)
        print(f'### {self.__class__.__name__} __abc__ works ###')

    def xyz(self, cnt):
        sleep(cnt)
        print(f'### {self.__class__.__name__} __xyz__ works ###')


@profile
class Inherited(MyClass):
    def __init__(self):
        super(Inherited, self).__init__()
        sleep(0.1)
        print(f'### {self.__class__.__name__} __init__ works ###')

    def abc(self):
        sleep(0.4)
        print(f'### {self.__class__.__name__} __abc__ works ###')


if __name__ == "__main__":
    foo_func(1)
    foo_func(0.7)
    foo_func(0.5)
    a = MyClass()
    MyClass.cls()
    MyClass.sta()
    a.abc()
    a.xyz(1)
    print()
    b = Inherited()
    b.abc()
