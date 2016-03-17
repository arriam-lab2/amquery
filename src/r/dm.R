#library(ggplot2)
#library(plyr)
library(ade4)
library(corrplot)
library(reshape2)

dm.parse.file <- function(filename) {
    #as.data.frame(read.table(filename, sep="\t", header=TRUE))
    as.data.frame(read.table(filename))
}

# parse files containing distance matrixies
dm.parse.dir <- function(directory) {
    dir_files = list.files(directory, pattern='*.txt', full.names=TRUE)
    #l <- lapply(dir_files, read.table, sep="\t", header=TRUE)
    lapply(dir_files, dm.parse.file)
}


# reorder rows and cols as in sample
dm.reformat <- function(dm, sample) {
    m <- match(colnames(sample), colnames(dm))
    dm[m,m]
}

# R-squared function
rsqured <- function(x, y) {
    tss = sum((x - mean(x[[1]]))^2)
    rss = sum((y - x)^2)
    return (1 - rss/tss)
}

dm.compare.r2 <- function(x, y) {
    df <- melt(mapply(r2, x, y))
    df <- rename(df, c("value"="R2"))
    df$mean_dist <- sapply(x, mean)

    g <- ggplot(df, aes(x=factor(rownames(df)))) + 
        geom_line(aes(y=R2, colour = "R-squared", group=1)) + 
        geom_line(aes(y=mean_dist, colour = "mean Unifrac", group=1))

    print(g)

    print("Mean distance vs. R-squared corellation:")
    print(cor(df$R2, df$mean_dist))

    return(df)
}

dm.compare.cor <- function(x, y) {
    corrplot(cor(x, y), method="color")
    m <- mantel.rtest(as.dist(x), as.dist(y), nrepet=10000)
    print(m)

}

dm.melt.all <- function(xx.tables) { 
    as.vector(as.matrix(xx.tables))
}

dm.compare.all <- function(xx.tables, yy.tables) {
    xx.melted <- sapply(xx.tables, dm.melt.all)
    yy.melted <- sapply(yy.tables, dm.melt.all)

    corr.matrix <- cor(t(xx.melted), t(yy.melted))
    corr.matrix[is.na(corr.matrix)] = 1
    corrplot(corr.matrix)
}

