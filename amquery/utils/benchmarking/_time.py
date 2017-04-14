import time
import click
from functools import wraps


def measure_time(enabled):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args)
            end = time.time()
            click.secho("%s elapsed time: %f" % (func.__name__, end - start), fg='yellow')
            return result

        return wrapper if enabled else func

    return decorator
