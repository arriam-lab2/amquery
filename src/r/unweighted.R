source('dm.R')

uu.full_filename <- '../../data/mikkele/full/uu_full.txt'
uu.full <- dm.parse.file(uu.full_filename)
uu.path <- '../../out/un_unifrac'
uu.tables <- dm.parse.dir(uu.path)

bc.full_filename <- '../../out/bc_50/seqs.txt'
bc.full <- dm.parse.file(bc.full_filename)
bc.path <- '../../out/bc_50'
bc.tables <- dm.parse.dir(bc.path)

jsd.full_filename <- '../../out/jsd_50/seqs.txt'
jsd.full <- dm.parse.file(jsd.full_filename)
jsd.path <- '../../out/jsd_50'
jsd.tables <- dm.parse.dir(jsd.path)

uu.tables <- lapply(uu.tables, dm.reformat, uu.full)
bc.tables <- lapply(bc.tables, dm.reformat, uu.full)
jsd.tables <- lapply(jsd.tables, dm.reformat, uu.full)

bc.full <- dm.reformat(bc.full, uu.full)
jsd.full <- dm.reformat(jsd.full, uu.full)
uu.full$X <- NULL

rownames(uu.full) <- colnames(uu.full)
rownames(bc.full) <- colnames(bc.full)
rownames(jsd.full) <- colnames(jsd.full)

# u.unifrac & jsd
dm.compare.cor(jsd.full, uu.full)
dm.compare.all(uu.tables, jsd.tables)

# u.unifrac & bray-curtis
dm.compare.cor(bc.full, uu.full)
dm.compare.all(uu.tables, bc.tables)
