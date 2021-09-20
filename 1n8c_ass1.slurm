#!/bin/bash
#SBATCH --partition=snowy
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --output=1n8c.out
#SBATCH --time=0-02:00:00

# Load required modules
module load foss/2019b
module load python/3.7.4

# Launch multiple process python code
time srun -n 8 python3 ass1.py
echo "1 node 8 cores"