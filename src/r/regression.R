library(phyloseq)
library(ggplot2)
library(ape)
library(reshape2)

scatter.plot <- function(dataset, dist1, dist2) {
    x <- distance(gm, dist1)
    x.matrix <- as.matrix(x)
    x.melted <- melt(x.matrix)

    y <- distance(gm, dist2)
    y.matrix <- as.matrix(y)
    y.melted <- melt(y.matrix)

    df <- y.melted
    df$x <- x.melted$value

    g <- ggplot(data=df, aes(x=x, y=value, color=Var2)) + geom_point()
    g
}

read.qiime.data <- function(dir,
    biomfile="otu_table.biom",
    mapfile="map.txt",
    treefile="rep_set.tre")
{
    otu.table <- import_biom(paste0(dir, "/", biomfile))
    map <- import_qiime_sample_data(paste0(dir, "/", mapfile))
    tree <- read.tree(paste0(dir, "/", treefile))
    data <- merge_phyloseq(otu.table, map, tree)
    data
}

data(GlobalPatterns)

mikkele <- read.qiime.data("../../data/mikkele")

plot <- scatter.plot(mikkele, "jsd", "wunifrac")
print(plot)

plot <- scatter.plot(GlobalPatterns, "jsd", "wunifrac")
print(plot)
