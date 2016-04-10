library(plyr)

source('dm.R')
source('jackknife.R')

weighted.spearman.plot <- function(xx.dirname) {
    xx.full_filename <- sprintf("%s/seqs.txt", xx.dirname)
    xx.full <- dm.parse.file(xx.full_filename)
    xx.tables <- dm.parse.dir(xx.dirname)

    xx.relative.name <- tail(strsplit(xx.dirname, "/")[[1]], n=1)
    xx.names <- strsplit(xx.relative.name, "_")[[1]]
    xx.method <- xx.names[1]
    xx.k <- xx.names[2]

    wu.tables <- lapply(wu.tables, dm.reformat, wu.full)
    xx.tables <- lapply(xx.tables, dm.reformat, wu.full)

    xx.full <- dm.reformat(xx.full, wu.full)
    wu.full$X <- NULL

    rownames(wu.full) <- colnames(wu.full)
    rownames(xx.full) <- colnames(xx.full)

    #dm.compare.cor(xx.full, wu.full)

    xx.melted <- t(dm.melt.all(xx.tables))
    wu.melted <- t(dm.melt.all(wu.tables))
    wu.mean <- jk.mean(wu.tables)

    g <- dm.compare.against.mean(xx.melted, wu.melted, wu.mean)
    g <- g + ggtitle(sprintf("%s (k=%s)", xx.method, xx.k)) +
            theme(plot.title = element_text(lineheight=.8, face="bold"))
    g
}

weighted.compare <- function(basedir, distname) {
    wu.path <- sprintf("%s/w_unifrac", basedir)
    wu.full_filename <- sprintf("%s/wu_full.txt", wu.path)
    wu.full <- dm.parse.file(wu.full_filename)
    wu.tables <- dm.parse.dir(wu.path)

    # Select all dirs starts with a distance name
    dist.pattern <- sprintf("%s_*", distname)
    xx.dirs <- dir(basedir, pattern=dist.pattern, full.names=TRUE)

    plots <- llply(xx.dirs, weighted.spearman.plot)

    # Grouping plots
    groups <- matrix(plots, ncol=6, byrow=TRUE)
    apply(groups, 1, function(x) do.call(grid.arrange, c(x, ncol=2, nrow=3)))
}
