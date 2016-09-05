import os
from Bio import SeqIO


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


class Sample:
    def __init__(self,
                 source_file: str):

        self._name = os.path.splitext(os.path.basename(source_file))[0]
        self._source_file = SampleFile(source_file)
        self.kmer_index = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_file(self) -> str:
        return self._source_file

    def sequences(self) -> str:
        seqs_records = SeqIO.parse(open(self.source_file.path),
                                   self.source_file.file_format)
        for seq_record in seqs_records:
            yield str(seq_record.seq)
