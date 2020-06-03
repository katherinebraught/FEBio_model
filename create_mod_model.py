import sys
import math
#pip install xmltodict
import xmltodict

if len(sys.argv) != 4:
	print("Error: call program as create_mod_model.py input_feb_file output_feb_file time")
	exit()

input_feb = sys.argv[1]
modified_feb = sys.argv[2]
time = sys.argv[3]

with open(input_feb) as fd:
        data = xmltodict.parse(fd.read())
fd.close()

#modify curve
point = data['febio_spec']['LoadData']['loadcurve']['point'][1]
point = point.split(',')
x = float(point[0])
y = float(point[1])
new_y = y/x * float(time)
new_point = time + "," + str(new_y)

data['febio_spec']['LoadData']['loadcurve']['point'][1] = new_point

point = data['febio_spec']['LoadData']['loadcurve']['point'][2]
point = point.split(',')
x = point[0]
new_point = x + "," + str(new_y + new_y*0.01)

data['febio_spec']['LoadData']['loadcurve']['point'][2] = new_point

#modify output files

for element in data['febio_spec']['Output']['logfile']['element_data']:
	element['@file'] = "mod_" + element['@file']

	
OUT = open(modified_feb, "w") 

xml_data = xmltodict.unparse(data, pretty=True, short_empty_elements=True)
OUT.write(xml_data)
OUT.close()