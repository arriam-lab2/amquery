function get_by_regex {
    filename="${1}"
    regex="${2}"
    
    while read line; do
        if [[ $line =~ $regex ]] ; then result=${BASH_REMATCH[1]}; fi                                                                                                 
    done < $filename
}

function get_time {
    regex="Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (.*)"
    get_by_regex "${1}" "${regex}"
}

function get_memory {
    regex="Maximum resident set size \(kbytes\): (.*)"
    get_by_regex "${1}" "${regex}"
}

function parse_results {
    input_dir="${1}"
    output_dir="${2}"

    build_time=$output_dir/build_time.txt
    build_memory=$output_dir/build_memory.txt
    rm -f $build_time $build_memory

    for build_size in 100 300 500 700 1000
    do
        index_dir="${input_dir}/${build_size}"

        # total build time
        build_files=(
            "${index_dir}"/prebuild_picking.log
            "${index_dir}"/prebuild_repset.log
            "${index_dir}"/prebuild_aln.log
            "${index_dir}"/prebuild_alnfilt.log
            "${index_dir}"/prebuild_tree.log
            "${index_dir}"/prebuild_otu.log
            "${index_dir}"/build_memory.log 
        )

        time_file=$(mktemp)
        memory_file=$(mktemp)
        for build_file in "${build_files[@]}"
        do
            if [ -f "${build_file}" ]; then
                get_time "${build_file}"
                seconds=`python time_convert.py $result`
                echo $seconds >> $time_file

                get_memory "${build_file}"
                mbytes=`python mem_convert.py $result`
                echo $mbytes >> $memory_file
            fi
        done
        echo `cat $time_file | xargs` >> $build_time
        echo `cat $memory_file | xargs` >> $build_memory
        rm $time_file $memory_file

        # update time
        for add_size in 100 300 500 700 1000
        do
            add_time_output=$output_dir/add_${add_size}_time.txt
            add_memory_output=$output_dir/add_${add_size}_memory.txt
            
            add_files=(
                "${index_dir}"/preadd_${add_size}_memory.log
                "${index_dir}"/add_${add_size}_memory.log
            )

            time_file=$(mktemp)
            memory_file=$(mktemp)
            for add_file in "${add_files[@]}"
            do
                if [ -f "${add_file}" ]; then
                    get_time "${add_file}"
                    seconds=`python time_convert.py $result`
                    echo $seconds >> $time_file

                    get_memory "${add_file}"
                    mbytes=`python mem_convert.py $result`
                    echo $mbytes >> $memory_file
                fi
            done;
            echo `cat $time_file | xargs` >> $add_time_output
            echo `cat $memory_file | xargs` >> $add_memory_output
            rm $time_file $memory_file
        done;
    done;
}

if [[ $# -ne 2 ]]; then
    echo "Usage: bash $0 INPUT_DIR OUTPUT_DIR"
else
    mkdir -p $2
    parse_results $1 $2
fi
