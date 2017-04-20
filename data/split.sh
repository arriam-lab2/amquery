function split {
    input_dir="${1}"
    pattern="${3}"
    build_size="${4}"
    output_dir="${2}/${build_size}"
    mkdir -p "${output_dir}"

    len=$(find ${input_dir} -type f -name "${pattern}" | wc -l)
    [ $len -lt $build_size ] && rm -r "${output_dir}" && \
        echo "Couldn't create $build_size split: too few files found ($len)" && return

    shuffled_samples=($(find ${input_dir} -type f -name "${pattern}" | sort -R))
    additional_size=$(expr ${len} - ${build_size})
    [ $additional_size -le 0 ] && additional_size=0

    to_build=$(printf '%s\n' "${shuffled_samples[@]}" | head -n ${build_size})
    to_add=$(printf '%s\n' "${shuffled_samples[@]}" | tail -n ${additional_size})

    main_output_subdir="${output_dir}/main"
    additional_output_subdir="${output_dir}/additional"

    mkdir -p "${main_output_subdir}"
    mkdir -p "${additional_output_subdir}"

    echo "${to_build}" | xargs ln -s -t "${main_output_subdir}"
    [ $additional_size -gt 0 ] && echo "${to_add}" | xargs ln -s -t "${additional_output_subdir}"
    
    #python ../amquery/utils/merge_fasta.py `echo ${to_build} | xargs` -o ${output_dir}/main.fna
    #python ../amquery/utils/merge_fasta.py `echo ${to_add} | xargs` -o ${output_dir}/additional.fna
}


if [[ $# -ne 2 ]]; then
    echo "Usage: bash split.sh <input-dir> <output-dir>"
else
    pattern='*.fasta'

    for build_size in {100..1000..100}
    #for build_size in {10..20..5}
    do
        split "${1}" "${2}" "${pattern}" "${build_size}"
    done
fi
