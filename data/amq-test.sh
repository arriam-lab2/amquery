
function run_amq_test {
    split_dir="${1}"
    output_dir="${2}"
    build_size=$3
    bench_subdir=$4
    index_dir="${output_dir}/${build_size}"
    bench_dir=/home/ilia/storage/metagen/bench

    pushd `pwd` && cd "${index_dir}/origin"
    
    for k in 1 3 5 7 10 15 20
    do
        amq-test -q precision \
            ${split_dir}/$build_size/main.fna \
            -r ${bench_dir}/$bench_subdir/${build_size}/wu/weighted_unifrac_otu_table.txt \
            -k $k > "${index_dir}/minp_${bench_subdir}_$k.txt" 2> "${index_dir}/minp_${bench_subdir}.log"
    done;

    popd
}



if [[ $# -ne 2 ]]; then
    echo "Usage: bash $0 <input-dir> <output-dir>"
else
    for build_size in 100 300 500 700 1000
    do
        run_amq_test $1 $2 $build_size denovo
        run_amq_test $1 $2 $build_size ref
    done;
fi
