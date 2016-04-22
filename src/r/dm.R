library(ggplot2)
library(gridExtra)
library(ade4)
library(corrplot)
library(reshape2)
library(lattice)
library(phytools)
library(car)

dm.parse.file <- function(filename) {
    #as.data.frame(read.table(filename, sep="\t", header=TRUE))
    as.data.frame(read.table(filename))
}

# parse files containing distance matrixies
dm.parse.dir <- function(directory) {
    dir_files = list.files(directory, pattern='*.txt', full.names=TRUE)
    lapply(dir_files, dm.parse.file)
}

# reorder rows and cols as in sample
dm.reformat <- function(dm, sample) {
    m <- match(colnames(sample), colnames(dm))
    dm[m,m]
}

# R-squared function
rsqured <- function(x, y) {
    tss = sum((y - mean(y))^2)
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

    print("Mean distance vs. R-squared correlation:")
    print(cor(df$R2, df$mean_dist))

    return(df)
}

dm.compare.cor <- function(x, y) {
    par(mfrow = c(1, 2))
    corrplot(cor(x, y), method="color")
    corrplot(cor(y, y), method="color")
    par(mfrow = c(1, 1))

    m <- mantel.rtest(as.dist(y), as.dist(x), nrepet=10000)
    print(m)

    mm <- multi.mantel(as.dist(y), as.dist(x), nperm=1000)
    p <- qqPlot(residuals(mm))
    print(p)
}

dm.melt.all <- function(xx.tables) {
    sapply(xx.tables, function (x) { as.vector(as.matrix(x)) })
}

dm.vectorize.all <- function(xx.tables) {
    res <- c()
    for (xt in xx.tables) {
        res <- c(res, as.vector(as.matrix(xt)))
    }
    res
}

# Spearman's correlation plot for all pairs (txx[i], tyy[j])
dm.compare.fullagainst <- function(txx, tyy) {
    corr.matrix <- cor(txx, tyy, method="spearman")
    corr.matrix[is.na(corr.matrix)] = 1
    corrplot(corr.matrix)
}

dm.compare.spearman2 <- function(xmean, ymean) {
    df <- melt(xmean)
    df$y <- melt(ymean)$value
    df$variable <- NULL
    df <- rename(df, c("value"="x"))

    sp <- cor(df$x, df$y, method="spearman")
    sp
}

# the dependence of Spearman's correlation on mean Unifrac distance
dm.compare.against.mean <- function(txx, tyy, yy.mean) {
    dist.cor <- suppressWarnings(sapply(1:dim(txx)[2],
        function(i) cor(txx[,i], tyy[,i], method="spearman")))

    df <- melt(yy.mean)
    df$dist.cor <- dist.cor

    # Omit NA values
    df <- df[complete.cases(df),]

    g <- ggplot(data=df, aes(x=value, y=dist.cor, color=variable)) +
        geom_point() +
        labs(color="Sample", x="Mean Unifrac distance", y="Spearman correlation coefficient")
    g
}
