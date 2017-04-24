library(ggplot2)
library(ggthemes)
library(reshape)
library(ggsci)
library(gridExtra)
library(cowplot)


precision.read_data <- function(data_file) {
    df <- read.table(data_file)
    colnames(df) <- c(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)
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

time.plot <- function(df) {
    p <- ggplot(df, aes(size, value, fill=variable)) + 
        geom_bar(stat="identity", position="stack", alpha=0.7) + 
        labs(x="Number of samples", y="Time in seconds") +
        scale_fill_npg(guide=guide_legend(title="", ncol=1)) +
        theme_minimal() + 
        theme(legend.position="bottom") +
        theme(plot.margin = unit(c(15, 6, 6, 6), "pt"))
    p
}

time.ref.combined <- function(filename) {
    df <- read.table(filename)
    df.amq <- df[c("V1", "V2", "V3")]
    df.qiime.wu <- df[c("V1", "V4", "V5", "V6")]
    df.qiime.bc <- df[c("V1", "V4", "V5", "V7")]

    colnames(df.amq) <- c('size', 'k-mer counting', 'Tree construction')
    colnames(df.qiime.wu) <- c('size', 'pick_otus', 'make_otu_table', 'beta_diversity')
    colnames(df.qiime.bc) <- c('size', 'pick_otus', 'make_otu_table', 'beta_diversity')

    df.amq <- melt(df.amq, id.vars='size')
    df.qiime.wu <- melt(df.qiime.wu, id.vars='size')
    df.qiime.bc <- melt(df.qiime.bc, id.vars='size')

    p1 <- time.plot(df.qiime.bc) + labs(x="") + ylim(0, 900)
    p2 <- time.plot(df.qiime.wu) + labs(y="") + ylim(0, 900)
    p3 <- time.plot(df.amq) + labs(x="", y="") + ylim(0, 900)

    p <- plot_grid(
        p1,
        p2 ,
        p3,
        align = 'vh',
        labels = c("A", "B", "C"),
        hjust = -1,
        nrow = 1
    )
    p
}

time.denovo.combined <- function(filename) {
    df <- read.table(filename)
    df.amq <- df[c("V1", "V2", "V3")]
    df.qiime.wu <- df[c("V1", "V4", "V5", "V6", "V7", "V8", "V9", "V10")]
    df.qiime.bc <- df[c("V1", "V4", "V5", "V6", "V7", "V8", "V9", "V11")]

    colnames(df.amq) <- c('size', 'k-mer counting', 'Tree construction')
    qiime_columns <- c('size', 'pick_otus', 'pick_rep_set', 'align_seqs', 'filter_alignment', 
                       'make_phylogeny', 'make_otu_table', 'beta_diversity')
    colnames(df.qiime.wu) <- qiime_columns
    colnames(df.qiime.bc) <- qiime_columns

    df.amq <- melt(df.amq, id.vars='size')
    df.qiime.wu <- melt(df.qiime.wu, id.vars='size')
    df.qiime.bc <- melt(df.qiime.bc, id.vars='size')

    p1 <- time.plot(df.qiime.bc) + labs(x="") + ylim(0, 7500)
    p2 <- time.plot(df.qiime.wu) + labs(y="") + ylim(0, 7500)
    p3 <- time.plot(df.amq) + labs(x="", y="") + ylim(0, 7500)

    p <- plot_grid(
        p1,
        p2 ,
        p3,
        align = 'vh',
        labels = c("A", "B", "C"),
        hjust = -1,
        nrow = 1
    )
    p
}

mem.plot <- function(df) {
    p <- ggplot(df, aes(size, value, fill=variable)) + 
        geom_bar(stat="identity", position="dodge", alpha=0.7) + 
        labs(x="Number of samples", y="Time in seconds") +
        scale_fill_npg(guide=guide_legend(title="", ncol=2)) +
        theme_minimal() + 
        theme(legend.position="bottom") +
        theme(plot.margin = unit(c(15, 6, 6, 6), "pt"))
    p
}

mem.ref.combined <- function(filename) {
    df <- read.table(filename)
    df.amq <- df[c("V1", "V2")]
    df.qiime.wu <- df[c("V1", "V3", "V4", "V5")]
    df.qiime.bc <- df[c("V1", "V3", "V4", "V6")]

    colnames(df.amq) <- c('size', 'Overall')
    qiime_columns <- c('size', 'pick_otus', 'make_otu_table', 'beta_diversity')
    colnames(df.qiime.wu) <- qiime_columns
    colnames(df.qiime.bc) <- qiime_columns

    df.amq <- melt(df.amq, id.vars='size')
    df.qiime.wu <- melt(df.qiime.wu, id.vars='size')
    df.qiime.bc <- melt(df.qiime.bc, id.vars='size')

    p1 <- mem.plot(df.qiime.bc) + labs(x="", y="Memory consumption, Mb") + ylim(0, 1500)
    p2 <- mem.plot(df.qiime.wu) + labs(y="") + ylim(0, 1500)
    p3 <- mem.plot(df.amq) + labs(x="", y="") + ylim(0, 1500)

    p <- plot_grid(
        p1,
        p2 ,
        p3,
        align = 'vh',
        labels = c("A", "B", "C"),
        hjust = -1,
        nrow = 1
    )
    p
}

mem.denovo.combined <- function(filename) {
    df <- read.table(filename)
    df.amq <- df[c("V1", "V2")]
    df.qiime.wu <- df[c("V1", "V3", "V4", "V5", "V6", "V7", "V8", "V9")]
    df.qiime.bc <- df[c("V1", "V3", "V4", "V5", "V6", "V7", "V8", "V10")]

    colnames(df.amq) <- c('size', 'Overall')
    qiime_columns <- c('size', 'pick_otus', 'pick_rep_set', 'align_seqs', 'filter_alignment', 
                       'make_phylogeny', 'make_otu_table', 'beta_diversity')
    colnames(df.qiime.wu) <- qiime_columns
    colnames(df.qiime.bc) <- qiime_columns

    df.amq <- melt(df.amq, id.vars='size')
    df.qiime.wu <- melt(df.qiime.wu, id.vars='size')
    df.qiime.bc <- melt(df.qiime.bc, id.vars='size')

    p1 <- mem.plot(df.qiime.bc) + labs(x="", y="Memory consumption, Mb") + ylim(0, 2500)
    p2 <- mem.plot(df.qiime.wu) + labs(y="") + ylim(0, 2500)
    p3 <- mem.plot(df.amq) + labs(x="", y="") + ylim(0, 2500)

    p <- plot_grid(
        p1,
        p2 ,
        p3,
        align = 'vh',
        labels = c("A", "B", "C"),
        hjust = -1,
        nrow = 1
    )
    p
}


p1 <- precision.combined(c('wu_mp_at_k.txt', 'wu_bmp_at_k.txt', 'wu_map_at_k.txt', 'wu_bmap_at_k.txt', 'wu_gain_at_k.txt', 'wu_bgain_at_k.txt',
                           'bc_mp_at_k.txt', 'bc_bmp_at_k.txt', 'bc_map_at_k.txt', 'bc_bmap_at_k.txt', 'bc_gain_at_k.txt', 'bc_bgain_at_k.txt'))
ggsave("ref_precision.tiff", p1, width=18, height=16, units="cm")

p3 <- time.ref.combined('ref_time.txt')
ggsave("ref_time.tiff", p3, width=18, height=9, units="cm")

p4 <- time.denovo.combined('denovo_time.txt')
ggsave("denovo_time.tiff", p4, width=18, height=12, units="cm")

p5 <- mem.ref.combined('ref_mem.txt')
ggsave("ref_mem.tiff", p5, width=18, height=9, units="cm")

p6 <- mem.denovo.combined('denovo_mem.txt')
ggsave("denovo_mem.tiff", p6, width=18, height=10, units="cm")