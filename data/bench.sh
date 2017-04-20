
function runqiime {
    mainseq=${1}/main.fna
    addseq=${1}/additional.fna

    # initial pick
    pick_open_reference_otus.py -i ${mainseq} -o ${1}/mainotus/ --min_otu_size 1 
    # additional pick
    pick_open_reference_otus.py -i ${addseq} -o ${1}/addotus/ --min_otu_size 1 -r ${1}/mainotus/new_refseqs.fna --new_ref_set_id AdditionalOTU
    # merge OTU tables
    merge_otu_tables.py -i ${1}/mainotus/otu_table_mc1_w_tax_no_pynast_failures.biom,${1}/addotus/otu_table_mc1_w_tax_no_pynast_failures.biom -o ${1}/otu_table_w_tax_merged.biom
    # merge repsets
    python merge_repsets.py ${1}/mainotus/rep_set.fna ${1}/addotus/rep_set.fna ${1}/rep_set_merged.fna
    # align merged repset
    parallel_align_seqs_pynast.py -i ${1}/rep_set_merged.fna -o ${1}/aln/
    # filter alignment
    filter_alignment.py -i ${1}/aln/rep_set_merged_aligned.fasta -o ${1}/aln/
    # build repset phylogeny
    make_phylogeny.py -i ${1}/aln/rep_set_merged_aligned_pfiltered.fasta -o ${1}/rep_set_merged.tre
    # beta diversity main
    beta_diversity.py -i ${1}/otu_table_w_tax_merged.biom -o ${1}/bdiv -m weighted_unifrac -t ${1}/rep_set_merged.tre
}

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
