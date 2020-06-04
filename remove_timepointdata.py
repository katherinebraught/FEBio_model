
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

THRESHHOLD = 1.21 #Set area stretch threshold here 

#takes in values as float
def area_stretch(Ex, Ey):
	return math.sqrt(2*(Ex)+1) * math.sqrt(2*(Ey)+1) #Set equation for area stretch based on component x and y strains here 

#takes in values as string
def line_string(time, elnum, Ex, Ey, stretch):
	return time + "," + elnum + "," + Ex + "," + Ey + "," + stretch + "\n"

def headings():
	return "Time,Element,Ex,Ey,Area_Strain\n"
  
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

def threshold_and_strain_data(infile, input_with_lift, outfile, threshholdvaluefile):
	INFILE = open(infile, "r")  # open the file specified by the value of arg1, to read from the file.
	INFILE_WITH_LIFT = open(input_with_lift, "r")  # open the file specified by the value of arg1, to read from the file.
	OUT = open(outfile, "w")	 # open the file specified by the value of arg2, to write to the file.
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

	growth_strain_index = 0
	for line in data_no_lift:
		data = line.split(",")
		if len(data)> 1:
			stretch =  area_stretch(float(data[1]), float(data[2])) / growth_strain[growth_strain_index]
			growth_strain_index+=1
			OUT.write(line_string(str(time), data[0], data[1], data[2],str(stretch)))
			if stretch > THRESHHOLD:
				THRESHHOLD_F.write(str(time) + "," + data[0] + "\n")
				time_list.append(data[0])
		else:
			data = line.split("=")
			if data[0].strip() == "*Time":
				time = float(data[1].strip())
				if found_time:
					threshhold_values.append((time, time_list))
					time_list = []
				found_time = True
				growth_strain_index = 0


	INFILE.close()
	OUT.close()
	THRESHHOLD_F.close()

	print("Output files written to " + outfile + " and " + threshholdvaluefile)
	
	return threshhold_values
	
def export_new_FEB_file(inputfile, outputfile, elements_to_remove, time):
	#read input file
	OUT = open(outputfile, "w") 
	with open(inputfile) as fd:
		data = xmltodict.parse(fd.read())
	fd.close()
	comp_OUT = open("test.unmod.out", "w") 
	xml_data = xmltodict.unparse(data, pretty=True)
	comp_OUT.write(xml_data)
	comp_OUT.close()
	
	#modify input data
	
	#make new material
	materials = data['febio_spec']['Material']['material']
	#copy mucosa
	new_muc = {}#materials['Mucosa']
	max_id = 0
	for mat in materials:
		if int(mat['@id']) > max_id:
			max_id = int(mat['@id'])
		if mat['@name'] == 'Mucosa':
			new_muc = mat.copy()
	#update id - check num of materials and add 1
	new_id = str(max_id + 1)
	new_muc['@id'] = new_id
	#update name "Mucosa+timepoint"
	new_name = 'Mucosa' + time
	new_muc['@name'] = new_name
   #remove extra generations and update start time
	new_muc['generation'] = [new_muc['generation'][0].copy(), new_muc['generation'][0].copy()]
	new_muc['generation'][1]['start_time'] = time
	new_muc['generation'][0]['start_time'] = '0'
	#add to dictionary
	data['febio_spec']['Material']['material'].append(new_muc)
	
	
	#look through the <Elements type="hex8" mat="2" name="Mucosa"> and remove each item in elements
	elements = (data['febio_spec']['Geometry']['Elements'])
	mucosa = []
	new_elements = elements
	new_muc_element = {}
	for element in elements:
		if element['@name'] == 'Mucosa':
			mucosa = element
			elements.remove(element)
			new_muc_element = element.copy()
	
	#make new element
	new_muc_element['@mat'] = new_id
	new_muc_element['@name'] = "el_" + new_name
	new_muc_element['elem'] = []
	
	#remove elements elements to remove
	for element in mucosa['elem']:
	   # print(type(element))
	   # print((element))
	   # print('\n\n')
	   # print(type(element['@id']))
		if element['@id'] in elements_to_remove:
			mucosa['elem'].remove(element)
			new_muc_element['elem'].append(element)
			
			
	#update dictionary
	new_elements.append(mucosa)
	new_elements.append(new_muc_element)
	data['febio_spec']['Geometry']['Elements'] = new_elements
	
	
	
	#write to output file
	xml_data = xmltodict.unparse(data, pretty=True, short_empty_elements=True)
	OUT.write(xml_data)
	OUT.close()
	

	

if len(sys.argv) != 8:
	print("Error: call program as extract.py strain_values_from_febio strain_values_with_lift outputfile areastrainElementsFile febioInputFile newfebioInputFileName timepoint")
	exit()

inputfile = sys.argv[1]
input_with_lift = sys.argv[2]
outputfile = sys.argv[3]
areastrainElementsFile = sys.argv[4]
FEB_in = sys.argv[5]#"test.in"
FEB_out = sys.argv[6]#"test.feb"
TIMEPOINT = sys.argv[7]


threshhold_elements = threshold_and_strain_data(inputfile, input_with_lift, outputfile, areastrainElementsFile)

#print(threshhold_elements)	  

export_new_FEB_file(FEB_in, FEB_out, threshhold_elements[int(TIMEPOINT)][1], str(threshhold_elements[int(TIMEPOINT)][0]))
