function amq_test {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    pattern=$4
    index_dir="${output_dir}/${build_size}"

    test_size=100
    wu_table="/home/ilia/storage/metagen/bench/ref/$build_size/wu/weighted_unifrac_otu_table.txt"
    to_test=$(find ${split_dir}/$build_size/main -type l -name "${pattern}" -exec readlink {} \; | shuf -n $test_size | xargs realpath)

    amq --workon "${index_dir}" use origin
    k=5

    echo $build_size...
    for k in 5 7 10 15 20
    do
        amq-test -q precision `echo ${to_test}` -r "$wu_table" -k "$k" > "${index_dir}/test_${k}.log" 
        echo $k
    done;
    echo " OK"
}


if [[ $# -ne 2 ]]; then
    echo "Usage: bash $0 <input-dir> <output-dir>"
else
    pattern='*.fasta'
    
    for build_size in {100..1000..100}
    do
        amq_test $1 $2 $build_size "${pattern}"
    done;
fi
