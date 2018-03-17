import os
import json


AMQ_STORAGE_DIR = os.path.join(os.path.expanduser("~"), ".amq/")
CONFIG_PATH = os.path.join(AMQ_STORAGE_DIR, "config.json")
DATABASES_DIR = os.path.join(AMQ_STORAGE_DIR, "databases")


def _create_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

    return os.path.join(path, '')


def _get_database_dir(database_name):
    database_dir = os.path.join(DATABASES_DIR, database_name)
    _create_if_not_exists(database_dir)
    return database_dir


def _get_default_config():
    """
    Return default values for a global config
    """
    config = {
        "databases": {},
    }
    return config


def create_default_config():
    """
    Create a default global config
    """
    _create_if_not_exists(AMQ_STORAGE_DIR)
    _create_if_not_exists(DATABASES_DIR)

    config = _get_default_config()
    save_config(config)
    return config


def _read_config():
    """
    Read a global config, do not check if it exists
    """
    with open(CONFIG_PATH, 'r') as config_file:
        return json.load(config_file)


def _get_global_config():
    """
    Check if global config exists, and create if not
    """
    _create_if_not_exists(AMQ_STORAGE_DIR)

    if os.path.exists(CONFIG_PATH):
        return _read_config()
    else:
        return create_default_config()


def create_database(database_name):
    """
    Create a record for a new database
    """

    config = _get_global_config()
    config["databases"][database_name] = get_default_database_config(database_name)
    database_dir = os.path.join(AMQ_STORAGE_DIR, database_name)
    _create_if_not_exists(database_dir)
    return config


def read_config():
    """
    Read a global config (existing or default)
    """
    return _get_global_config()


def save_config(config):
    """
    Save an edited config to the file
    """
    with open(CONFIG_PATH, 'w') as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True)


def get_default_database_config(database_name):
    """
    Default values for a record of a new database
    """

    config = {
        "name": database_name,
        "distance": {},
        "index": {},
        "misc": {},
    }
    return config


def get_distance_path(database_name):
    database_dir = _get_database_dir(database_name)
    return os.path.join(database_dir, 'distance.txt')


def get_storage_path(database_name):
    database_dir = _get_database_dir(database_name)
    return os.path.join(database_dir, 'storage.json')


def get_kmers_dir(database_name):
    database_dir = _get_database_dir(database_name)
    return os.path.join(database_dir, 'kmers')


def get_biom_path(database_name):
    database_dir = _get_database_dir(database_name)
    return os.path.join(database_dir, 'otu_table.biom')


def get_sample_dir(database_name):
    database_dir = _get_database_dir(database_name)
    return os.path.join(database_dir, 'samples')


def get_samplemap_path(database_name):
    database_dir = _get_database_dir(database_name)
    return os.path.join(database_dir, 'sample_map.json')

