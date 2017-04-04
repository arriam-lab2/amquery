import os
import numpy as np
import functools
import itertools
import operator as op
import joblib
import hashlib
from typing import Sequence, Any, List
from Bio import SeqIO

from amquery.utils.config import Config
from amquery.utils.decorators import hide_field


class SampleFile:

    def __init__(self, path: str):
        self._path = path
        self._format = os.path.splitext(os.path.basename(path))[1][1:]
        if self._format == 'fna':
            self._format = 'fasta'

    @property
    def path(self) -> str:
        return self._path

    @property
    def file_format(self) -> str:
        return self._format


_alphabet = dict(zip([char for char in ('A', 'C', 'G', 'T')],
                     itertools.count()))


def _isvalid(sequence: Sequence[Any]) -> bool:
    return functools.reduce(op.and_, [char in _alphabet for char in sequence])


def _validate(sequence: Sequence[Any]):
    return sequence if _isvalid(sequence) else []


def _transform(sequence: Sequence[Any]) -> List:
    return np.array([_alphabet[char] for char in sequence], dtype=np.uint8)

def _md5_hash(string: str) -> str:
    m = hashlib.md5()
    m.update(string.encode("utf8"))
    return m.hexdigest()


class Sample:

    def __init__(self, source_file: str):
        self._name = _md5_hash(source_file)
        self._original_name = os.path.splitext(os.path.basename(source_file))[0]
        self._source_file = SampleFile(source_file)
        self.kmer_index = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def original_name(self) -> str:
        return self._original_name

    @staticmethod
    def make_sample_obj_filename(config: Config, source_filename: str) -> str:
        return os.path.join(config.sample_dir, _md5_hash(source_filename))

    @staticmethod
    def make_kmer_index_obj_filename(config: Config, source_filename: str) -> str:
        return os.path.join(config.kmer_index_dir, _md5_hash(source_filename))
        
    @staticmethod
    def load(config: Config, object_file):
        sample = joblib.load(object_file)
        sample.load_kmer_index(config)
        return sample

    def load_kmer_index(self, config: Config) -> None:
        self.kmer_index = joblib.load(Sample.make_kmer_index_obj_filename(config, self.source_file.path))

    @hide_field("kmer_index")
    def _save(self, config: Config):
        joblib.dump(self, Sample.make_sample_obj_filename(config, self.source_file.path))
    
    def save(self, config: Config) -> None:
        self._save(config)
        
        if self.kmer_index:
            joblib.dump(self.kmer_index, Sample.make_kmer_index_obj_filename(config, self.source_file.path))

    @property
    def source_file(self) -> str:
        return self._source_file

    def iter_seqs(self):
        seqs_records = SeqIO.parse(open(self.source_file.path),
                                   self.source_file.file_format)
        for seq_rec in seqs_records:
            yield _transform(_validate(seq_rec.seq))
