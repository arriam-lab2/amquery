"""
API usage example
"""


import amquery.api as amq


if __name__ == "__main__":

    input_file = "data/10.fasta"
    additional_sample = "data/250/115.fasta"
    database_name1 = "test1"
    database_name2 = "test2"

    amq.create_database(database_name1, distance="ffp-jsd", kmer_size=15)
    amq.create_database(database_name2, distance="ffp-jsd", kmer_size=15)

    amq.build_databases([input_file])
    amq.add_samples([additional_sample], db=database_name1)

    amq.stats(database_name1)
    amq.stats(database_name2)

    samples = amq.get_samples(database_name1)
    amq.print_samples(samples)

    k = 5
    results = amq.search(additional_sample, k, db=database_name1)
    amq.print_search_results(results, k, database_name1)

    results = amq.search(additional_sample, k, db=database_name2)
    amq.print_search_results(results, k, database_name1)


