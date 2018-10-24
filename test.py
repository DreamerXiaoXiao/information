def test(args):
    print(args)
    print(*args)


def test2(*args):
    print(args)


test([1,2,3])