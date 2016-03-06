
#filename = 'data/weighted_unifrac_otu_table.txt'
filename = 'data/unweighted_unifrac_otu_table.txt'
xtable <- read.table(filename, sep="\t", header=TRUE)
uu <- as.data.frame(xtable)

filename = 'j_matrix.txt'
xtable <- read.table(filename, sep="\t", header=TRUE)
ji <- as.data.frame(xtable)

# reorder rows and cols
m <- match(uu$X, ji$X)
ji$X <- NULL
uu$X <- NULL
ji <- ji[m,m]

# R-square matrix
cor_matrix <- round(cor(uu, ji)^2, 4)
library(reshape2)
mcor_matrix<- melt(cor_matrix)

# heat map
library(ggplot2)
ggplot(data = mcor_matrix, aes(x=Var1, y=Var2, fill=value)) + geom_tile()

#uu$X <- as.character(df$X)
#uu$type <- substr(df$X, 1, nchar(df$X) - 1)
#uu$type <- as.factor(df$type)
#uu$X <- NULL

#library(lattice)
#pairs(uu, col = uu$type)
