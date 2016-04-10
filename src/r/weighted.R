source('dm.R')

wu.full_filename <- '../../data/mikkele/full/wu_full.txt'
wu.full <- dm.parse.file(wu.full_filename)
wu.path <- '../../out/w_unifrac'
wu.tables <- dm.parse.dir(wu.path)

weighted.compare.dir <- function(xx.dirname) {
    xx.full_filename <- sprintf("%s/seqs.txt", xx.dirname)
    xx.full <- dm.parse.file(xx.full_filename)
    xx.tables <- dm.parse.dir(xx.dirname)

    wu.tables <- lapply(wu.tables, dm.reformat, wu.full)
    xx.tables <- lapply(xx.tables, dm.reformat, wu.full)

    xx.full <- dm.reformat(xx.full, wu.full)
    wu.full$X <- NULL

    rownames(wu.full) <- colnames(wu.full)
    rownames(xx.full) <- colnames(xx.full)

    #dm.compare.cor(jsd.full, wu.full)
    dm.compare.all(wu.tables, xx.tables)
}

weighted.compare <- function(basedir, distname) {
    # Select all dirs starts with a distance name
    dist.pattern <- sprintf("%s_*", distname)
    xx.dirs <- dir(basedir, pattern=dist.pattern, full.names=TRUE)

    for (xx.dirname in xx.dirs) {
        weighted.compare.dir(xx.dirname)
        print(xx.dirname)
    }
}

# Weighted Unifrac & JSD
weighted.compare("../../out", "jsd")

#weighted.compare("bc")
