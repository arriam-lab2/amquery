
# unweighted unifrac distance table
#uu <- read.table('data/unweighted_unifrac_otu_table.txt', sep="\t", header=TRUE)
#print(uu)

#'data/weighted_unifrac_otu_table.txt'
filename = 'j_matrix.txt'
xtable <- read.table(filename, sep="\t", header=TRUE)
df <- as.data.frame(xtable)

df$X <- as.character(df$X)
df$type <- substr(df$X, 1, nchar(df$X) - 1)
df$type <- as.factor(df$type)
df$X <- NULL

library(lattice)
splom(df, col = df$type)
