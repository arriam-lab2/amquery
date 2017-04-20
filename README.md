# AmQuery
_(ver. 0.2.2)_

[![Build Status](https://semaphoreci.com/api/v1/nromashchenko/amquery/branches/develop/shields_badge.svg)](https://semaphoreci.com/nromashchenko/amquery)
[![Code Climate](https://codeclimate.com/github/nromashchenko/amquery/badges/gpa.svg)](https://codeclimate.com/github/nromashchenko/amquery)
[![Test Coverage](https://codeclimate.com/github/nromashchenko/amquery/badges/coverage.svg)](https://codeclimate.com/github/nromashchenko/amquery/coverage)

AmQuery is a unified searchable database of amplicon libraries, designed for fast similarity search of 16S rRNA amplicon libraries against a large database.

*Note: this package is under development.*

AmQuery is a tool that allows users to compare hundreds of samples in a matter of minutes and to maintain databases with seamless and fast sample insertion and instant search. It is heavily optimized for large datasets and was developed to match weighted UniFrac results without having to pay the price of OTU-picking and tree-construction.


## Setup
Clone this repo to some directory and run `pip install .` inside.

## Usage

###### Building an index

**WARNING!** This step may take a long time.

```
amq init index
amq build <your-data-path>/*.fasta
amq stats
```
Note that any input file must contain only sequences from single sample.

###### Similarity search query
```
amq find -k <number-of-neighbors> <your-sample-file-path>
```

## License
This project is licensed under the terms of the [MIT](https://github.com/nromashchenko/amquery/blob/develop/LICENSE.txt) license.
