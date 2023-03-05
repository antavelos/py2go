mahi = 1
manu = True
alex: int = 1


def f(a: int) -> int:
    b = 1
    if a < 1:
        a = a + b
    return a


class A:
    def __init__(self, a: float):
        self.a = a

    def p(self):
        print(self.a)
