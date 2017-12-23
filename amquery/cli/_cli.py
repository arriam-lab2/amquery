import click
import json
from shutil import copyfile
from amquery.core import Index
from amquery.core.distance import distances, DEFAULT_DISTANCE
from amquery.utils.multiprocess import Pool
from amquery.utils.config import CONFIG_PATH, read_config, save_config, \
                                 create_database, get_biom_path


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
@click.option('--force', '-f', is_flag=True, help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.option('--jobs', '-j', type=int, default=1, help='Number of jobs to start in parallel')
def cli(force, quiet, jobs):
    Pool.instance(jobs=jobs)


@cli.command()
@click.option("--edit", is_flag=True)
def config(edit):
    if edit:
        click.edit(filename=CONFIG_PATH)
    else:
        print(json.dumps(read_config(), indent=4, sort_keys=True))


@cli.group()
def db():
    pass


def _get_databases_list(config):
    return [db for db in config["databases"]]


@db.command()
def list():
    """
    List registered databases
    """
    config = read_config()
    print("\n".join(x for x in _get_databases_list(config)))


@db.command()
@click.argument('name', type=str, required=True)
@click.option("--distance", type=click.Choice(distances.keys()), default=DEFAULT_DISTANCE)
@click.option("--rep_tree", type=click.Path())
@click.option("--rep_set", type=click.Path())
@click.option("--biom_table", type=click.Path())
@click.option("--kmer_size", "-k", type=int, default=15)
def create(name, distance, rep_tree, rep_set, biom_table, kmer_size):
    """
    Create new database
    """

    config = create_database(name)
    database_config = config["databases"][name]
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
    config = read_config()
    databases = [db] if db else _get_databases_list(config)

    for database_name in databases:
        index, database_config = Index.load(database_name)
        index.build(database_config, input_files)
        index.save()


@cli.command()
@click.option('--kmer_size', '-k', type=int, help='K-mer size', default=15)
@click.option('--distance', '-d', type=click.Choice(distances.keys()), default='jsd', help='A distance metric')
def refine(kmer_size, distance):
    raise NotImplementedError


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
@click.option("--biom_table", type=click.Path())
def add(db, input_files, biom_table):
    """
    Add samples to databases
    """
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

    index, database_config = Index.load(database_name)
    indexed = len(index)

    click.secho("Database: ", bold=True, nl=False)
    click.secho(database_name)
    click.secho("Indexed: ", bold=True, nl=False)
    click.secho("%s samples" % indexed)


@cli.command()
@click.argument('database_name', type=str, required=True)
def ls(database_name):
    """
    Show a list of indexed samples
    """
    index, database_config = Index.load(database_name)

    click.secho("Indexed", bold=True)
    sample_names = sorted(sample.name for sample in index.samples)
    for name in sample_names:
        click.secho("%s" % name, fg='blue')


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('sample_name', type=str, required=True)
@click.option('-k', type=int, required=True, help='Count of nearest neighbors')
def find(db, sample_name, k):
    """
    Nearest neighbors search against databases
    """
    config = read_config()
    databases = [db] if db else _get_databases_list(config)

    for database_name in databases:
        index, database_config = Index.load(database_name)

        values, points = index.find(sample_name, k)
        click.secho("{} nearest neighbors against {}:".format(str(k), str(database_name)), bold=True)
        click.secho('\t\t\t'.join(x for x in ['Sample', 'Distance']), bold=True)

        for value, sample_id in zip(values, points):
            tabs = 3 - int(len(sample_id) / 6 - 1)
            click.secho(("%s" + '\t' * tabs) % sample_id, fg='blue', nl=False)
            click.echo("%f\t" % value)

        click.echo()
