source('dm.R')


wu.full_filename <- '../../data/mikkele/full/wu_full.txt'
wu.full <- dm.parse.file(wu.full_filename)
wu.path <- '../../out/w_unifrac'
wu.tables <- dm.parse.dir(wu.path)

gji.full_filename <- '../../out/gji_50/seqs.txt'
gji.full <- dm.parse.file(gji.full_filename)
gji.path <- '../../out/gji_50'
gji.tables <- dm.parse.dir(gji.path)

bc.full_filename <- '../../out/bc_50/seqs.txt'
bc.full <- dm.parse.file(bc.full_filename)
bc.path <- '../../out/bc_50'
bc.tables <- dm.parse.dir(bc.path)

jsd.full_filename <- '../../out/jsd_50/seqs.txt'
jsd.full <- dm.parse.file(jsd.full_filename)
jsd.path <- '../../out/jsd_50'
jsd.tables <- dm.parse.dir(jsd.path)

wu.tables <- lapply(wu.tables, dm.reformat, wu.full)
gji.tables <- lapply(gji.tables, dm.reformat, wu.full)
bc.tables <- lapply(bc.tables, dm.reformat, wu.full)
jsd.tables <- lapply(jsd.tables, dm.reformat, wu.full)

bc.full <- dm.reformat(bc.full, wu.full)
jsd.full <- dm.reformat(jsd.full, wu.full)
gji.full <- dm.reformat(gji.full, wu.full)
wu.full$X <- NULL

rownames(wu.full) <- colnames(wu.full)
rownames(gji.full) <- colnames(gji.full)
rownames(bc.full) <- colnames(bc.full)
rownames(jsd.full) <- colnames(jsd.full)

dm.compare.cor(gji.full, wu.full)
dm.compare.all(wu.tables, gji.tables)

# w.unifrac & jsd
dm.compare.cor(jsd.full, wu.full)
dm.compare.all(wu.tables, jsd.tables)

# w.unifrac & bray-curtis
dm.compare.cor(bc.full, wu.full)
dm.compare.all(wu.tables, bc.tables)
