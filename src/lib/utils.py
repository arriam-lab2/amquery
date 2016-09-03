import pickle


def singleton(cls):
    instances = {}

    @staticmethod
    def instance(*args):
        if cls not in instances:
            instances[cls] = cls(*args)

        return instances[cls]

    cls.instance = instance
    return cls


def cached(path):
    path = path

    def decorated(cls):
        cls.save = save
        cls.load = load
        return cls

    def save(self):
        pickle.dump(self, open(path, "wb"))

    @staticmethod
    def load():
        with open(path, 'rb') as f:
            return pickle.load(f)

    return decorated
