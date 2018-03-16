"""
Command line interface module
"""

import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
@click.option('--jobs', '-j', type=int, default=1, help='Number of jobs to start in parallel')
def cli(jobs):
    """
    Amquery
    """

    from api.utils.multiprocess import Pool
    Pool.instance(jobs=jobs)


@cli.command()
@click.option("--edit", is_flag=True)
def config(edit):
    """
    Print or edit a config file
    """
    import json
    from api.utils.config import CONFIG_PATH, read_config

    if edit:
        click.edit(filename=CONFIG_PATH)
    else:
        print(json.dumps(read_config(), indent=4, sort_keys=True))


@cli.group()
def db():
    """
    Database-specific commands
    """
    pass


def _get_databases_list(config):
    return [db for db in config["databases"]]


@db.command()
def list():
    """
    List registered databases
    """
    from api.utils.config import read_config

    config = read_config()
    print("\n".join(x for x in _get_databases_list(config)))


def _validate_distance(ctx, param, value):
    from api.core.distance import distances, DEFAULT_DISTANCE

    try:
        return distances[value] if value else DEFAULT_DISTANCE
    except ValueError:
        raise click.BadParameter('Distance must be one of {}'.format(",".join(s for s in distances.keys)))

@db.command()
@click.argument('name', type=str, required=True)
@click.option("--distance", callback=_validate_distance, default="")
@click.option("--rep_tree", type=click.Path())
@click.option("--rep_set", type=click.Path())
@click.option("--biom_table", type=click.Path())
@click.option("--kmer_size", "-k", type=int, default=15)
def create(name, distance, rep_tree, rep_set, biom_table, kmer_size):
    """
    Create a new database
    """
    
    from shutil import copyfile
    from api.core import Index
    from api.utils.config import save_config, create_database, get_biom_path

    config = create_database(name)
    database_config = config['databases'][name]
    database_config['distance'] = distance

    if rep_tree:
        database_config['rep_tree'] = str(rep_tree)
    if rep_set:
        database_config['rep_set'] = str(rep_set)
    if biom_table:
        database_config['biom_table'] = get_biom_path()
        copyfile(str(biom_table), get_biom_path())
    if kmer_size:
        database_config['kmer_size'] = str(kmer_size)

    save_config(config)

    index = Index.create(database_config)
    index.save()


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
def build(db, input_files):
    """
    Build databases by indexing samples
    """
    from api.core import Index
    from api.utils.config import read_config

    config = read_config()
    databases = [db] if db else _get_databases_list(config)

    for database_name in databases:
        index, _ = Index.load(database_name)
        index.build(input_files)
        index.save()


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
@click.option("--biom_table", type=click.Path())
def add(db, input_files, biom_table):
    """
    Add samples to databases
    """
    from api.core import Index
    from api.utils.config import read_config, save_config

    config = read_config()
    databases = [db] if db else _get_databases_list(config)

    for database_name in databases:
        index, database_config = Index.load(database_name)
        if biom_table:
            database_config['biom_table'] = str(biom_table)
            index.add(database_config, input_files)
            index.save()

    save_config(config)


@cli.command()
@click.argument('database_name', type=str, required=True)
def stats(database_name):
    """
    Show a general information about databases
    """
    from api.core import Index

    index, database_config = Index.load(database_name)
    indexed = len(index)

    click.secho("Database: ", bold=True, nl=False)
    click.secho(database_name)
    click.secho("Indexed: ", bold=True, nl=False)
    click.secho("%s samples" % indexed)


@cli.command()
@click.argument('database_name', type=str, required=True)
def list(database_name):
    """
    Show a list of indexed samples
    """
    from api.core import Index

    index, database_config = Index.load(database_name)

    click.secho("Indexed", bold=True)
    sample_names = sorted(sample.name for sample in index.samples)
    for name in sample_names:
        click.secho("%s" % name, fg='blue')


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('sample_name', type=str, required=True)
@click.option('-k', type=int, required=True, default=5, help='Count of nearest neighbors')
def find(db, sample_name, k):
    """
    Nearest neighbors search against databases
    """
    from api.core import Index
    from api.utils.config import read_config

    config = read_config()
    databases = [db] if db else _get_databases_list(config)

    for database_name in databases:
        index, database_config = Index.load(database_name)

        values, points = index.find(sample_name, k)
        click.secho("{} nearest neighbors against {}:".format(str(k), str(database_name)), bold=True)
        click.secho('\t\t\t'.join(x for x in ['Sample', 'Distance']), bold=True)

        for value, sample_id in zip(values, points):
            tabs = 3 - int(len(sample_id) / 5 - 1)
            click.secho(("%s" + '\t' * tabs) % sample_id, fg='blue', nl=False)
            click.echo("%f\t" % value)

        click.echo()
