from collections import OrderedDict


def whenthen(func):

    class Wrapper:
        def __init__(self, base_function):
            self._base_func = base_function
            self._dict = OrderedDict()

        def __call__(self, *args, **kwargs):
            for when_func, then_func in self._dict.items():
                if when_func(*args, **kwargs):
                    return self._dict[when_func](*args, **kwargs)

            return self._base_func(*args, **kwargs)

        def when(self, when_func):
            self._dict[when_func] = None
            return self

        def then(self, then_func):
            self._dict[next(reversed(self._dict.keys()))] = then_func
            return self

    return Wrapper(func)

@whenthen
def fract(x):
    return x * fract(x - 1)


@fract.when
def fract(x):
    return x == 0


@fract.then
def fract(x):
    return 1


@fract.when
def fract(x):
    return x > 5


@fract.then
def fract(x):
    return x * (x - 1) * (x - 2) * (x - 3) * (x - 4) * fract(x - 5)


if __name__ == "__main__":
    print(fract(0))
    print(fract(1))
    print(fract(2))
    print(fract(5))
    print(fract(8))
    print(fract(10))
