function run_amq_denovo {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    index_dir="${output_dir}/${build_size}"

    pushd `pwd`
    mkdir -p ${index_dir}/origin && cd ${index_dir}/origin

    qiime_dir=/home/ilia/storage/metagen/bench/denovo/
    biom_table=${qiime_dir}/$build_size/otu_table.biom 
    rep_tree=${qiime_dir}/$build_size/rep_set.tre 
    rep_set=${qiime_dir}/$build_size/rep_set.fna

    amq init --rep_tree="${rep_tree}" --biom_table="${biom_table}" --method=weighted-unifrac

    /usr/bin/time -v amq build ${split_dir}/$build_size/main.fna \
        > "${index_dir}/build_time.log" 2> "${index_dir}/build_memory.log"

    echo $build_size-samples index built

    for add_size in 100 300 500 700 1000
    do
        cp -r "${index_dir}/origin" "${index_dir}/$add_size"
        pushd `pwd` && cd "${index_dir}/$add_size"
       
        to_add=$(find ${split_dir}/$build_size/additional -type l -exec readlink {} \; | shuf -n $add_size | xargs realpath)
        amq_source=`python -c "import amquery; print(amquery.__file__)"`
        amq_dir=`dirname ${amq_source}`
        add_x_fna=${index_dir}/${add_size}/add_${add_size}.fna
        python ${amq_dir}/utils/merge_fasta.py `echo ${to_add} | xargs` -o "${add_x_fna}"

        workon qiime
        #/usr/bin/time -v map_reads_to_reference.py -i "${add_x_fna}" -r "${rep_set}" -m bwa-sw \
        /usr/bin/time -v map_reads_to_reference.py -i "${add_x_fna}" -r "${rep_set}" \
            > "${index_dir}/preadd_${add_size}_time.log" 2> "${index_dir}/preadd_${add_size}_memory.log"
        workon amq-env

        #/usr/bin/time -v amq add `echo ${to_add} | xargs` --biom_table bwa-sw_mapped/observation_table.biom \
        /usr/bin/time -v amq add `echo ${to_add} | xargs` --biom_table usearch_mapped/observation_table.biom \
            > "${index_dir}/add_${add_size}_time.log" 2> "${index_dir}/add_${add_size}_memory.log"

        amq stats
        rm -r "${index_dir}/$add_size"
        echo $build_size: $add_size added

        popd
    done;

    popd
}

function run_amq_ref {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    index_dir="${output_dir}/${build_size}"

    pushd `pwd`
    mkdir -p ${index_dir}/origin && cd ${index_dir}/origin

    qiime_dir=/home/ilia/storage/metagen/bench/ref/
    biom_table=${qiime_dir}/$build_size/otu_table.biom 
    rep_tree=/home/ilia/storage/metagen/hitdb/HITdb.tre
    rep_set=/home/ilia/storage/metagen/hitdb/HITdb_sequences.fna

    amq init --rep_tree="${rep_tree}" --biom_table="${biom_table}" --method=weighted-unifrac
    echo amq init --rep_tree="${rep_tree}" --biom_table="${biom_table}" --method=weighted-unifrac

    /usr/bin/time -v amq build ${split_dir}/$build_size/main.fna \
        > "${index_dir}/build_time.log" 2> "${index_dir}/build_memory.log"

    echo $build_size-samples index built

    for add_size in 100 300 500 700 1000
    do
        cp -r "${index_dir}/origin" "${index_dir}/$add_size"
        pushd `pwd` && cd "${index_dir}/$add_size"
       
        to_add=$(find ${split_dir}/$build_size/additional -type l -exec readlink {} \; | shuf -n $add_size | xargs realpath)
        amq_source=`python -c "import amquery; print(amquery.__file__)"`
        amq_dir=`dirname ${amq_source}`
        add_x_fna=${index_dir}/${add_size}/add_${add_size}.fna
        python ${amq_dir}/utils/merge_fasta.py `echo ${to_add} | xargs` -o "${add_x_fna}"

        workon qiime
        #/usr/bin/time -v map_reads_to_reference.py -i "${add_x_fna}" -r "${rep_set}" -m bwa-sw \
        /usr/bin/time -v map_reads_to_reference.py -i "${add_x_fna}" -r "${rep_set}" \
            > "${index_dir}/preadd_${add_size}_time.log" 2> "${index_dir}/preadd_${add_size}_memory.log"
        workon amq-env

        #/usr/bin/time -v amq add `echo ${to_add} | xargs` --biom_table bwa-sw_mapped/observation_table.biom \
        /usr/bin/time -v amq add `echo ${to_add} | xargs` --biom_table usearch_mapped/observation_table.biom \
            > "${index_dir}/add_${add_size}_time.log" 2> "${index_dir}/add_${add_size}_memory.log"

        amq stats
        rm -r "${index_dir}/$add_size"
        echo $build_size: $add_size added

        popd
    done;

    popd
}


function run_amq {
    split_dir=`realpath "${1}"`
    output_dir=`realpath "${2}"`
    build_size=$3
    index_dir="${output_dir}/${build_size}"

    pushd `pwd`
    mkdir -p ${index_dir}/origin && cd ${index_dir}/origin

    amq init

    /usr/bin/time -v amq build ${split_dir}/$build_size/main.fna \
        > "${index_dir}/build_time.log" 2> "${index_dir}/build_memory.log"

    echo $build_size-samples index built

    for add_size in 100 300 500 700 1000
    do
        cp -r "${index_dir}/origin" "${index_dir}/$add_size"
        pushd `pwd` && cd "${index_dir}/$add_size"
       
        to_add=$(find ${split_dir}/$build_size/additional -type l -exec readlink {} \; | shuf -n $add_size | xargs realpath)
        amq_source=`python -c "import amquery; print(amquery.__file__)"`
        amq_dir=`dirname ${amq_source}`

        /usr/bin/time -v amq add `echo ${to_add} | xargs` \
            > "${index_dir}/add_${add_size}_time.log" 2> "${index_dir}/add_${add_size}_memory.log"

        amq stats
        rm -r "${index_dir}/$add_size"
        echo $build_size: $add_size added

        popd
    done;

    popd
}


if [[ $# -ne 2 ]]; then
    echo "Usage: bash $0 <input-dir> <output-dir>"
else
    source `/usr/bin/which "virtualenvwrapper.sh"`
    workon amq-env

    for build_size in 100 300 500 700 1000
    do
        #run_amq_denovo $1 $2 $build_size
        run_amq_ref $1 $2 $build_size
        #run_amq $1 $2 $build_size
    done;
fi
