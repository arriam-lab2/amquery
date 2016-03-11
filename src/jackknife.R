# jk.-functions expect that dm is a result of jackknife resampling

# jackknife-pseudovalue
jk.pseudovalue <- function(di, dfull, N) {
    return (N*dfull - (N-1)*di) 
}

# mean of jackknife-pseudovalues
jk.pseudomean <- function(dm_list, dfull) {
    N <- length(dm_list)
    pseudovalues <- lapply(dm_list, jk.pseudovalue, dfull, N)
    return (Reduce('+', pseudovalues) / N)
}

sqr <- function(x) { x^2 }

jk.pseudovar <- function(dm_list, dfull) {
    N <- length(dm_list)
    residuals <- lapply(dm_list, '-', dfull)
    rss <- lapply(residuals, sqr)
    rss_sum <- Reduce('+', rss)
    return ((N-1)/N * rss_sum)
}


jk.mean <- function(dm_list, dfull) {
    N <- length(dm_list)
    return (Reduce('+', dm_list) / N)
}

