function run_amq {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    pattern=$4
    index_dir="${output_dir}/${build_size}"

    amq --workon "${index_dir}" init origin

    # build the index
    # NOTE: symbolic links only
    /usr/bin/time -v amq build \
        $(find ${split_dir}/$build_size/main -type l -name "${pattern}" -exec readlink {} \;) \
        > "${index_dir}/build_time.log" 2> "${index_dir}/build_memory.log"

    echo $build_size-samples index built
    
    for add_size in {100..1000..100}
    do
        # make a copy of the current index 
        cp -r "${index_dir}/origin" "${index_dir}/$add_size"
        amq use $add_size
        to_add=$(find ${split_dir}/$build_size/additional -type l -name "${pattern}" -exec readlink {} \; | shuf -n $add_size | xargs realpath)

        # add new samples
        /usr/bin/time -v amq add `echo ${to_add}` > "${index_dir}/add_${add_size}_time.log" \
            2> "${index_dir}/add_${add_size}_memory.log"

        # clean up
        rm -r "${index_dir}/$add_size"
        echo "${to_add}" > "${index_dir}"/add_${add_size}_list.txt
        echo $build_size: $add_size added
    done;
}


if [[ $# -ne 2 ]]; then
    echo "Usage: bash bench.sh <input-dir> <output-dir>"
else
    pattern='*.fasta'
    
    for build_size in {100..1000..100}
    do
        run_amq $1 $2 $build_size "${pattern}"
    done;
fi
