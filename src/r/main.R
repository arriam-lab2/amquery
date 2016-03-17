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
dm.compare.cor(uu.full, ji.full)
dm.compare.all(ji.tables, uu.tables)

df <- melt(uu.full)
df$jaccard <- melt(ji.full)$value
l <- lm(data=df, value ~ poly(jaccard, degree=2))
summary(l)

res <- residuals(l)
ks.test(unique(res), "punif")

#dm.compare.ci(uu_tables, ji_tables, uf)
