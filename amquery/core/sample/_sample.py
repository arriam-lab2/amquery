import os
import numpy as np
import functools
import itertools
import operator as op
import joblib
from Bio import SeqIO
from amquery.utils.decorators import hide_field
from amquery.utils.config import get_kmers_dir, get_sample_dir
from amquery.utils.iof import make_sure_exists


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


_alphabet = dict(zip([char for char in ('A', 'C', 'G', 'T')],
                     itertools.count()))


def _isvalid(sequence):
    return functools.reduce(op.and_, [char in _alphabet for char in sequence])


def _validate(sequence):
    return sequence if _isvalid(sequence) else []


def _transform(sequence):
    return np.array([_alphabet[char] for char in sequence], dtype=np.uint8)


def _parse_sample_name(sample_file):
    return os.path.basename(sample_file).split(".fasta")[0]


class Sample:
    def __init__(self, sample_file):
        self._name = _parse_sample_name(sample_file)
        self._source_file = SampleFile(sample_file)
        self._kmer_index = None

    @property
    def name(self):
        return self._name

    @property
    def original_name(self):
        return self._original_name

    @staticmethod
    def make_sample_obj_filename(source_filename):
        return os.path.join(get_sample_dir(), _parse_sample_name(source_filename))

    @staticmethod
    def make_kmer_index_obj_filename(source_filename):
        return os.path.join(get_kmers_dir(), _parse_sample_name(source_filename))

    @staticmethod
    def load(object_file):
        sample = joblib.load(object_file)
        return sample

    def load_kmer_index(self):
        self._kmer_index = joblib.load(Sample.make_kmer_index_obj_filename(self.source_file.path))

    @hide_field("_kmer_index")
    def _save(self):
        self._kmer_index = None
        joblib.dump(self, Sample.make_sample_obj_filename(self.source_file.path))

    def save(self):
        make_sure_exists(get_sample_dir())
        self._save()

        if self._kmer_index:
            joblib.dump(self._kmer_index, Sample.make_kmer_index_obj_filename(self.source_file.path))

    @property
    def source_file(self):
        return self._source_file

    @property
    def kmer_index(self):
        if not self._kmer_index:
            self.load_kmer_index()

        return self._kmer_index

    def set_kmer_index(self, index):
        self._kmer_index = index

    def iter_seqs(self):
        seqs_records = SeqIO.parse(open(self.source_file.path),
                                   self.source_file.file_format)
        for seq_rec in seqs_records:
            yield _transform(_validate(seq_rec.seq))
