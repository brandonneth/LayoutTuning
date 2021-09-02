# Given a directory of RAJAPerf output files, checks that the checksum values are valid and then combines all the performance data into a single csv file.

# Use: python3 check-and-combine.py OutputFile [directories with result files]



import sys
import os
import string

import pandas as pd

#returns True if the checksums are all the same, False otherwise
def is_valid_run(checksumFilename, numVariants):
	with open(checksumFilename, "r") as f:
		lines = f.readlines()
		linesToCheck=lines[-(numVariants+2):-2]
		for line in linesToCheck:
			if line.split()[-1] != "0.0000000000000000000":
				return False
	return True

#extracts the variant name and execution time for thewith data in the csv file passed
def extract_variant_time_pairs(timingFilename):
	with open(timingFilename, 'r') as f:
		lines = f.readlines()
		variantLine = lines[1]
		timeLine = lines[2]
		variants = [variant.strip() for variant in variantLine.split(',')[1:]]
		times = [time.strip() for time in timeLine.split(',')[1:]]
		pairs = [p for p in zip(variants, times)]
	return pairs

def variant_to_perm(v):
	if v == "DGZ":
		return "0213"
	elif v == "DZG":
		return "0312"
	elif v == "GDZ":
		return "2013"
	elif v == "GZD":
		return "2301"
	elif v == "ZGD":
		return "3012"
	elif v == "ZDG":
		return "3201"
	else:
		return "INVALID VARIANT NAME" + v



if len(sys.argv) < 3:
	exit()

outputFilename = sys.argv[1]
resultDirs=sys.argv[2:]


data = []
for resultDir in resultDirs:
	print("Extracting results from ", resultDir)
	
	files = os.listdir(resultDir)
	
	print("Creating list of runs")
	runs = {"-".join(f.split("-")[:-1]) for f in files}
	print("Runs:")
	print(runs)
	invalid=[]
	valid=[]	
	for run in runs:
		checksumFilename = os.path.join(resultDir,run) + "-checksum.txt"
		if is_valid_run(checksumFilename, 6):
			valid.append(run)
		else:
			invalid.append(run)	
	valid.sort()
	invalid.sort()
	print("Valid Runs:")
	for run in valid:
		print(run)
	print("Invalid Runs:")
	for run in invalid:
		print(run)

	for v in valid:
		parts = v.split('-')
		kernel = parts[0]
		phi = parts[1]
		ell = parts[2]
		psi = parts[3]
		
		size = os.path.split(resultDir)[-1].strip('size')

		print("kernel:", kernel)
		print("phi, ell, psi:", phi, ell, psi)
		print('size:', size)
		
		timingFilename = os.path.join(resultDir,v) + "-timing.csv"
		variantsAndTimes = extract_variant_time_pairs(timingFilename)
		print('v and t:', variantsAndTimes)
		for variant,time in variantsAndTimes:
			datapoint = [kernel,variant_to_perm(variant),phi,ell,psi,size,time]
			data.append(datapoint)

columnNames=["Kernel","ExecPolPerm", "Phi", "Ell", "Psi", "Size", "Time"]
print(data)


df = pd.DataFrame(data=data, columns=columnNames)
print(df)

with open(outputFilename, 'w') as out:
	df.to_csv(out, index=False)
