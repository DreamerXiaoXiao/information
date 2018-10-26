import functools


def data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


@data
def num1():
    print(1)


@data
def num2():
    print(2)


if __name__ == '__main__':
    print(num1.__name__)
    print(num2.__name__)