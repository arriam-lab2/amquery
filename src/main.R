source('dm.R')

uu_full_filename = 'data/unweighted_unifrac_otu_table.txt'
#uu_full_filename = 'data/weighted_unifrac_otu_table.txt'
uf <- dm.parse.file(uu_full_filename)

#uu_path = 'data/out3/unweighted_unifrac/rare_dm/'
uu_path = 'out/un_unifrac'
uu_tables <- dm.parse.dir(uu_path)

ji_full_filename = 'out/jaccard_50/seqs.txt'
jf <- dm.parse.file(ji_full_filename)

ji_path = 'out/jaccard_50'
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

df <- melt(uf)
df$jaccard <- melt(jf)$value
l <- lm(data=df, value ~ poly(jaccard, degree=2))
summary(l)

res <- residuals(l)
ks.test(unique(res), "punif")

#dm.compare.ci(uu_tables, ji_tables, uf)
