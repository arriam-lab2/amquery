library(ggplot2)

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
}

dm.compare.r2 <- function(x, y) {
    # R-squared function
    r2 <- function(x, y) {
        tss = sum((x - mean(x[[1]]))^2)
        rss = sum((y - x)^2)
        return (1 - rss/tss)
    }

    df <- melt(mapply(r2, x, y))
    g <- ggplot(df, aes(x=factor(rownames(df)), y=value, group=1)) + geom_line()
    print(g)
    return(df)
}

dm.compare <- function(x, y) {
    #y <- dm.reformat(y, x)
    #x$X <- NULL
    dm.compare.cor2(x, y)
    dm.compare.r2(x, y)
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
    md$pp <- m$value > alpha | is.na(m$value)
    g <- ggplot(data = md, aes(x=Var1, y=Var2, fill=pp)) + geom_tile()
    print(g)
    g <- ggplot(data = md, aes(x=Var1, y=Var2, fill=value)) + geom_tile()
    print(g)
}


