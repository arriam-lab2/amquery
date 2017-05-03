def singleton(cls):
    instances = {}

    @staticmethod
    def instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)

        return instances[cls]

    cls.instance = instance
    return cls


def hide_field(*fields):
    def decorator(fn):
        def wrapped(*args, **kwargs):
            owner = args[0]
            values = [getattr(owner, f) for f in fields]
            for f in fields:
                delattr(owner, f)

            result = fn(*args, **kwargs)

            for field, value in zip(fields, values):
                setattr(owner, field, value)

            return result
        return wrapped
    return decorator
 