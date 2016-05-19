#!/bin/bash

dir=$1

for file in "$dir"/*; do
  echo $file
  dir=`dirname $file`
  name=`basename $file`
  shortname=${name%.*}
  extension="${file##*.}"

  line1=`sed -n "1 {p;q;}" $file`
  line3=`sed -n "3 {p;q;}" $file`

  # if the file contains only one fasta record
  length=`head -n 3 $file | wc -l`

  # fasta
  if [[ ($line1 == '>'*  && $line3 == '>'* && $extension != 'fasta') || $length < 3 ]]; then
      echo "Renaming $name"
      mv "$file" "$dir/$shortname.fasta"
  fi
done

echo "Done."
