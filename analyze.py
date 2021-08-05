import pandas as pd
import sys

if len(sys.argv) < 2:
	print("First arg should be combined .csv")
	exit()

dataFilename = sys.argv[1]

with open(dataFilename, 'r') as d:
	df = pd.read_csv(dataFilename, dtype={'Phi': str, 'Ell' : str, 'Psi' : str, 'ExecPolPerm' : str})

print(df)


pv = pd.pivot_table(df, values='Time', index=['Size', 'ExecPolPerm'], columns=["Phi", 'Ell', "Psi"])

print('Pivoted:')
print(pv)

sizes = df['Size'].unique()

for s in sizes:
	df_t = df[df.Size == s].sort_values(['Time'])
	print("DF for s==",s)
	print(df_t)

sys.path.append("./AccessAnalysis")
import accessAnalysis



params = ['nm', 'd', 'g', 'z']
phi_access = ["nm", "g", "z"]
ell_access = ["nm", "d"]
psi_access = ["d", "g", "z"]


allExecPols = df['ExecPolPerm'].unique()
allPhi = df['Phi'].unique()
allEll = df['Ell'].unique()

kpols = list(map(lambda x : [int(y) for y in x], allExecPols))
phis = list(map(lambda x : [int(y) for y in x], allPhi))
ells = list(map(lambda x : [int(y) for y in x], allEll))
import itertools
layout_combos = list(itertools.product(phis, ells, phis))

scores = accessAnalysis.kernel_scores_dataframe(params, [phi_access,ell_access,psi_access], kpols, layout_combos, columns=['ExecPolPerm', 'Phi', 'Ell', 'Psi', 'Score'])

df_t = df.merge(scores)
print(df_t)


from plotnine import *

figure = (ggplot(df_t, aes('Score', 'Time', color='factor(Size)'))
	+ geom_point()
	+ stat_smooth(method='lm')
	+ facet_wrap('~Size', scales='free'))

print(figure)



