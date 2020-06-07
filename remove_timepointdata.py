
# The following python script takes in an ouput file from FeBIO containing a list of Ex and Ey strain values
# at each time point, calculates the corresponding area stretch, then outputs a list of elements with their 
# corresponding area stretch if the value is above the prescribed threshold. 

# RUNNING THE SCRIPT 
# To run the script in terminal, navigate to the folder the contains the output file from FeBIO with Ex and Ey data
# at each element and time point. Enter the following command in the terminal: 
# python extract.py FeBIO_Output_File_Name.txt Script_Output_1.txt Script_Output_2.txt

#test git commands

import sys
import math
#pip install xmltodict
import xmltodict
import collections 

THRESHHOLD = 1.21 #Set area stretch threshold here 

#takes in values as float
def area_stretch(Ex, Ey):
	return math.sqrt(2*(Ex)+1) * math.sqrt(2*(Ey)+1) #Set equation for area stretch based on component x and y strains here 

#takes in values as string
def line_string(time, elnum, Ex, Ey, total_area, growth_area, elastic_stretch):
	return time + "," + elnum + "," + Ex + "," + Ey + "," + total_area + "," + growth_area + "," + elastic_stretch + "\n"

def headings():
	return "Time,Element,Ex,Ey,Total Area Strech,Growth Area Strech,Elastic Area Stretch\n"
  
def find_strain_values_for_final_timepoint(data_no_lift):
	values = []
	for line in data_no_lift:
		data = line.split(",")
		if len(data)> 1:
			stretch =  area_stretch(float(data[1]), float(data[2]))
			values.append(stretch)
		else:
			data = line.split("=")
			if data[0].strip() == "*Time":
				values = []
	return values

#timepoint and starting_timepoint are 0 indexed
def threshold_and_strain_data(infile, input_with_lift, outfile, threshholdvaluefile, timepoint, starting_timepoint):
	INFILE = open(infile, "r")  # open the file specified by the value of arg1, to read from the file.
	INFILE_WITH_LIFT = open(input_with_lift, "r")  # open the file specified by the value of arg1, to read from the file.
	OUT = open(outfile, "a")	 # open the file specified by the value of arg2, to write to the file.
	THRESHHOLD_F = open(threshholdvaluefile, "w")
	

	# Read data
	data_no_lift = INFILE.read().splitlines()
	data_with_lift = INFILE_WITH_LIFT.read().splitlines()
	growth_strain = find_strain_values_for_final_timepoint(data_with_lift)
	time = 0

	##add headings
	OUT.write(headings())
	THRESHHOLD_F.write("Time,Element\n")
	threshhold_values = []
	time_list = []
	found_time = False
	
	time_index=0
	growth_strain_index = 0
	for line in data_no_lift:
		data = line.split(",")
		if len(data)> 1:
			total_stretch= area_stretch(float(data[1]), float(data[2])) 
			growth_stretch = growth_strain[growth_strain_index]
			stretch =  total_stretch / growth_stretch
			growth_strain_index+=1
			if time_index >= starting_timepoint and time_index <= timepoint:
				OUT.write(line_string(str(time), data[0], data[1], data[2],str(total_stretch),str(growth_stretch), str(stretch)))
			if stretch > THRESHHOLD:
				THRESHHOLD_F.write(str(time) + "," + data[0] + "\n")
				time_list.append(data[0])
		else:
			data = line.split("=")
			if data[0].strip() == "*Time":
				if found_time:
					threshhold_values.append((time, time_list))
					time_list = []
					time_index+=1
				time = float(data[1].strip())
				found_time = True
				growth_strain_index = 0
	#append final timepoint
	threshhold_values.append((time, time_list))

	INFILE.close()
	OUT.close()
	THRESHHOLD_F.close()

	print("Output files written to " + outfile + "with data for timepoints " + str(starting_timepoint+1) + " to " + str(timepoint+1) + " and " + threshholdvaluefile)
	
	return threshhold_values
	
def export_new_FEB_file(inputfile, outputfile, elements_to_remove, time):
	#read input file
	OUT = open(outputfile, "w") 
	with open(inputfile) as fd:
		data = xmltodict.parse(fd.read())
	fd.close()
	#save a copy of the xml data before changes
	xml_data = xmltodict.unparse(data, pretty=True, short_empty_elements=True)

	#file for debug only
	comp_OUT = open("test.unmod.out", "w") 
	original_xml_data = xmltodict.unparse(data, pretty=True)
	comp_OUT.write(xml_data)
	comp_OUT.close()
	
	new_parts = []
	new_materials = []
	#modify input data
	#for each part
	added=0
	for part in data['febio_spec']['Geometry']['Elements']:
		#if name has mucosa
		if 'Mucosa' in part['@name']:
			new_part = part.copy()
			new_part['elem'] = []
			removed_element = False
			#remove all the elements from the part and the elements to remove
			for element in part['elem']:
				if element['@id'] in elements_to_remove:
					removed_element = True
					part['elem'].remove(element)
					elements_to_remove.remove(element['@id'])
					new_part['elem'].append(element)
					
			#if we removed anything
			if removed_element:
				#finish seting up the new material and part
				new_material = {}
				old_material = {}
				max_id = 0
				for mat in data['febio_spec']['Material']['material']:
					if int(mat['@id']) > max_id:
						max_id = int(mat['@id'])
					if mat['@name'] == part['@name']:
						new_material = mat.copy()
						old_material = mat
						
				
				#update names
				new_material['@name'] = new_material['@name'] + "-" + time
				new_part['@name'] = new_part['@name'] + "-" + time
			
				#add a generation
				#print("pre condition: adding generation to existing generation " + new_material['generation'] + '\n')
				new_material['generation'] = new_material['generation'].copy()
				if isinstance(new_material['generation'],list):
					new_material['generation'].append(new_material['generation'][0].copy())
				else:
					new_material['generation'] = [new_material['generation'], new_material['generation'].copy()]
				
				new_material['generation'][len(new_material['generation']) -1]['start_time'] = time
				#print("post: added generation to existing generation " + new_material['generation'] + '\n')

				
				#if we did not remove all the elements:
				if len(part['elem']) != 0:
					print(str(max_id))
					#append the copy of material and add a generation (check if list or item)
					added+=1
					new_id = str(max_id + added)
					new_material['@id'] = new_id
					new_part['@mat'] = new_id
					
					new_parts.append(new_part.copy())
					new_materials.append(new_material.copy())
					
				#if did remove all the elements
				else:
					#set the old material and element as the new material/generation
					old_material = new_material
					part = new_part
				
	#update dictionary
	for mat in new_materials:
		data['febio_spec']['Material']['material'].append(mat)
	for part in new_parts:
		data['febio_spec']['Geometry']['Elements'].append(part)
	
	
	#write to output file
	xml_data = xmltodict.unparse(data, pretty=True, short_empty_elements=True)
	OUT.write(xml_data)
	OUT.close()
	
	

if len(sys.argv) != 9:
	print("Error: call program as extract.py strain_values_from_febio strain_values_with_lift outputfile threshhold_elements febioInputFile newfebioInputFileName timepoint previous_timepoint")
	exit()

inputfile = sys.argv[1]
input_with_lift = sys.argv[2]
outputfile = sys.argv[3]
areastrainElementsFile = sys.argv[4]
FEB_in = sys.argv[5]#"test.in"
FEB_out = sys.argv[6]#"test.feb"
TIMEPOINT = int(sys.argv[7]) - 1
PREVIOUS_TIMEPOINT = int(sys.argv[8])


threshhold_elements = threshold_and_strain_data(inputfile, input_with_lift, outputfile, areastrainElementsFile+sys.argv[7], TIMEPOINT, PREVIOUS_TIMEPOINT)

print(threshhold_elements)	  

export_new_FEB_file(FEB_in, FEB_out, threshhold_elements[int(TIMEPOINT)][1], str(threshhold_elements[int(TIMEPOINT)][0]))
