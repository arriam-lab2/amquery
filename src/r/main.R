source('dm.R')

uu.full_filename <- '../../data/mikkele/full/uu_full.txt'
uu.full <- dm.parse.file(uu.full_filename)
uu.path <- '../../out/un_unifrac'
uu.tables <- dm.parse.dir(uu.path)

wu.full_filename <- '../../data/mikkele/full/wu_full.txt'
wu.full <- dm.parse.file(wu.full_filename)
wu.path <- '../../out/w_unifrac'
wu.tables <- dm.parse.dir(wu.path)

ji.full_filename <- '../../out/jaccard_50/seqs.txt'
ji.full <- dm.parse.file(ji.full_filename)
ji.path <- '../../out/jaccard_50'
ji.tables <- dm.parse.dir(ji.path)

bc.full_filename <- '../../out/bc_50/seqs.txt'
bc.full <- dm.parse.file(bc.full_filename)
bc.path <- '../../out/bc_50'
bc.tables <- dm.parse.dir(bc.path)

uu.tables <- lapply(uu.tables, dm.reformat, uu.full)
wu.tables <- lapply(wu.tables, dm.reformat, uu.full)
ji.tables <- lapply(ji.tables, dm.reformat, uu.full)
bc.tables <- lapply(bc.tables, dm.reformat, uu.full)

wu.full <- dm.reformat(wu.full, uu.full)
ji.full <- dm.reformat(ji.full, uu.full)
bc.full <- dm.reformat(bc.full, uu.full)
uu.full$X <- NULL
rownames(uu.full) <- colnames(uu.full)
rownames(wu.full) <- colnames(wu.full)
rownames(ji.full) <- colnames(ji.full)
rownames(bc.full) <- colnames(bc.full)


# u.unifrac & jaccard
dm.compare.cor(ji.full, uu.full)
dm.compare.all(uu.tables, ji.tables)
dm.compare.lm(ji.tables, uu.tables)

# w.unifrac & jaccard
dm.compare.cor(ji.full, wu.full)
dm.compare.all(wu.tables, ji.tables)
dm.compare.lm(ji.tables, wu.tables)

# unifrac & bray-curtis
dm.compare.cor(bc.full, uu.full)
dm.compare.all(uu.tables, bc.tables)
dm.compare.lm(bc.tables, uu.tables)

# unifrac & bray-curtis
dm.compare.cor(bc.full, wu.full)
dm.compare.all(wu.tables, bc.tables)
dm.compare.lm(bc.tables, wu.tables)

