
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

function split {
    output_dir=$(mktemp -dp $3)

    shuffled_samples=($(ls -df ${1}/* | sort -R))
    len=$(ls ${1} | wc -l)
    additional_size=$(expr ${len} - ${2})

    to_build=$(printf '%s\n' "${shuffled_samples[@]}" | head -n ${2})
    to_add=$(printf '%s\n' "${shuffled_samples[@]}" | tail -n $additional_size)

    python ../amquery/utils/merge_fasta.py `echo ${to_build} | xargs` -o ${output_dir}/main.fna
    python ../amquery/utils/merge_fasta.py `echo ${to_add} | xargs` -o ${output_dir}/additional.fna
}


if [[ $# -ne 3 ]]; then
    echo "Usage: bash bench.sh <input-dir> <main-file-size> <output-dir>"
else
    split $1 $2 $3> /dev/null
    runqiime $output_dir
fi