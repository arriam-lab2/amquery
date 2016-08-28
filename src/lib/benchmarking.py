import time


class measure_time:
    def __init__(self, enabled):
        self.enabled = enabled

    class Wrapper:
        def __init__(self, f):
            self.f = f

        def __call__(self, *args, **kwargs):
            start = time.time()
            self.f(*args, **kwargs)
            end = time.time()
            print(self.f.__name__, "elapsed time:", end - start)

    def __call__(self, f):
        return self.Wrapper(f) if self.enabled else f


if __name__ == "__main__":
    import math

    @measure_time(enabled=True)
    def testf(x):
        for _ in range(x):
            math.factorial(x)

        print(x)

    testf(3000)
