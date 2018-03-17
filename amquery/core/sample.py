import os
import joblib
from Bio import SeqIO
from amquery.utils.decorators import hide_field
from amquery.utils.iof import make_sure_exists
from amquery.utils.config import get_kmers_dir, get_sample_dir


class SampleFile:
    def __init__(self, path: str):
        self._path = path
        self._format = os.path.splitext(os.path.basename(path))[1][1:]
        if self._format == 'fna':
            self._format = 'fasta'

    @property
    def path(self):
        return self._path

    @property
    def file_format(self):
        return self._format


def _parse_sample_name(sample_file):
    with open(sample_file, 'r') as f:
        line = ' '
        while line[0] != '>':
            line = f.readline()
        
        return line.split('_')[0].split('>')[1].strip()
        

class Sample:
    def __init__(self, sample_file, database_name):
        self._name = _parse_sample_name(sample_file)
        self._source_file = SampleFile(sample_file)
        self._kmer_index = None
        self._database_name = database_name

    @property
    def name(self):
        return self._name

    @staticmethod
    def make_sample_obj_filename(source_filename, database_name):
        return os.path.join(get_sample_dir(database_name), _parse_sample_name(source_filename))

    @staticmethod
    def make_kmer_index_obj_filename(source_filename, database_name):
        return os.path.join(get_kmers_dir(database_name), _parse_sample_name(source_filename))

    @staticmethod
    def load(object_file):
        sample = joblib.load(object_file)
        return sample

    def load_kmer_index(self, database_name):
        self._kmer_index = joblib.load(Sample.make_kmer_index_obj_filename(self.source_file.path, database_name))

    @hide_field("_kmer_index")
    def _save(self):
        self._kmer_index = None
        joblib.dump(self, 
                    Sample.make_sample_obj_filename(self.source_file.path, self._database_name))

    def save(self):
        make_sure_exists(get_sample_dir(self._database_name))
        self._save()

        if self._kmer_index:
            joblib.dump(self._kmer_index, 
                        Sample.make_kmer_index_obj_filename(self.source_file.path, self._database_name))

    @property
    def source_file(self):
        return self._source_file

    @property
    def kmer_index(self):
        if not self._kmer_index:
            self.load_kmer_index(self._database_name)

        return self._kmer_index

    def set_kmer_index(self, index):
        self._kmer_index = index

    def sequences(self):
        return [str(record.seq) for record in SeqIO.parse(
            self.source_file.path, self.source_file.file_format)
        ]
