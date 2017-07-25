ref_input=16_07_17_ref
ref_output=out_ref
denovo_input=16_07_17_denovo
denovo_output=out_denovo
jsd_input=16_07_17_jsd
jsd_output=out_jsd
output=out

# dowload results
[ ! -d $ref_input ] && bash copy.sh ref $ref_input
[ ! -d $denovo_input ] && bash copy.sh denovo $denovo_input
[ ! -d $jsd_input ] && bash copy.sh $jsd_input

# parse output files
rm -rf $ref_output && bash plots.sh $ref_input $ref_output
rm -rf $denovo_output && bash plots.sh $denovo_input $denovo_output
rm -rf $jsd_output && bash plots.sh $jsd_input $jsd_output

# merge results
mkdir -p $output
paste -d" " $jsd_output/build_time.txt \
            $ref_output/build_time.txt \
            $denovo_output/build_time.txt > $output/build_time.txt
paste -d" " $jsd_output/build_memory.txt \
            $ref_output/build_memory.txt \
            $denovo_output/build_memory.txt > $output/build_memory.txt

for add_size in 100 300 500 700 1000
do
    paste -d" " $jsd_output/add_${add_size}_time.txt \
                $ref_output/add_${add_size}_time.txt \
                $denovo_output/add_${add_size}_time.txt > $output/add_${add_size}_time.txt

    paste -d" " $jsd_output/add_${add_size}_memory.txt \
                $ref_output/add_${add_size}_memory.txt \
                $denovo_output/add_${add_size}_memory.txt > $output/add_${add_size}_memory.txt
done


# latex tables
temp_file=$(mktemp)
awk '{gsub(/ /,"\\&")}1' out/build_time.txt | cut -f1-4 -d'&' > $temp_file
paste -d'&' $temp_file <(awk '{gsub(/ /,"+")}1' $ref_output/build_time.txt | bc) > $output/table1.txt

awk '{gsub(/ /,"\\&")}1' out/build_time.txt | cut -f5-11 -d'&' > $temp_file
paste -d'&' $temp_file <(awk '{gsub(/ /,"+")}1' $denovo_output/build_time.txt | bc) > $output/table2.txt

awk '{gsub(/ /,"\\&")}1' out/build_memory.txt | cut -f1-4 -d'&' > $output/table3.txt
awk '{gsub(/ /,"\\&")}1' out/build_memory.txt | cut -f5-11 -d'&' > $output/table4.txt
rm $temp_file

# plots
Rscript plots.R