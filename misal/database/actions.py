from misal.core import action


@action.argument('path', 'a fastq file')
@action.action(save=True)
def add(metadata, preprocessed, index, path):
    pass


@action.argument('path', 'a fastq file')
@action.action(save=False)
def search(preprocessed, index, path):
    pass


if __name__ == '__main__':
    raise RuntimeError
