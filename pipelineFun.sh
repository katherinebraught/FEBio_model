#!/bin/bash

#updating timepoints: 5,10,15

#inputed variables
inputfile=$1
febioOut=$2

#other filenames
timepoints_data=timepoints_data
lifted_input=lift_$inputfile
modified_strain_values=mod_$febioOut
temp_input=temp_$inputfile
final_model=new_model_$inputfile
strain_values_output=strain_values_output.csv
prev_time=0

#clear strain_values_output so we can append to new file
rm -f $strain_values_output


#first step: run on inputfile to get a list of timepoints
echo creating lifted file
FEBio2 -i $inputfile > febio_output_t0
python find_timepoints.py $febioOut $timepoints_data

cp $inputfile $temp_input
#for loop goes here

for timepoint in 3000 6000 9000
do
#generate a model with lift from original inputfile
python create_mod_model.py $temp_input $lifted_input $timepoints_data $timepoint
#generate strain_data for modified file:
FEBio2 -i $lifted_input > febio_lifted_output_t$timepoint

echo removing time point $timepoint
python remove_timepointdata.py $febioOut $modified_strain_values $strain_values_output threashold_values_output $temp_input $final_model $timepoint $prev_time
FEBio2 -i $final_model > febio_output_t$timepoint
cp $final_model $temp_input
prev_time=$timepoint
done


