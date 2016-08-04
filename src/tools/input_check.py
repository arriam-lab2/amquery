#!/usr/bin/env python3

import click
import os
from typing import Sequence, List
from enum import Enum

import lib.iof as iof


class FileFormat(Enum):
    fasta = 1
    fastq = 2
    unknown = 3


class UnknownFormatException(Exception):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return repr(self.filename)


class FilenameParser:
    @staticmethod
    def parse(filename: str) -> FileFormat:
        parser_mapping = {
            FileFormat.fasta: FilenameParser.__is_fasta,
            FileFormat.fastq: FilenameParser.__is_fastq,
        }

        for file_format, checker in parser_mapping.items():
            if checker(filename):
                return file_format

    @staticmethod
    def __is_fasta(filename: str) -> bool:
        if iof.is_empty(filename):
            return True

        with open(filename, 'r') as f:
            control_chars = ['>', '@', '+', '!']
            first_line = f.readline().strip()
            next_line = FilenameParser.__next_line(f, control_chars)

            if not next_line:
                return True
            else:
                return first_line[0] == next_line.strip()[0] == '>'

    @staticmethod
    def __is_fastq(filename: str) -> bool:
        if iof.is_empty(filename):
            return True

        with open(filename, 'r') as f:
            control_chars = ['>', '@', '+', '!']
            first_line = f.readline().strip()
            second_line = FilenameParser.__next_line(f, control_chars)
            third_line = FilenameParser.__next_line(f, control_chars)

            if (first_line and first_line[0] == '@' and
                second_line and second_line[0] == '+' and
                third_line and third_line[0] == '!'):
                return True

            return False

    @staticmethod
    def __next_line(f, control_chars: List[str]):
        line = f.readline()
        while line and line[0] not in control_chars:
            line = f.readline()

        return line


def check_file(filename: str):
    file_format = FilenameParser.parse(filename)

    if not file_format or file_format == FileFormat.unknown:
        raise UnknownFormatException(filename)

    extension = os.path.splitext(filename)[1]
    new_name = filename.replace(extension, '.' + file_format.name)
    if new_name != filename:
        print("Renaming", filename)
        os.rename(filename, new_name)


def check_directory(dirname: str):
    files = iof.all_files([dirname])
    for f in files:
        check_file(f)


@click.command()
@click.argument('input_dirs', type=click.Path(exists=True),
                nargs=-1, required=True)
def run(input_dirs: Sequence[str]):
    input_dirs = [iof.normalize(d) for d in input_dirs]
    for dirname in input_dirs:
        check_directory(dirname)


if __name__ == "__main__":
    run()
