# jk.-functions expect that dm is a result of jackknife resampling

sqr <- function(x) { x^2 }

jk.pseudovar <- function(dm_list, dfull) {
    N <- length(dm_list)
    residuals <- lapply(dm_list, '-', dfull)
    rss <- lapply(residuals, sqr)
    rss_sum <- Reduce('+', rss)
    return ((N-1)/N * rss_sum)
}

jk.mean <- function(dm_list) {
    N <- length(dm_list)
    return (Reduce('+', dm_list) / N)
}

jk.var <- function(dm_list) {
    N <- length(dm_list)
    dm_mean <- jk.mean(dm_list)
    residuals <- lapply(dm_list, '-', dm_mean)
    rss <- lapply(residuals, sqr)
    rss_sum <- Reduce('+', rss)
    return (rss_sum / (N - 1))

}
