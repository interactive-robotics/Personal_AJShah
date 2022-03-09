#!/bin/bash

#SBATCH -n 32

#SBATCH --mem=4G

module load anaconda/2020.02
source /gpfs/runtime/opt/anaconda/3-5.2.0/etc/profile.d/conda.sh
conda activate lpopl
module load mpi/openmpi_4.0.5_gcc_10.2_slurm20 gcc/10.2 cuda/11.1.1

srun --mpi=pmix python -m mpi4py.futures mpi_test.py
