
from misal.core.state import Stateful, A, Sample


# mock some functions for now

class Metadata(Stateful):

    def __init__(self, path):
        pass

    def save(self):
        pass

    def reset(self):
        pass

    def register(self, value: A) -> Sample[A]:
        pass


class Preprocessed(Stateful):

    def __init__(self, path):
        pass

    def save(self):
        pass

    def reset(self):
        pass

    def register(self, value: A) -> Sample[A]:
        pass


class Index(Stateful):

    def __init__(self, path, dist):
        pass

    def save(self):
        pass

    def reset(self):
        pass

    def register(self, value: A) -> Sample[A]:
        pass


if __name__ == '__main__':
    raise RuntimeError
