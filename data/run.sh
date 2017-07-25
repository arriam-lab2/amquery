ref_input=16_07_17_ref
ref_output=out_ref
denovo_input=16_07_17_denovo
denovo_output=out_denovo
jsd_input=16_07_17_jsd
jsd_output=out_jsd
output=out

function download {
    [ ! -d $ref_input ] && bash copy.sh ref $ref_input
    [ ! -d $denovo_input ] && bash copy.sh denovo $denovo_input
    [ ! -d $jsd_input ] && bash copy.sh $jsd_input
}

function parse {
    rm -rf $ref_output && bash plots.sh $ref_input $ref_output
    rm -rf $denovo_output && bash plots.sh $denovo_input $denovo_output
    rm -rf $jsd_output && bash plots.sh $jsd_input $jsd_output
}

function merge_build {
    mkdir -p $output
    paste -d" " $jsd_output/build_time.txt \
                $ref_output/build_time.txt \
                $denovo_output/build_time.txt > $output/build_time.txt
    paste -d" " $jsd_output/build_memory.txt \
                $ref_output/build_memory.txt \
                $denovo_output/build_memory.txt > $output/build_memory.txt
}


function merge_add {
    
    for add_size in 100 300 500 700 1000
    do
        paste -d" " $jsd_output/add_${add_size}_time.txt \
                    $ref_output/add_${add_size}_time.txt \
                    $denovo_output/add_${add_size}_time.txt > $output/add_${add_size}_time.txt

        paste -d" " $jsd_output/add_${add_size}_memory.txt \
                    $ref_output/add_${add_size}_memory.txt \
                    $denovo_output/add_${add_size}_memory.txt > $output/add_${add_size}_memory.txt
    done

}

function cut_column {
    column=$1
    key=$2
    for build_size in 100 300 500 700 1000
    do
        cat $jsd_output/p_${build_size}_$key.txt | cut -d" " -f${column} > $jsd_output/$build_size
    done;
}

function merge_precision {
    for build_size in 100 300 500 700 1000
    do
        cat $jsd_input/${build_size}/p_denovo_1.txt $jsd_input/${build_size}/p_denovo_3.txt \
            $jsd_input/${build_size}/p_denovo_5.txt $jsd_input/${build_size}/p_denovo_7.txt \
            $jsd_input/${build_size}/p_denovo_10.txt $jsd_input/${build_size}/p_denovo_15.txt \
            $jsd_input/${build_size}/p_denovo_20.txt > $jsd_output/p_${build_size}_denovo.txt

        cat $jsd_input/${build_size}/p_ref_1.txt $jsd_input/${build_size}/p_ref_3.txt \
            $jsd_input/${build_size}/p_ref_5.txt $jsd_input/${build_size}/p_ref_7.txt \
            $jsd_input/${build_size}/p_ref_10.txt $jsd_input/${build_size}/p_ref_15.txt \
            $jsd_input/${build_size}/p_ref_20.txt > $jsd_output/p_${build_size}_ref.txt
    done;

    for key in denovo ref
    do
        cut_column 1 $key && paste -d" " $jsd_output/100 $jsd_output/300 $jsd_output/500 $jsd_output/700 $jsd_output/1000 > $output/p_$key.txt
        cut_column 2 $key && paste -d" " $jsd_output/100 $jsd_output/300 $jsd_output/500 $jsd_output/700 $jsd_output/1000 > $output/ap_$key.txt
        cut_column 3 $key && paste -d" " $jsd_output/100 $jsd_output/300 $jsd_output/500 $jsd_output/700 $jsd_output/1000 > $output/gain_$key.txt

        cut_column 4 $key && paste -d" " $jsd_output/100 $jsd_output/300 $jsd_output/500 $jsd_output/700 $jsd_output/1000 > $output/p_b_$key.txt
        cut_column 5 $key && paste -d" " $jsd_output/100 $jsd_output/300 $jsd_output/500 $jsd_output/700 $jsd_output/1000 > $output/ap_b_$key.txt
        cut_column 6 $key && paste -d" " $jsd_output/100 $jsd_output/300 $jsd_output/500 $jsd_output/700 $jsd_output/1000 > $output/gain_b_$key.txt
    done;
}

function merge_all {
    merge_build
    merge_add
    merge_precision
}

function create_tables {
    temp_file=$(mktemp)
    awk '{gsub(/ /,"\\&")}1' out/build_time.txt | cut -f1-4 -d'&' > $temp_file
    paste -d'&' $temp_file <(awk '{gsub(/ /,"+")}1' $ref_output/build_time.txt | bc) > $output/table1.txt

    awk '{gsub(/ /,"\\&")}1' out/build_time.txt | cut -f5-11 -d'&' > $temp_file
    paste -d'&' $temp_file <(awk '{gsub(/ /,"+")}1' $denovo_output/build_time.txt | bc) > $output/table2.txt

    awk '{gsub(/ /,"\\&")}1' out/build_memory.txt | cut -f1-4 -d'&' > $output/table3.txt
    awk '{gsub(/ /,"\\&")}1' out/build_memory.txt | cut -f5-11 -d'&' > $output/table4.txt
    rm $temp_file
}

function create_plots {
    Rscript plots.R
}

function main {
    download
    parse
    merge_all
    create_tables
    create_plots
}

main