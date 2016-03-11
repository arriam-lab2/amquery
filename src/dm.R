library(ggplot2)
library(plyr)
library(gridExtra)

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
    g1 <- dm.compare.cor2(x, y)
    g2 <- dm.compare.r2(x, y)
    #grid.draw(rbind(ggplotGrob(g1), ggplotGrob(g2), size="last"))
    #grid.arrange(g1, g2, ncol=1)

}

dm.get <- function(x, i, j) { x[[i]][[j]] }

dm.compare.ci <- function(x, y, zfull) {
    tx <- dim(zfull)[2]
    ty <- dim(zfull)[1]

    ci <- 0.95
    alpha <- 0.05
    res <- c()
    
    for (i in 1:tx) {
        for (j in 1:ty) {
            xi <- sapply(x, dm.get, i, j)
            yi <- sapply(y, dm.get, i, j)
            pvalue <- round(t.test(xi, yi, conf.level=ci, var.equal=TRUE)$p.value, 4)
            res <- c(pvalue, res)
        }
    }

    resmat <- matrix(res, ncol=tx, nrow=ty)
    rownames(resmat) <- names(zfull)
    colnames(resmat) <- names(zfull)
    print(resmat)

    md <- melt(resmat)
    md$pp <- md$value > alpha | is.na(md$value)
    g <- ggplot(data = md, aes(x=Var1, y=Var2, fill=pp)) + geom_tile()
    print(g)
    g <- ggplot(data = md, aes(x=Var1, y=Var2, fill=value)) + geom_tile()
    print(g)
}


