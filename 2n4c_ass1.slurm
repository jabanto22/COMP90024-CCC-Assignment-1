#!/bin/bash
#SBATCH --partition=snowy
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --output=2n4c.out
#SBATCH --time=0-02:00:00

# Load required modules
module load foss/2019b
module load python/3.7.4

# Launch multiple process python code
time srun -n 8 python3 ass1.py
echo "2 nodes 4 cores"