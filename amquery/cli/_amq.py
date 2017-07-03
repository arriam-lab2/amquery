import click
import os
import amquery.utils.iof as iof
from amquery.utils.config import get_default_config
from amquery.utils.multiprocess import Pool
from amquery.utils.config import read_config
from amquery.core.distance import distances, DEFAULT_DISTANCE
from amquery.core import Index


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
@click.option('--force', '-f', is_flag=True, help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.option('--jobs', '-j', type=int, default=1, help='Number of jobs to start in parallel')
def cli(force, quiet, jobs):
    Pool.instance(jobs=jobs)


@cli.command()
@click.option("--method", type=click.Choice(distances.keys()), default=DEFAULT_DISTANCE)
@click.option("--rep_tree", type=click.Path())
@click.option("--rep_set", type=click.Path())
@click.option("--biom_table", type=click.Path())
@click.option("--kmer_size", "-k", type=int, default=15)
def init(method, rep_tree, rep_set, biom_table, kmer_size):
    index_dir = os.path.join(os.getcwd(), '.amq')
    iof.make_sure_exists(index_dir)
    index_path = os.path.join(index_dir, 'config')

    config = get_default_config()
    config.set('config', 'path', index_path)
    config.set('distance', 'method', method)

    if rep_tree:
        config.set('distance', 'rep_tree', str(rep_tree))
    if rep_set:
        config.set('distance', 'rep_set', str(rep_set))
    if biom_table:
        config.set('distance', 'biom_table', str(biom_table))
    if kmer_size:
        config.set('distance', 'kmer_size', str(kmer_size))

    with open(config.get('config', 'path'), 'w') as f:
        config.write(f)

    index = Index.init()
    index.save()


@cli.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
def build(input_files):
    index = Index.load()
    index.build(input_files)
    index.save()


@cli.command()
@click.option('--kmer_size', '-k', type=int, help='K-mer size', default=15)
@click.option('--distance', '-d', type=click.Choice(distances.keys()), default='jsd', help='A distance metric')
def refine(kmer_size, distance):
    raise NotImplementedError


@cli.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
@click.option("--biom_table", type=click.Path())
def add(input_files, biom_table):
    config = read_config()

    if biom_table:
        config.set('additional', 'biom_table', str(biom_table))

    index = Index.load()
    index.add(input_files)
    index.save()


@cli.command()
def stats():
    index = Index.load()
    indexed = len(index)

    click.secho("Indexed: ", bold=True, nl=False)
    click.secho("%s samples" % indexed)


@cli.command()
def ls():
    index = Index.load()

    click.secho("Indexed", bold=True)
    sample_names = sorted(list(sample.name for sample in index.samples))
    for name in sample_names:
        click.secho("%s" % name, fg='blue')


@cli.command()
@click.argument('sample_name', type=str, required=True)
@click.option('-k', type=int, required=True, help='Count of nearest neighbors')
def find(sample_name, k):
    index = Index.load()
    values, points = index.find(sample_name, k)
    click.secho("%s nearest neighbors:" % k, bold=True)
    click.secho('\t'.join(x for x in ['Sample', 'Similarity']), bold=True)

    for value, sample_id in zip(values, points):
        click.secho("%s\t" % sample_id, fg='blue', nl=False)
        click.echo("\t%f\t" % value)
