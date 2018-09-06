from misal.core import toaction, argument


@argument('path', 'a fastq file')
@toaction(save=True, description='Add samples')
def add(metadata, preprocessed, index, path: str, arg2):
    pass


@argument('path', 'a fastq file')
@toaction(save=False, description='Search samples')
def search(preprocessed, index, path: str, arg2):
    pass


if __name__ == '__main__':
    raise RuntimeError
