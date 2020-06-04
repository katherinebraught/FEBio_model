#!/bin/bash

#updating timepoints: 5,10,15

#inputed variables
inputfile=$1
febioOut=$2

#other filenames
timepoints_data=timepoints_data
lifted_input=lift_$inputfile
modified_strain_values=mod_$febioOut
temp_input=new_model_$inputfile

#first step: run on inputfile to get a list of timepoints
echo creating lifted file
FEBio3 -i $inputfile
python find_timepoints.py $febioOut $timepoints_data


#for loop goes here
for timepoint in 5, 10, 15
do
#generate a model with lift from original inputfile
python create_mod_model.py $inputfile $lifted_input $timepoints_data $timepoint
#generate strain_data for modified file:
FEBio3 -i $lifted_input

echo removing time point
python remove_timepointdata.py $febioOut $modified_strain_values strain_values_output threashold_values_output $inputfile $temp_input $timepoint
FEBio3 -i $temp_input
done


