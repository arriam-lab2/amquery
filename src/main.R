
dm.parse.file <- function(filename) {
    as.data.frame(read.table(filename, sep="\t", header=TRUE))
}

# parse files containing distance matrixies
dm.parse.dir <- function(directory) {
    dir_files = list.files(directory, pattern='*.txt', full.names=TRUE)
    #l <- lapply(dir_files, read.table, sep="\t", header=TRUE)
    lapply(dir_files, dm.parse.file)
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
    #y <- dm.reformat(y, x)
    x$X <- NULL
    #dm.compare.cor2(x, y)
    dm.compare.r2(x, y)
}

#filename = 'data/weighted_unifrac_otu_table.txt'
uu_full_filename = 'data/unweighted_unifrac_otu_table.txt'
uf <- dm.parse.file(uu_full_filename)

uu_path = 'data/out3/unweighted_unifrac/rare_dm/'
uu_tables <- dm.parse.dir(uu_path)

ji_full_filename = 'jaccard_matrix.txt'
ji <- dm.parse.file(ji_full_filename)

#jsd_full_filename = 'jsd_matrix.txt'

uu_tables <- lapply(uu_tables, dm.reformat, uf)
ji <- dm.reformat(ji, uf)
uf$X <- NULL

N <- length(uu_tables)

source('jackknife.R')
round(jk.pseudomean(uu_tables, uf, N), 4)
round(jk.pseudovar(uu_tables, uf, N), 4)






#uu <- uu_tables[[1]]
#lapply(uu_tables, dm.compare, ji)
#dm.compare(uu, ji)

