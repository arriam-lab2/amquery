source('dm.R')

uu_full_filename = 'data/unweighted_unifrac_otu_table.txt'
#uu_full_filename = 'data/weighted_unifrac_otu_table.txt'
uf <- dm.parse.file(uu_full_filename)

uu_path = 'data/out3/unweighted_unifrac/rare_dm/'
uu_tables <- dm.parse.dir(uu_path)

ji_full_filename = 'out/ji_full.txt'
#ji_full_filename = 'out/jsd_full.txt'
jf <- dm.parse.file(ji_full_filename)

ji_path = 'out/ji'
#ji_path = 'out/jsd'
ji_tables <- dm.parse.dir(ji_path)

uu_tables <- lapply(uu_tables, dm.reformat, uf)
ji_tables <- lapply(ji_tables, dm.reformat, uf)
jf <- dm.reformat(jf, uf)
uf$X <- NULL
rownames(uf) <- colnames(uf)
rownames(jf) <- colnames(jf)


# unifrac vs. jaccard
dm.compare(uf, jf)
dm.compare(uf, uf)


source('jackknife.R')
round(jk.pseudomean(uu_tables, uf), 4)
round(jk.pseudovar(uu_tables, uf), 4)

round(jk.pseudomean(ji_tables, jf), 4)
round(jk.pseudovar(ji_tables, jf), 4)

round(jk.mean(uu_tables), 4)
round(jk.var(uu_tables), 4)

round(jk.mean(ji_tables), 4)
round(jk.var(ji_tables), 4)

dm.compare.ci(uu_tables, ji_tables, uf)


#uu <- uu_tables[[1]]
#lapply(uu_tables, dm.compare, ji)
#dm.compare(uu, ji)

