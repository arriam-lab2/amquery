
filename = 'jaccard_matrix.txt'
#filename = 'jsd_matrix.txt'
xtable <- read.table(filename, sep="\t", header=TRUE)
ji <- as.data.frame(xtable)


# parse files containing distance matrixies
dm.parse <- function(directory) {
    dir_files = list.files(directory, pattern='*.txt', full.names=TRUE)
    l <- lapply(dir_files, read.table, sep="\t", header=TRUE)
    lapply(l, as.data.frame)
}

# reorder rows and cols as in sample
dm.reformat <- function(dm, sample) {
    m <- match(sample$X, dm$X)
    dm$X <- NULL
    dm[m,m]
}

dm.compare.cor2 <- function(x, y) {
    # correlation matrix
    cor_matrix <- round(cor(x, y)^2, 4)
    library(reshape2)
    mcor_matrix <- melt(cor_matrix)

    # cor-squared heat map
    library(ggplot2)
    ggplot(data = mcor_matrix, aes(x=Var1, y=Var2, fill=value)) + geom_tile()
}

dm.compare.r2 <- function(x, y) {
    # R-squared function
    r2 <- function(x, y) {
        tss = sum((x - mean(x[[1]]))^2)
        rss = sum((y - x)^2)
        return (1 - rss/tss)
    }

    df <- melt(mapply(r2, x, y))
    #ggplot(df, aes(x=seq(1, dim(df)[1]), y=value)) + geom_line()
}

dm.compare <- function(x, y) {
    y <- dm.reformat(y, x)
    x$X <- NULL
    dm.compare.cor2(x, y)
    dm.compare.r2(x, y)
}

#filename = 'data/weighted_unifrac_otu_table.txt'
filename = 'data/unweighted_unifrac_otu_table.txt'
uu_path = 'data/out2/unweighted_unifrac/rare_dm/'

uu_tables <- dm.parse(uu_path)
uu <- uu_tables[[1]]
lapply(uu_tables, dm.compare, ji)
#dm.compare(uu, ji)

