function run_amq {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    index_dir="${output_dir}/${build_size}"

    pushd `pwd`
    mkdir -p ${index_dir}/origin && cd ${index_dir}/origin
    amq init

    # build an index
    /usr/bin/time -v amq build ${split_dir}/$build_size/main.fna \
        > "${index_dir}/build_time.log" 2> "${index_dir}/build_memory.log"

    echo $build_size-samples index built

    for add_size in {100..1000..100}
    #for add_size in {1..5..2}
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

function merge_fasta {
    split_dir=$1
    index_size=$2
    amq_source=`python -c "import amquery; print(amquery.__file__)"`
    amq_dir=`dirname ${amq_source}`
    python ${amq_dir}/utils/merge_fasta.py `find ${split_dir}/${index_size}/main/ -type l -exec readlink {} \; ` -o ${split_dir}/${index_size}/main.fna
    python ${amq_dir}/utils/merge_fasta.py `find ${split_dir}/${index_size}/additional/ -type l -exec readlink {} \; ` -o ${split_dir}/${index_size}/additional.fna
    #python ${amq_dir}/utils/merge_fasta.py `find ${split_dir}/${index_size}/main/ -type f` -o ${split_dir}/${index_size}/main.fna
    #python ${amq_dir}/utils/merge_fasta.py `find ${split_dir}/${index_size}/additional/ -type f` -o ${split_dir}/${index_size}/additional.fna
}

if [[ $# -ne 2 ]]; then
    echo "Usage: bash bench.sh <input-dir> <output-dir>"
else
    #for build_size in {100..1000..100}
    #do
    #    merge_fasta $1 ${build_size}
    #done;

    for build_size in {100..1000..100}
    #for build_size in 10
    do
        run_amq $1 $2 $build_size
    done;
fi
