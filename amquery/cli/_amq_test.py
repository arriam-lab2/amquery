import click
import pandas as pd
import numpy as np
import random
from amquery.core.index import Index
from amquery.core.sample import Sample
from amquery.utils.multiprocess import Pool
from amquery.utils.split_fasta import split_fasta
from amquery.utils.config import get_sample_dir

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
@click.option('--force', '-f', is_flag=True, help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.option('--jobs', '-j', type=int, default=1, help='Number of jobs to start in parallel')
def cli(force, quiet, jobs):
    Pool.instance(jobs=jobs)


# load pairwise distance matrix from file
def load(input_filename: str):
    matrix = []
    with open(input_filename) as infile:
        labels = infile.readline()[:-1].split("\t")[1:]

        for line in infile.readlines():
            values = line[:-1].split("\t")[1:]
            matrix.append(values)

        matrix = [list(map(float, l)) for l in matrix]

    return pd.DataFrame(data=np.matrix(matrix), index=labels, columns=labels)


def precision_at_k(result, relevant, k):
    return np.sum([1.0 if x in relevant else 0.0 for x in result]) / k


def average_precision_at_k(result, relevant, k):
    return np.sum([(1.0 if result[m - 1] in relevant else 0.0) * precision_at_k(result[:m], relevant[:m], m)
                  for m in range(1, k + 1)]) / k


# normalized discounted cumulative gain at k
def ndcg_at_k(result, relevance_dict, k):
    dcg = np.sum([(2 ** (relevance_dict[result[m-1]] if result[m-1] in relevance_dict else 0.0) - 1) / np.log2(m + 1)
                  for m in range(1, k + 1)])
    return dcg / np.sum(1.0 / np.log2(m+1) for m in range(1, k + 1))


@cli.command()
@click.argument('input_file', type=click.Path(exists=True), required=True)
@click.option('--reference', '-r', type=click.Path(exists=True), required=True)
@click.option('-k', type=int, required=True, help='Count of nearest neighbors')
def precision(input_file, reference, k):
    reference_df = load(reference)
    index, config = Index.load()

    p_at_k, ap_at_k, gain_at_k = [], [], []
    bp_at_k, bap_at_k, bgain_at_k = [], [], []

    samples = [Sample(sample_file) for sample_file in split_fasta(input_file, get_sample_dir())]

    for sample in samples:
        values, best_by_amq = index.find(sample.name, k)
        best_by_reference = reference_df[sample.name].sort_values()
        baseline = random.sample(list(best_by_reference.index), k)
        reference_worst_result = best_by_reference[-1]
        relevance = [1 - x / reference_worst_result for x in best_by_reference]
        relevance_dict = dict(list(zip(best_by_reference.index, relevance)))

        best_by_reference = list(best_by_reference.index)[:k]
        p_at_k.append(precision_at_k(best_by_amq, best_by_reference, k))
        ap_at_k.append(average_precision_at_k(best_by_amq, best_by_reference, k))
        gain_at_k.append(ndcg_at_k(best_by_amq, relevance_dict, k))

        bp_at_k.append(precision_at_k(baseline, best_by_reference, k))
        bap_at_k.append(average_precision_at_k(baseline, best_by_reference, k))
        bgain_at_k.append(ndcg_at_k(baseline, relevance_dict, k))

        bp_at_k.append(precision_at_k(baseline, best_by_reference, k))
        bap_at_k.append(average_precision_at_k(baseline, best_by_reference, k))
        bgain_at_k.append(ndcg_at_k(baseline, relevance_dict, k))

    m = len(samples)
    print(np.sum(p_at_k) / m, np.sum(ap_at_k) / m, np.sum(gain_at_k) / m,
          np.sum(bp_at_k) / m, np.sum(bap_at_k) / m, np.sum(bgain_at_k) / m)



@cli.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
@click.option('--reference', '-r', type=click.Path(exists=True), required=True)
@click.option('-k', type=int, required=True, help='Count of nearest neighbors')
def minprecision(input_files, reference, k):
    reference_df = load(reference)
    index = Index.load()

    index_size = len(index.sample_map)

    result = []
    for input_file in input_files:
        values, points = index.find(input_file, index_size)
        best_by_amq = [s.name for s in points]
        sample = Sample(input_file)
        best_by_reference = reference_df[sample.name].sort_values()
        best_by_reference = list(best_by_reference.index)[:k]

        for i in range(index_size):
            if best_by_amq[i] in best_by_reference:
                best_by_reference.remove(best_by_amq[i])

            if not best_by_reference:
                break

        result.append(i + 1)

    #print(np.sum(result) / len(input_files))
    print("\n".join(str(x) for x in result))
