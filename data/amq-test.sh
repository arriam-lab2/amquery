
function run_amq_test {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    pattern=$4
    index_dir="${output_dir}/${build_size}"


    for k in 1 3 5 7 10 15 20
    do
        amq-test --workon "${index_dir}" -q minprecision \
            $(find ${split_dir}/$build_size/main -type l -name "${pattern}" -exec readlink {} \;) \
            -r /home/ilia/storage/metagen/bench/denovo/${build_size}/wu/weighted_unifrac_otu_table.txt \
            -k $k$ > "${index_dir}/minp_$k.txt" 2> "${index_dir}/minp.log"
    done;
}



if [[ $# -ne 2 ]]; then
    echo "Usage: bash $0 <input-dir> <output-dir>"
else
    pattern='*.fasta'
    
    for build_size in {100..1000..100}
    do
        run_amq_test $1 $2 $build_size "${pattern}"
    done;
fi
