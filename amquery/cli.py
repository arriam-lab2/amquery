"""
Command line interface module
"""

import click
import amquery.api as api


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])



@click.group()
@click.option('--jobs', '-j', type=int, default=1, help='Number of jobs to start in parallel')
def cli(jobs):
    """
    Amquery
    """
    api.default_setup(jobs)


@cli.command()
@click.option("--edit", is_flag=True)
def config(edit):
    """
    Print or edit a config file
    """
    if edit:
        api.edit_config()
    else:
        api.read_config()


@cli.group()
def db():
    """
    Database-specific commands
    """
    pass


@db.command()
def list():
    """
    List registered databases
    """
    api.list_databases()


def _validate_distance(ctx, param, value):
    from amquery.core.distance import distances, DEFAULT_DISTANCE

    if value:
        try:
            distances[value]
            return value
        except KeyError:
            raise click.BadParameter('Distance must be one of {}'.format(", ".join(s for s in distances.keys())))
    else:
        return DEFAULT_DISTANCE

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
    
    api.create_database(name, 
                        distance=distance, rep_tree=rep_tree, rep_set=rep_set, 
                        biom_table=biom_table, kmer_size=kmer_size)


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
def build(db, input_files):
    """
    Build databases by indexing samples
    """
    api.build_databases(input_files, db=db)


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
@click.option("--biom_table", type=click.Path())
def add(db, input_files, biom_table):
    """
    Add samples to databases
    """
    api.add_samples(input_files, db=db)


@cli.command()
@click.argument('database_name', type=str, required=True)
def stats(database_name):
    """
    Show a general information about databases
    """
    api.stats(database_name)


@cli.command()
@click.argument('database_name', type=str, required=True)
def list(database_name):
    """
    Show a list of indexed samples
    """
    samples = api.get_samples(database_name)
    api.print_samples(samples)


@cli.command()
@click.option('--db', type=str, required=False)
@click.argument('sample_name', type=str, required=True)
@click.option('-k', type=int, required=True, default=5, help='Count of nearest neighbors')
def find(db, sample_name, k):
    """
    Nearest neighbors search against databases
    """
    results = api.search(sample_name, k, db=db)
    api.print_search_results(results, k, db)
