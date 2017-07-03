from biom import load_table
from biom.util import biom_open


def merge_biom_tables(master_fp, additional_fp):
    """
    :param master_fp: str
    :param additional_fp: str
    :return: None
    """
    master = load_table(master_fp)
    master = master.merge(load_table(additional_fp))

    with biom_open(master_fp, 'w') as biom_file:
        master.to_hdf5(biom_file, "amquery", True)
