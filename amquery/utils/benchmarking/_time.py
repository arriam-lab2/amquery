import time
import click
import os
from functools import wraps
from amquery.utils.config import AMQ_VERBOSE_MODE


def measure_time(enabled):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args)
            end = time.time()
            if os.environ[AMQ_VERBOSE_MODE]:
                click.secho("%s elapsed time: %f" % (func.__name__, end - start), fg='yellow')
            return result

        return wrapper if enabled else func

    return decorator
