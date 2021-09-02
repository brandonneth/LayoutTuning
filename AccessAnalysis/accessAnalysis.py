# Here we have the code that turns access information and execution policies into scored sets of permutations for the arrays.
# I'm porting this from Haskell, so i'm going to include the typing module

from typing import *
import itertools
import pandas as pd
LambdaParameters = List[str]
LayoutPolicy = List[int]
KernelPolicy = List[int]
AccessArguments = List[str]
StrideOrder = List[int]
AccessIndices = List[int]

#The input data is the access arguments for each access
#The input transformations (also sort of data) are the view's layout, the lambda paramaters, and the kernel policy
def apply_lambda(params: LambdaParameters, args: AccessArguments) -> AccessIndices:
	#apply_lambda args access = foldr (++) [] [elemIndices acc args | acc <- access]
	return [params.index(arg) for arg in args]


def apply_kpol(kpol: KernelPolicy, indicies: AccessIndices) -> StrideOrder:
	return [kpol.index(index) for index in indicies]


def apply_lpol(lpol: LayoutPolicy, l: List[Any]) -> List[Any]:
	assert len(lpol) == len(l)
	return [l[i] for i in lpol]

def score(stride: StrideOrder) -> int:
	if stride == []:
		return 0
	else:
		return len([x for x in stride[1:] if x < stride[0]]) + score(stride[1:])	

def access_to_score(params: LambdaParameters, args: AccessArguments, kpol: KernelPolicy, lpol: LayoutPolicy) -> int:
	return score(apply_kpol(kpol, apply_lpol(lpol, apply_lambda(params, args))))

def accesses_to_score(params: LambdaParameters, accesses: List[AccessArguments], kpol: KernelPolicy, lpols: List[LayoutPolicy], repeat_factor=[]) -> int:
	if repeat_factor == []:
		pass
	else:
		assert len(accesses) == len(repeat_factor)
		repeated_accesses = [list(itertools.repeat(access,factor)) for access,factor in zip(accesses,repeat_factor)]
		print(repeated_accesses)
		accesses = []
		for elem in repeated_accesses:
			accesses += elem

		repeated_lpols = [list(itertools.repeat(lpol,factor)) for lpol,factor in zip(lpols,repeat_factor)]
		print(repeated_lpols)
		lpols = []
		for elem in repeated_lpols:
			lpols += elem

		
	normalizedAccesses = [apply_lpol(lpol, access) for lpol,access in zip(lpols, accesses)]

	scores = [access_to_score(params, access, kpol, lpol) for access,lpol in zip(accesses, lpols)]
	return sum(scores)


#
# Tests
#

lambda_params = ["nm", "d", "g", "z"]

phi_access = ["nm", "g", "z"]
ell_access = ["nm", "d"]
psi_access = ["d", "g", "z"]

policy0 = [0,1,2,3]
policy1 = [0,2,3,1]
policy2 = [3,2,1,0]

phi_layout1 = [0,2,1]
ell_layout1 = [1,0]
psi_layout1 = [2,0,1]

phi_layout2 = [0,1,2]
ell_layout2 = [0,1]
psi_layout2 = [0,1,2]

accesses = [phi_access, ell_access, psi_access]
layouts1 = [phi_layout1, ell_layout1, psi_layout1]

print("apply_lambda tests")
assert([0,2,3] == apply_lambda(lambda_params, phi_access))
assert([0,1] == apply_lambda(lambda_params, ell_access))
assert([1,2,3] == apply_lambda(lambda_params, psi_access))

print("apply_kpol tests")
assert([0,1,2] == apply_kpol(policy1, apply_lambda(lambda_params, phi_access)))
assert([3,1,0] == apply_kpol(policy2, apply_lambda(lambda_params, phi_access)))
assert([0,3] == apply_kpol(policy1, apply_lambda(lambda_params, ell_access)))
assert([3,2] == apply_kpol(policy2, apply_lambda(lambda_params, ell_access)))
assert([3,1,2] == apply_kpol(policy1, apply_lambda(lambda_params, psi_access)))
assert([2,1,0] == apply_kpol(policy2, apply_lambda(lambda_params, psi_access)))

print("apply_lpol tests")
assert [0,2,1] == apply_lpol(phi_layout1, apply_kpol(policy1, apply_lambda(lambda_params, phi_access)))

print("score tests")
assert 0 == score([0,1,2])
assert 3 == score([2,1,0])
assert 5 == score([0,3,5,2,1])



print('starting score 1:', accesses_to_score(lambda_params, accesses, policy0, layouts1))

ltimes_kpols = [[0,2,1,3],[0,3,1,2],[2,0,1,3],[2,3,0,1], [3,0,1,2],[3,2,0,1]]


phi_layouts = itertools.permutations(range(0,3))
psi_layouts = itertools.permutations(range(0,3))
ell_layouts = [[0,1],[1,0]]

layout_combos = list(itertools.product(phi_layouts, ell_layouts, psi_layouts))
combos = list(itertools.product(ltimes_kpols, layout_combos))

print("All combos of execution policies and layouts")
print(list(combos))


all_scores = [accesses_to_score(lambda_params, accesses, policy, layouts) for (policy,layouts) in combos]

data = [[ ''.join([str(x) for x in policy])] + list(map((lambda l : ''.join([str(x) for x in l])), layouts)) + [score] for ((policy,layouts),score) in zip(combos,all_scores)]
print('data')
print(data)
header = ['ExecPolPerm', 'Phi', 'Ell', 'Psi', 'Score']

df = pd.DataFrame(data, columns=header)

print('dataframe:')
print(df)

def kernel_scores_dataframe(params: LambdaParameters, accesses: List[AccessArguments], all_kpols: List[KernelPolicy], all_lpols_combos: List[List[LayoutPolicy]], columns=[], repeat_factor=[]) -> pd.DataFrame:
	combos = list(itertools.product(all_kpols, all_lpols_combos))
	all_scores = [accesses_to_score(params, accesses, policy, layouts, repeat_factor=repeat_factor) for (policy, layouts) in combos]
	data = [[ ''.join([str(x) for x in policy])] + list(map((lambda l : ''.join([str(x) for x in l])), layouts)) + [score] for ((policy,layouts),score) in zip(combos,all_scores)]
	return pd.DataFrame(data, columns=columns)


print("dataframe from func")
print(kernel_scores_dataframe(lambda_params, accesses, ltimes_kpols, layout_combos, columns=header))

