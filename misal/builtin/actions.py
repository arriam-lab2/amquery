from misal.core import toaction, argument


@argument('path', 'a file to write to')
@argument('text', 'some text to write')
@toaction(save=False, description='Write text to a file')
def echoto(metadata, preprocessed, path: str, text: str):
    # the first two arguments are here for testing purposes only
    with open(path, 'w') as out:
        print(text, file=out)


@argument('path', 'a fastq file')
@toaction(save=True, description='Add samples')
def add(metadata, preprocessed, index, path: str):
    pass


@argument('path', 'a fastq file')
@toaction(save=False, description='Search samples')
def search(preprocessed, index, path: str):
    pass


if __name__ == '__main__':
    raise RuntimeError
