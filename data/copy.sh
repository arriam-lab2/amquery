function copy_jsd {
    root=$1
    output=$2

    for split_no in 100 300 500 700 1000
    do
        mkdir -p ${output}/${split_no}
        scp nick@arriam-cpu:"${bench_root}/${bench_dir}/${split_no}/*.log" ${output}/${split_no}
        scp nick@arriam-cpu:"${bench_root}/${bench_dir}/${split_no}/p*.txt" ${output}/${split_no}
    done;
}

function copy_wu_ref {
    root=$1
    output=$2

    for split_no in 100 300 500 700 1000
    do
        mkdir -p ${output}/${split_no}
        scp nick@arriam-cpu:"${bench_root}/${bench_dir}/${split_no}/*.log" ${output}/${split_no}
        scp nick@arriam-cpu:"${root}/ref/time/picking/${split_no}.txt" \
            ${output}/${split_no}/prebuild_picking.log
        scp nick@arriam-cpu:"${root}/ref/time/make_table/${split_no}.txt" \
            ${output}/${split_no}/prebuild_otu.log
    done;
}

function copy_wu_denovo {
    root=$1
    output=$2

    for split_no in 100 300 500 700 1000
    do
        mkdir -p ${output}/${split_no}
        scp nick@arriam-cpu:"${bench_root}/${bench_dir}/${split_no}/*.log" ${output}/${split_no}
        scp nick@arriam-cpu:"${root}/denovo/time/picking/${split_no}.txt" \
            ${output}/${split_no}/prebuild_picking.log
        scp nick@arriam-cpu:"${root}/denovo/time/repset/${split_no}.txt" \
            ${output}/${split_no}/prebuild_repset.log
        scp nick@arriam-cpu:"${root}/denovo/time/aln/${split_no}.txt" \
            ${output}/${split_no}/prebuild_aln.log
        scp nick@arriam-cpu:"${root}/denovo/time/aln_filt/${split_no}.txt" \
            ${output}/${split_no}/prebuild_alnfilt.log
        scp nick@arriam-cpu:"${root}/denovo/time/tree/${split_no}.txt" \
            ${output}/${split_no}/prebuild_tree.log
        scp nick@arriam-cpu:"${root}/denovo/time/make_table/${split_no}.txt" \
            ${output}/${split_no}/prebuild_otu.log
    done;
}

if [[ $# < 1 ]]; then
    echo "Usage: bash [denovo, ref, jsd] $0 OUTPUT_DIR"
else
    root=/home/ilia/storage/metagen/bench
    bench_root=/home/nick/storage/amquery/data/
    output="${1}"

    while [[ $# -gt 1 ]]
    do
    key="$1"

    case $key in
        denovo)
        KEY=denovo
        output="${2}"
        shift
        ;;
        ref)
        KEY=ref
        output="${2}"
        shift
        ;;
        *)
        shift
        ;;
    esac
    done

    bench_dir="${output}"
    mkdir -p "${output}"
    
    if [[ "$KEY" == "denovo" ]]
    then
        copy_wu_denovo "${root}" "${output}"
    elif  [[ "$KEY" == "ref" ]]
    then
        copy_wu_ref "${root}" "${output}"
    else
        copy_jsd "${root}" "${output}"
    fi

fi
