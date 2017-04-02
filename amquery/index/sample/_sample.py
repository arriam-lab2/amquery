import os
from Bio import SeqIO

import functools
import itertools
import operator as op
from typing import Sequence, Any, List
import numpy as np


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


@functools.total_ordering
class Sample:
    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __init__(self, source_file: str):
        self._name = os.path.splitext(os.path.basename(source_file))[0]
        self._source_file = SampleFile(source_file)
        self.kmer_index = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_file(self) -> str:
        return self._source_file

    def iter_seqs(self):
        seqs_records = SeqIO.parse(open(self.source_file.path),
                                   self.source_file.file_format)
        for seq_rec in seqs_records:
            yield _transform(_validate(seq_rec.seq))
