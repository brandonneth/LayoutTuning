import pandas as pd
import sys

if len(sys.argv) < 2:
	exit()

dataFilename = sys.argv[1]

with open(dataFilename, 'r') as d:
	df = pd.read_csv(dataFilename, dtype={'Phi': str, 'Ell' : str, 'Psi' : str, 'ExecPolPerm' : str})

print(df)


pv = pd.pivot_table(df, values='Time', index=['Size', 'ExecPolPerm'], columns=["Phi", 'Ell', "Psi"])

print('Pivoted:')
print(pv)

for s in [1,2,4]:
	df_t = df[df.Size == s].sort_values(['Time'])
	print("DF for s==",s)
	print(df_t)

