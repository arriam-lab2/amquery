library(plyr)

source('dm.R')
source('jackknife.R')

unweighted.spearman.plot <- function(xx.dirname) {
    xx.full_filename <- sprintf("%s/seqs.txt", xx.dirname)
    xx.full <- dm.parse.file(xx.full_filename)
    xx.tables <- dm.parse.dir(xx.dirname)

    xx.relative.name <- tail(strsplit(xx.dirname, "/")[[1]], n=1)
    xx.names <- strsplit(xx.relative.name, "_")[[1]]
    xx.method <- xx.names[1]
    xx.k <- xx.names[2]

    uu.tables <- lapply(uu.tables, dm.reformat, uu.full)
    xx.tables <- lapply(xx.tables, dm.reformat, uu.full)

    xx.full <- dm.reformat(xx.full, uu.full)
    uu.full$X <- NULL

    rownames(uu.full) <- colnames(uu.full)
    rownames(xx.full) <- colnames(xx.full)

    #dm.compare.cor(xx.full, uu.full)

    xx.melted <- t(dm.melt.all(xx.tables))
    uu.melted <- t(dm.melt.all(uu.tables))
    uu.mean <- jk.mean(uu.tables)

    g <- dm.compare.against.mean(xx.melted, uu.melted, uu.mean)
    g <- g + ggtitle(sprintf("%s (k=%s)", xx.method, xx.k)) +
            theme(plot.title = element_text(lineheight=.8, face="bold"))
    g
}

unweighted.compare <- function(basedir, distname) {
    uu.path <- sprintf("%s/un_unifrac", basedir)
    uu.full_filename <- sprintf("%s/uu_full.txt", uu.path)
    uu.full <- dm.parse.file(uu.full_filename)
    uu.tables <- dm.parse.dir(uu.path)

    # Select all dirs starts with a distance name
    dist.pattern <- sprintf("%s_*", distname)
    xx.dirs <- dir(basedir, pattern=dist.pattern, full.names=TRUE)

    plots <- llply(xx.dirs, unweighted.spearman.plot)

    # Grouping plots
    groups <- matrix(plots, ncol=6, byrow=TRUE)
    apply(groups, 1, function(x) do.call(grid.arrange, c(x, ncol=2, nrow=3)))
}
