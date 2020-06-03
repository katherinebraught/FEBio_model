#!/bin/bash

inputfile=$1
febioOut=$2

febio2 -i $1

python remove_timepointdata.py $2 strain_$2 threshhold_values$2 $inputfile intermed_$inputfile 8

febio2 -i intermed_$inputfile

python remove_timepointdata.py $2 strain_$2 threshhold_values$2 intermed_$inputfile final_$inputfile 9

febio2 -i final_$inputfile
