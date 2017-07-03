function run_amq {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    index_dir="${output_dir}/${build_size}"

    pushd `pwd`
    mkdir -p ${index_dir}/origin && cd ${index_dir}/origin

    amq init
    qiime_dir=/home/ilia/storage/metagen/bench/denovo/
    #amq init --rep_tree=${qiime_dir}/$build_size/rep_set.tre --biom_table=${qiime_dir}/$build_size/otu_table.biom --method=weighted-unifrac

    # build an index
    /usr/bin/time -v amq build ${split_dir}/$build_size/main.fna \
        > "${index_dir}/build_time.log" 2> "${index_dir}/build_memory.log"

    echo $build_size-samples index built

    for add_size in {100..1000..100}
    do
        # make a copy of the current index 
        cp -r "${index_dir}/origin" "${index_dir}/$add_size"
        pushd `pwd` && cd "${index_dir}/$add_size"

        # add new samples
        /usr/bin/time -v amq add "${split_dir}/$build_size/additional.fna" \
            > "${index_dir}/${add_size}/add_time.log" 2> \
            "${index_dir}/${add_size}/add_memory.log"

        # clean up
        # rm -r "${index_dir}/$add_size"
        echo $build_size: $add_size added

        popd
    done;

    popd
}


if [[ $# -ne 2 ]]; then
    echo "Usage: bash $0 <input-dir> <output-dir>"
else
    for build_size in {100..1000..100}
    do
        run_amq $1 $2 $build_size
    done;
fi
