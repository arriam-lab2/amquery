"""
Application programming interface module
"""

import click


def default_setup(jobs):
    from amquery.utils.multiprocess import Pool
    Pool.instance(jobs=jobs)


def read_config():
    """
    Print a config file
    """
    import json
    from amquery.utils.config import CONFIG_PATH, read_config
    print(json.dumps(read_config(), indent=4, sort_keys=True))


def edit_config():
    from amquery.utils.config import CONFIG_PATH
    click.edit(filename=CONFIG_PATH)


def _get_databases_list(config):
    return [db for db in config["databases"]]


def list_databases():
    """
    List registered databases
    """
    from amquery.utils.config import read_config

    config = read_config()
    print("\n".join(x for x in _get_databases_list(config)))


def create_database(database_name, **kwargs):
    """
    Create a new database
    """
    
    from shutil import copyfile
    from amquery.core.index import Index
    import amquery.utils.config as amqconfig

    distance = kwargs.get("distance", "")
    rep_tree = kwargs.get("rep_tree", "")
    rep_set = kwargs.get("rep_set", "")
    biom_table = kwargs.get("biom_table", "")
    kmer_size = kwargs.get("kmer_size", "")

    config = amqconfig.create_database(database_name)
    
    database_config = config['databases'][database_name]
    database_config['distance'] = distance

    if rep_tree:
        database_config['rep_tree'] = str(rep_tree)
    if rep_set:
        database_config['rep_set'] = str(rep_set)
    if biom_table:
        database_config['biom_table'] = amqconfig.get_biom_path(database_name)
        copyfile(str(biom_table), amqconfig.get_biom_path(database_name))
    if kmer_size:
        database_config['kmer_size'] = str(kmer_size)

    amqconfig.save_config(config)

    index = Index.create(database_config)
    index.save(database_config)


def build_databases(input_files, **kwargs):
    """
    Build databases by indexing samples
    """
    from amquery.core.index import Index
    from amquery.utils.config import read_config

    config = read_config()

    database_name = kwargs.get("db", "")
    databases = [database_name] if database_name else _get_databases_list(config)

    for database_name in databases:
        database_config = config['databases'][database_name]

        index, _ = Index.load(database_name)
        index.build(input_files, database_name)
        index.save(database_config)


def add_samples(input_files, **kwargs):
    """
    Add samples to databases
    """
    from amquery.core.index import Index
    from amquery.utils.config import read_config, save_config

    config = read_config()

    database_name = kwargs.get("db", "")
    databases = [database_name] if database_name else _get_databases_list(config)

    biom_table = kwargs.get("biom_table", "")

    for database_name in databases:
        index, database_config = Index.load(database_name)
        if biom_table:
            database_config["biom_table"] = str(biom_table)

        index.add(input_files, database_config)
        index.save(database_config)

    save_config(config)


def stats(database_name):
    """
    Show a general information about databases
    """
    from amquery.core.index import Index

    index, database_config = Index.load(database_name)
    indexed = len(index)

    click.secho("Database: ", bold=True, nl=False)
    click.secho(database_name)
    click.secho("Indexed: ", bold=True, nl=False)
    click.secho("%s samples" % indexed)


def print_samples(sample_list):
    """
    Print list of samples
    """
    sample_names = sorted(sample.name for sample in sample_list)
    click.secho("Indexed", bold=True)
    for name in sample_names:
        click.secho("%s" % name, fg='blue')


def get_samples(database_name):
    """
    Get a list of indexed samples
    """
    from amquery.core.index import Index

    index, database_config = Index.load(database_name)
    return index.samples
    

def search(sample_name, k, **kwargs):
    """
    Nearest neighbors search against databases
    """
    from amquery.core.index import Index
    from amquery.utils.config import read_config

    config = read_config()
    database_name = kwargs.get("db", "")
    databases = [database_name] if database_name else _get_databases_list(config)

    results = []
    for database_name in databases:
        index, database_config = Index.load(database_name)

        values, points = index.search(sample_name, k, database_name)
        results.append({"database": database_name, 
                        "k": k,
                        "results": (values, points)})

    return results


def print_search_results(results, k, database_name):
    for search_result in results:
        database_name = search_result["database"]
        k = search_result["k"]
        values, points = search_result["results"]

        click.secho("{} nearest neighbors against {}:".format(str(k), str(database_name)), bold=True)
        click.secho('\t\t\t'.join(x for x in ['Sample', 'Distance']), bold=True)

        for value, sample_id in zip(values, points):
            tabs = 3 - int(len(sample_id) / 5 - 1)
            click.secho(("%s" + '\t' * tabs) % sample_id, fg='blue', nl=False)
            click.echo("%f\t" % value)

        click.echo()
