library(ggplot2)
library(gridExtra)
library(ade4)
library(corrplot)
library(reshape2)
library(lattice)
library(phytools)


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
    par(mfrow = c(1, 2))
    corrplot(cor(x, y), method="color")
    corrplot(cor(y, y), method="color")
    par(mfrow = c(1, 1))

    m <- mantel.rtest(as.dist(y), as.dist(x), nrepet=10000)
    print(m)

    mm <- multi.mantel(as.dist(y), as.dist(x), nperm=1000)
    #print(mm)
    p <- xyplot(residuals(mm) ~ fitted(mm))
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

dm.compare.lm <- function(xx.tables, yy.tables) {
    x <- dm.vectorize.all(xx.tables) 
    y <- dm.vectorize.all(yy.tables) 

    df <- data.frame(y, x)
    l <- lm(data=df, y ~ poly(x, degree=2))
    print(summary(l))

    res <- residuals(l)
    stest <- shapiro.test(unique(res))
    print(stest)

    p1 <- xyplot(residuals(l) ~ fitted(l))
    print(p1)
    p2 <- qplot(residuals(l))
    print(p2)
    #grid.arrange(p1, p2, ncol=2)
}

dm.compare.all <- function(xx.tables, yy.tables) {
    xx.melted <- dm.melt.all(xx.tables)
    yy.melted <- dm.melt.all(yy.tables)

    corr.matrix <- cor(t(yy.melted), t(xx.melted))
    corr.matrix[is.na(corr.matrix)] = 1
    corrplot(corr.matrix)
}

