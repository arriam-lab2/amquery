import os
import configparser


def get_default_config():
    config = configparser.ConfigParser()
    config.add_section('config')
    config.add_section('distance')
    config.add_section('index')
    config.add_section('additional')
    return config

def get_index_path():
    return os.path.join(os.getcwd(), '.amq')


def get_config_path():
    return os.path.join(get_index_path(), 'config')


def get_distance_path():
    return os.path.join(get_index_path(), 'distance.txt')


def get_storage_path():
    return os.path.join(get_index_path(), 'storage.json')


def get_kmers_dir():
    return os.path.join(get_index_path(), 'kmers')


def get_biom_path():
    return os.path.join(get_index_path(), 'otu_table.biom')


def get_sample_dir():
    return os.path.join(get_index_path(), 'samples')


def get_samplemap_path():
    return os.path.join(get_index_path(), 'sample_map.json')


def read_config():
    config = configparser.ConfigParser()
    config.read(get_config_path())
    return config


def save_config(config):
    with open(config.get('config', 'path'), 'w') as f:
        config.write(f)
