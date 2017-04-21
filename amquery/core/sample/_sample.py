import os
import numpy as np
import functools
import itertools
import operator as op
import joblib
from typing import Sequence, Any, List
from Bio import SeqIO
from functools import total_ordering
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


@total_ordering
class Sample:
    def __init__(self, source_file: str):
        self._source_file = SampleFile(source_file)
        self._name = self._parse_name()
        self._kmer_index = None

    def __eq__(self, other):
        return self.name.lower() == other.name.lower()

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def _parse_name(self):
        for record in SeqIO.parse(open(self.source_file.path),
                                  self.source_file.file_format):
            return str(record.id).split("_")[0]

    @property
    def name(self) -> str:
        return self._name

    def make_sample_obj_filename(self, config: Config, source_filename: str) -> str:
        return os.path.join(config.sample_dir, self.name)

    def make_kmer_index_obj_filename(self, config: Config, source_filename: str) -> str:
        return os.path.join(config.kmer_index_dir, self.name)
        
    @staticmethod
    def load(config: Config, object_file):
        sample = joblib.load(object_file)
        return sample

    def load_kmer_index(self, config: Config) -> None:
        self._kmer_index = joblib.load(self.make_kmer_index_obj_filename(config, self.source_file.path))

    @hide_field("_kmer_index")
    def _save(self, config: Config):
        self._kmer_index = None
        joblib.dump(self, self.make_sample_obj_filename(config, self.source_file.path))
    
    def save(self, config: Config) -> None:
        self._save(config)
        
        if self._kmer_index:
            joblib.dump(self._kmer_index, self.make_kmer_index_obj_filename(config, self.source_file.path))

    @property
    def source_file(self) -> str:
        return self._source_file

    def kmer_index(self, config):
        if not self._kmer_index:
            self.load_kmer_index(config)

        return self._kmer_index

    def set_kmer_index(self, index):
        self._kmer_index = index

    def iter_seqs(self):
        seqs_records = SeqIO.parse(open(self.source_file.path),
                                   self.source_file.file_format)
        for seq_rec in seqs_records:
            yield _transform(_validate(seq_rec.seq))
