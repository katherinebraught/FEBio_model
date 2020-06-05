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
strain_values_output=strain_values_output
prev_time=0

#clear strain_values_output so we can append to new file
rm -f $strain_values_output


#first step: run on inputfile to get a list of timepoints
echo creating lifted file
FEBio3 -i $inputfile > febio_output_t0
python find_timepoints.py $febioOut $timepoints_data

cp $inputfile $temp_input
#for loop goes here

for timepoint in 3 5 7 9 11
do
#generate a model with lift from original inputfile
python create_mod_model.py $inputfile $lifted_input $timepoints_data $timepoint
#generate strain_data for modified file:
FEBio3 -i $lifted_input > febio_lifted_output_t$timepoint

echo removing time point $timepoint
python remove_timepointdata.py $febioOut $modified_strain_values $strain_values_output threashold_values_output $temp_input $final_model $timepoint $prev_time
FEBio3 -i $temp_input > febio_output_t$timepoint
cp $final_model $temp_input
prev_time=$timepoint
done


