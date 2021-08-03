#!/bin/bash
#BSUB -nnodes 4

DATAPERMS3="012 021 102 120 201 210"
DATAPERMS2="01 10"
SIZES="1 2 4 8 16"
NPASSES=10

EXECUTABLE=RAJAPerf/build/bin/raja-perf.exe

for size in $SIZES
do
OUTDIR="size$size"
mkdir $OUTDIR
for phi_perm in $DATAPERMS3
do
	for ell_perm in $DATAPERMS2
	do
		for psi_perm in $DATAPERMS3
		do
			OUTFILE="LTIMES-$phi_perm-$ell_perm-$psi_perm"
                        KERNELS_FLAG="-k LTIMES"
			VARIANT_FLAG="-v DGZ DZG GDZ GZD ZDG ZGD" 
			OUTPUT_FLAG="-od $OUTDIR -of $OUTFILE"
			PERM_FLAG="--phi $phi_perm --ell $ell_perm --psi $psi_perm"
			SIZE_FLAG="--sizefact $size"
			NPASSES_FLAG="--npasses $NPASSES"
			FLAGS="$KERNELS_FLAG $VARIANT_FLAG $OUTPUT_FLAG $PERM_FLAG $SIZE_FLAG $NPASSES_FLAG"
			COMMAND="$EXECUTABLE $FLAGS"
			echo $COMMAND
			lrun -N1 -T1 $COMMAND &
		done
	done
done
done
wait
