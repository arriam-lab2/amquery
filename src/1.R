
#filename = 'data/weighted_unifrac_otu_table.txt'
filename = 'data/unweighted_unifrac_otu_table.txt'
xtable <- read.table(filename, sep="\t", header=TRUE)
uu <- as.data.frame(xtable)

filename = 'jaccard_matrix.txt'
#filename = 'jsd_matrix.txt'
xtable <- read.table(filename, sep="\t", header=TRUE)
ji <- as.data.frame(xtable)

# reorder rows and cols
m <- match(uu$X, ji$X)
ji$X <- NULL
uu$X <- NULL
ji <- ji[m,m]

# correlation matrix
cor_matrix <- round(cor(uu, ji)^2, 4)
library(reshape2)
mcor_matrix<- melt(cor_matrix)

# heat map
library(ggplot2)
ggplot(data = mcor_matrix, aes(x=Var1, y=Var2, fill=value)) + geom_tile()

# R-squared function
r2 <- function(x, y) {
    tss = sum((x - mean(x[[1]]))^2)
    rss = sum((y - x)^2)
    return (1 - rss/tss)
}

df <- melt(mapply(r2, uu, ji))
print(df)
ggplot(df, aes(x=seq(1, dim(df)[1]), y=value)) + geom_line()

