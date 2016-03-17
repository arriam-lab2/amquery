library(ggplot2)
library(plyr)
library(gridExtra)
library(ade4)
library(corrplot)
library(ade4)

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

dm.compare.cor2 <- function(x, y) {
    # correlation matrix
    cor_matrix <- round(cor(x, y)^2, 4)
    library(reshape2)
    mcor_matrix <- melt(cor_matrix)

    # cor-squared heat map
    g <- ggplot(data = mcor_matrix, aes(x=Var1, y=Var2, fill=value)) + geom_tile()
    print(g)
    #return (g)
}

dm.compare.r2 <- function(x, y) {
    # R-squared function
    r2 <- function(x, y) {
        tss = sum((x - mean(x[[1]]))^2)
        rss = sum((y - x)^2)
        return (1 - rss/tss)
    }

    df <- melt(mapply(r2, x, y))
    df <- rename(df, c("value"="R2"))
    df$mean_dist <- sapply(x, mean)

    g <- ggplot(df, aes(x=factor(rownames(df)))) + 
        geom_line(aes(y=R2, colour = "R-squared", group=1)) + 
        geom_line(aes(y=mean_dist, colour = "mean Unifrac", group=1))

    print(g)

    print("Mean distance vs. R-squared corellation:")
    print(cor(df$R2, df$mean_dist))

    #return (g)
    return(df)
}

dm.compare <- function(x, y) {
    #y <- dm.reformat(y, x)
    #x$X <- NULL

    corrplot(cor(x, y), method="color")
    m <- mantel.rtest(as.dist(x), as.dist(y), nrepet=10000)
    print(m)

    g1 <- dm.compare.cor2(x, y)
    g2 <- dm.compare.r2(x, y)

    #grid.draw(rbind(ggplotGrob(g1), ggplotGrob(g2), size="last"))
    #grid.arrange(g1, g2, ncol=1)

}

dm.melt.all <- function(xx.tables) { 
    sapply(xx.tables, melt(x)$value)
}

dm.compare.all <- function(xx.tables, yy.tables) {
    xx.melted <- dm.melt.all(xx.tables)
    yy.melted <- dm.melt.all(yy.tables)

    corr.matrix <- cor(t(xx.melted), t(yy.melted))
    corrplot(corr.matrix)
}

