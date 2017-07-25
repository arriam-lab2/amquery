library(ggplot2)
library(ggthemes)
library(reshape)
library(ggsci)
library(gridExtra)
library(cowplot)


precision.read_data <- function(data_file) {
    df <- read.table(data_file)
    colnames(df) <- c(100, 300, 500, 700, 1000)
    rownames(df) <- c(1, 3, 5, 7, 10, 15, 20)
    df$k <- rownames(df)
    df <- melt(df)
    df$variable <- NULL
    df
}

precision.plot <- function (amq_data_file, baseline_data_file) {
    df.amq <- precision.read_data(amq_data_file)
    df.amq$k <- as.integer(df.amq$k)
    names(df.amq)[names(df.amq)=="value"] <- "Amquery"

    df.baseline <- precision.read_data(baseline_data_file)
    df.amq$Baseline <- df.baseline$value

    df <- melt(df.amq, id.vars=c("k"))

    p <- ggplot(data=df, aes(x=k, y=value, group=variable, colour=variable, fill=variable)) + 
        geom_point() +
        ylim(0, 1) +
        geom_smooth(alpha=0.1) + 
        labs(x='', y='', colour='') +
        scale_fill_npg() + 
        scale_fill_discrete(guide=FALSE) +
        theme_minimal() + 
        theme(legend.position="top") +
        theme(plot.margin = unit(c(12, 6, 12, 6), "pt"))
    
    p
}

precision.combined <- function(files) {
    p1 <- precision.plot(files[1], files[2]) + labs(x="")
    p2 <- precision.plot(files[3], files[4]) + labs(x="Search size, k")
    p3 <- precision.plot(files[5], files[6]) + labs(x="")
    p4 <- precision.plot(files[7], files[8]) + labs(x="")
    p5 <- precision.plot(files[9], files[10]) + labs(x="Search size, k")
    p6 <- precision.plot(files[11], files[12]) + labs(x="")

    prow <- plot_grid(
        p1 + theme(legend.position="none"),
        p2 + theme(legend.position="none"),
        p3 + theme(legend.position="none"),
        p4 + theme(legend.position="none"),
        p5 + theme(legend.position="none"),
        p6 + theme(legend.position="none"),

        align = 'vh',
        labels = c("A", "B", "C", "D", "E", "F"),
        hjust = -1,
        nrow = 2
    )

    legend <- get_legend(p1)
    p <- plot_grid(prow, legend, ncol=1, rel_heights = c(1, .2))
    p
}

time.plot <- function(df, breaks=c()) {
    p <- ggplot(df, aes(size, value, fill=variable)) + 
        geom_bar(stat="identity", position="stack", alpha=0.7) + 
        labs(x="Number of samples", y="Time in seconds") +
        scale_fill_npg(guide=guide_legend(title="", ncol=2), breaks=breaks) +
        theme_minimal() + 
        theme(legend.position="bottom") +
        theme(plot.margin = unit(c(15, 6, 6, 6), "pt"))
    p
}

mem.plot <- function(df, breaks=c()) {
    p <- ggplot(df, aes(size, value, fill=variable)) + 
        geom_bar(stat="identity", position="dodge", alpha=0.7) + 
        labs(x="Number of samples", y="Time in seconds") +
        scale_fill_npg(guide=guide_legend(title="", ncol=2), breaks=breaks) +
        theme_minimal() + 
        theme(legend.position="bottom") +
        theme(plot.margin = unit(c(15, 6, 6, 6), "pt"))
    p
}

build.time <- function(filename) {
    df <- read.table(filename)
    df.jsd <- df[c("V1")]
    df.wu.ref <- df[c("V2", "V3", "V4")]
    df.wu.denovo <- df[c("V5", "V6", "V7", "V8", "V9", "V10", "V11")]

    df.wu.denovo <- df.wu.denovo[c(7, 1, 6, 2, 3, 4, 5)]
    df.wu.ref <- df.wu.ref[c(3, 1, 2)]

    cols.jsd <- c('indexing')
    cols.wu.ref <- c('indexing', 'pick_otus', 'make_otu_table')
    cols.wu.denovo <- c('indexing', 'pick_otus', 'make_otu_table', 'pick_rep_set', 'align_seqs', 
        'filter_alignment', 'make_phylogeny')

    colnames(df.jsd) <- cols.jsd
    colnames(df.wu.ref) <- cols.wu.ref 
    colnames(df.wu.denovo) <- cols.wu.denovo

    index_size <- as.factor(c(100, 300, 500, 700, 1000))
    df.jsd$size <- index_size
    df.wu.ref$size <- index_size
    df.wu.denovo$size <- index_size
    
    df.jsd <- melt(df.jsd, id.vars='size')
    df.wu.ref <- melt(df.wu.ref, id.vars='size')
    df.wu.denovo <- melt(df.wu.denovo, id.vars='size')

    ymax <- 7500
    p1 <- time.plot(df.wu.denovo, breaks=cols.wu.denovo) + labs(x="") + ylim(0, ymax)
    p2 <- time.plot(df.wu.ref, breaks=cols.wu.ref) + labs(y="") + ylim(0, ymax)
    p3 <- time.plot(df.jsd, breaks=cols.jsd) + labs(x="", y="") + ylim(0, ymax)

    p <- plot_grid(
        p1,
        p2,
        p3,
        align = 'vh',
        labels = c("A", "B", "C"),
        hjust = -2.2,
        vjust = 1.2,
        nrow = 1
    )
    p
}

build.memory <- function(filename) {
    df <- read.table(filename)
    df.jsd <- df[c("V1")]
    df.wu.ref <- df[c("V2", "V3", "V4")]
    df.wu.denovo <- df[c("V5", "V6", "V7", "V8", "V9", "V10", "V11")]
    
    df.wu.denovo <- df.wu.denovo[c(7, 1, 6, 2, 3, 4, 5)]
    df.wu.ref <- df.wu.ref[c(3, 1, 2)]

    cols.jsd <- c('indexing')
    cols.wu.ref <- c('indexing', 'pick_otus', 'make_otu_table')
    cols.wu.denovo <- c('indexing', 'pick_otus', 'make_otu_table', 'pick_rep_set', 'align_seqs', 
        'filter_alignment', 'make_phylogeny')

    colnames(df.jsd) <- cols.jsd
    colnames(df.wu.ref) <- cols.wu.ref 
    colnames(df.wu.denovo) <- cols.wu.denovo

    index_size <- as.factor(c(100, 300, 500, 700, 1000))
    df.jsd$size <- index_size
    df.wu.ref$size <- index_size
    df.wu.denovo$size <- index_size

    df.jsd <- melt(df.jsd, id.vars='size')
    df.wu.ref <- melt(df.wu.ref, id.vars='size')
    df.wu.denovo <- melt(df.wu.denovo, id.vars='size')

    ylimit <- 2100
    p1 <- mem.plot(df.wu.denovo, breaks=cols.wu.denovo) + labs(x="", y="Memory consumption, Mb") + ylim(0, ylimit)
    p2 <- mem.plot(df.wu.ref, breaks=cols.wu.ref) + labs(y="") + ylim(0, ylimit)
    p3 <- mem.plot(df.jsd, breaks=cols.jsd) + labs(x="", y="") + ylim(0, ylimit)

    p <- plot_grid(
        p1,
        p2,
        p3,
        align = 'vh',
        labels = c("A", "B", "C"),
        hjust = -2.2,
        vjust = 1.2,
        nrow = 1
    )
    p
}


add.time <- function(filename, ymax) {
    df <- read.table(filename)
    df.jsd <- df[c("V1")]
    df.wu.ref <- df[c("V2", "V3")]
    df.wu.denovo <- df[c("V4", "V5")]

    df.wu.denovo <- df.wu.denovo[c(2, 1)]
    df.wu.ref <- df.wu.ref[c(2, 1)]
    
    cols.jsd <- c('indexing')
    cols.wu.ref <- c('indexing', 'map_reads')
    cols.wu.denovo <- c('indexing', 'map_reads')
    
    colnames(df.jsd) <- cols.jsd
    colnames(df.wu.ref) <- cols.wu.ref
    colnames(df.wu.denovo) <- cols.wu.denovo
    
    index_size <- as.factor(c(100, 300, 500, 700, 1000))
    df.jsd$size <- index_size
    df.wu.ref$size <- index_size
    df.wu.denovo$size <- index_size

    df.jsd <- melt(df.jsd, id.vars='size')
    df.wu.ref <- melt(df.wu.ref, id.vars='size')
    df.wu.denovo <- melt(df.wu.denovo, id.vars='size')

    result <- list()
    result$p1 <- time.plot(df.wu.denovo, breaks=cols.wu.denovo) + labs(x="") + ylim(0, ymax)
    result$p2 <- time.plot(df.wu.ref, breaks=cols.wu.ref) + labs(y="") + ylim(0, ymax)
    result$p3 <- time.plot(df.jsd, breaks=cols.jsd) + labs(x="", y="") + ylim(0, ymax)
    result
}

add.time.combined <- function(filename1, filename2, ymax1, ymax2) {
    plots1 <- add.time(filename1, ymax1)
    plots2 <- add.time(filename2, ymax2)
    p <- plot_grid(
        plots1$p1 + theme(legend.position="none") + labs(y=""),
        plots1$p2 + theme(legend.position="none") + labs(x=""),
        plots1$p3 + theme(legend.position="none"),
        plots2$p1 + theme(legend.position="none"),
        plots2$p2 + theme(legend.position="none"),
        plots2$p3 + theme(legend.position="none"),
        align = 'vh',
        labels = c("A", "B", "C", "D", "E", "F"),
        hjust = -2.2,
        vjust = 1.2,
        nrow = 2
    )
    
    legend <- get_legend(plots1$p1)
    p <- plot_grid(p, legend, ncol=1, rel_heights = c(1, .2))
    p
}

add.memory <- function(filename, ymax) {
    df <- read.table(filename)
    df.jsd <- df[c("V1")]
    df.wu.ref <- df[c("V2", "V3")]
    df.wu.denovo <- df[c("V4", "V5")]

    df.wu.denovo <- df.wu.denovo[c(2, 1)]
    df.wu.ref <- df.wu.ref[c(2, 1)]
    
    cols.jsd <- c('indexing')
    cols.wu.ref <- c('indexing', 'map_reads')
    cols.wu.denovo <- c('indexing', 'map_reads')
    
    colnames(df.jsd) <- cols.jsd
    colnames(df.wu.ref) <- cols.wu.ref
    colnames(df.wu.denovo) <- cols.wu.denovo

    index_size <- as.factor(c(100, 300, 500, 700, 1000))
    df.jsd$size <- index_size
    df.wu.ref$size <- index_size
    df.wu.denovo$size <- index_size

    df.jsd <- melt(df.jsd, id.vars='size')
    df.wu.ref <- melt(df.wu.ref, id.vars='size')
    df.wu.denovo <- melt(df.wu.denovo, id.vars='size')

    p1 <- mem.plot(df.wu.denovo, breaks=cols.wu.denovo) + labs(x="", y="Memory consumption, Mb") + ylim(0, ymax)
    p2 <- mem.plot(df.wu.ref, breaks=cols.wu.ref) + labs(y="") + ylim(0, ymax)
    p3 <- mem.plot(df.jsd, breaks=cols.jsd) + labs(x="", y="") + ylim(0, ymax)

    p <- plot_grid(
        p1,
        p2,
        p3,
        align = 'vh',
        labels = c("A", "B", "C"),
        hjust = -2.2,
        vjust = 1.2,
        nrow = 1
    )
    p
}


draw.build <- function() {
    p1 <- build.time('out/build_time.txt')
    ggsave("out/build_time.tiff", p1, width=18, height=9, units="cm")

    p2 <- build.memory('out/build_memory.txt')
    ggsave("out/build_memory.tiff", p2, width=18, height=9, units="cm")
}

draw.add <- function() {
    p <- add.time.combined('out/add_100_time.txt', 'out/add_300_time.txt', 1300, 3000)
    ggsave("out/add_100_300_time.tiff", p, width=18, height=16, units="cm")
    p <- add.time.combined('out/add_500_time.txt', 'out/add_1000_time.txt', 5000, 10000)
    ggsave("out/add_500_1000_time.tiff", p, width=18, height=16, units="cm")

    #p <- add.memory('out/add_100_memory.txt', 1000)
    #ggsave("out/add_100_memory.tiff", p, width=18, height=9, units="cm")
    #p <- add.memory('out/add_300_memory.txt', 1000)
    #ggsave("out/add_300_memory.tiff", p, width=18, height=9, units="cm")
    #p <- add.memory('out/add_500_memory.txt', 1000)
    #ggsave("out/add_500_memory.tiff", p, width=18, height=9, units="cm")
    #p <- add.memory('out/add_700_memory.txt', 1000)
    #ggsave("out/add_700_memory.tiff", p, width=18, height=9, units="cm")
    #p <- add.memory('out/add_1000_memory.txt', 1000)
    #ggsave("out/add_1000_memory.tiff", p, width=18, height=9, units="cm")
}

precision <- function() {
    p <- precision.combined(c('wu_mp_at_k.txt', 'wu_bmp_at_k.txt', 'wu_map_at_k.txt', 'wu_bmap_at_k.txt', 'wu_gain_at_k.txt', 'wu_bgain_at_k.txt',
                              'bc_mp_at_k.txt', 'bc_bmp_at_k.txt', 'bc_map_at_k.txt', 'bc_bmap_at_k.txt', 'bc_gain_at_k.txt', 'bc_bgain_at_k.txt'))
    ggsave("ref_precision.tiff", p, width=18, height=16, units="cm")

}

draw.build()
draw.add()