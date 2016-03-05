import random
import tempfile

def generate_read(length):
    alphabet = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(alphabet) for x in range(length))

def generate_file(count, length):
    tfile = tempfile.NamedTemporaryFile(dir='./data/', delete=False)
    with open(tfile.name, 'w') as f:
        s = '\n'.join(generate_read(length) for x in range(count))
        f.write(s)

def generate_data(nfiles, count, length):
    for i in range(nfiles):
        generate_file(count, length)


if __name__ == "__main__":
    generate_data(100, 100, 100)
