import sys
import math

if len(sys.argv) != 3:
	print("Error: call program as find_timepoints.py data_file output_file")
	exit()

data_file = sys.argv[1]
output_file = sys.argv[2]

INFILE = open(data_file, "r")  # open the file specified by the value of arg1, to read from the file.
OUTFILE = open(output_file, "w")

lines = INFILE.read().splitlines()
for line in lines:
	data = line.split("=")
	if data[0].strip() == "*Time":
		OUTFILE.write(data[1].strip())
		OUTFILE.write('\n')

INFILE.close()
OUTFILE.close()