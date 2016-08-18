import os

class Sample:
    def __init__(self,
                 sample_name: str,
                 sample_file: str,
                 kmer_counter_path: str):

        self.sample_name = sample_name
        self.sample_file = sample_file
        self.kmer_counter_path = kmer_counter_path


def get_sample_name(input_file: str):
    shortname = os.path.split(input_file)[1]
    sample_name, _ = os.path.splitext(shortname)
    return sample_name
