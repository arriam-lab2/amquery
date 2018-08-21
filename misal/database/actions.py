def add(metadata, preprocessed, index):
    return lambda: (metadata, preprocessed, index)


def search(preprocessed, index):
    return lambda: (preprocessed, index)


if __name__ == '__main__':
    raise RuntimeError
