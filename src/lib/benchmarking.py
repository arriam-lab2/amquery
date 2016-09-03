import time
from functools import wraps


def measure_time(enabled):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args)
            end = time.time()
            print(func.__name__, "elapsed time:", end - start)
            return result

        return wrapper if enabled else func

    return decorator
