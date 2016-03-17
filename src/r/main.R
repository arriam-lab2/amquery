source('dm.R')

uu.full_filename = '../../data/mikkele/full/uu_full.txt'
uu.full <- dm.parse.file(uu.full_filename)

uu.path = '../../out/un_unifrac'
uu.tables <- dm.parse.dir(uu.path)

ji.full_filename = '../../out/jaccard_50/seqs.txt'
ji.full <- dm.parse.file(ji.full_filename)

ji.path = '../../out/jaccard_50'
ji.tables <- dm.parse.dir(ji.path)

uu.tables <- lapply(uu.tables, dm.reformat, uu.full)
ji.tables <- lapply(ji.tables, dm.reformat, uu.full)

ji.full <- dm.reformat(ji.full, uu.full)
uu.full$X <- NULL
rownames(uu.full) <- colnames(uu.full)
rownames(ji.full) <- colnames(ji.full)


# unifrac vs. jaccard
dm.compare.cor(ji.full, uu.full)
dm.compare.all(uu.tables, ji.tables)
dm.compare.lm(ji.tables, uu.tables)

