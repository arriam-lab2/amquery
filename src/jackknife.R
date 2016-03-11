# jk.-functions expect that dm is a result of jackknife resampling

# jackknife-pseudovalue
jk.pseudovalue <- function(di, dfull, N) {
    return (N*dfull - (N-1)*di) 
}

# mean of jackknife-pseudovalues
jk.pseudomean <- function(dm_list, dfull, N) {
    pseudovalues <- lapply(dm_list, jk.pseudovalue, dfull, N)
    return (Reduce('+', pseudovalues) / N)
}


