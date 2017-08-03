# Amquery
_(ver. 0.2.2)_

[![Build Status](https://semaphoreci.com/api/v1/nromashchenko/amquery/branches/develop/shields_badge.svg)](https://semaphoreci.com/nromashchenko/amquery)
[![Code Climate](https://codeclimate.com/github/nromashchenko/amquery/badges/gpa.svg)](https://codeclimate.com/github/nromashchenko/amquery)
[![Test Coverage](https://codeclimate.com/github/nromashchenko/amquery/badges/coverage.svg)](https://codeclimate.com/github/nromashchenko/amquery/coverage)

Amquery is a unified searchable database of amplicon libraries, designed for fast similarity search of 16S rRNA amplicon libraries against a large database. This tool allows users to compare hundreds of samples in a matter of minutes and to maintain databases with seamless and fast sample insertion and search.

*Note: this package is under development.*


## Setup
Clone this repo to some directory and run `pip install --process-dependency-links .` inside.

## Usage

###### Sample indexing
To index the samples from fasta-formatted INPUT_FILE, type following commands (**WARNING!** This step may take a long time):
```
mkdir index && cd index && amq init
amq build INPUT_FILE
```
Amquery will use a square root of Jensen-Shannon divergence over k-mer abundandcy distributions of sample reads by default. If you want to use weighted UniFrac instead, you must also provide proper OTU table and phylogenetic tree. Read ```amq init --help``` for further information.

###### Index statistics
Use the ```amq list``` to list all the indexed samples, and ```amq stats``` to view a short summary about the index.

###### Similarity search query
```
amq find -k NUMBER_OF_NEIGHORS SAMPLE_NAME
```

## License
This project is licensed under the terms of the [MIT](https://github.com/nromashchenko/amquery/blob/develop/LICENSE.txt) license.
