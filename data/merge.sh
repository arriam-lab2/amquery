
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

if [[ $# -ne 1 ]]; then
    echo "Usage: bash $0 <input-dir>"
else
    for build_size in {100..1000..100}
    do
        merge_fasta $1 ${build_size}
    done;
fi
