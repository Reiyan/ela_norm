#!/bin/bash

# set the number of nodes
#SBATCH --nodes=1

# set the number of CPU cores per node
#SBATCH --ntasks-per-node=32

# How much memory is needed (per node)
#SBATCH --mem=128GB

# set max wallclock time
#SBATCH --time=3-12:00:00

# set partition
#SBATCH --partition=normal

# set name of job
#SBATCH --job-name=PLACEHOLDER_JOB_NAME

# mail alert at start, end and abortion of execution
#SBATCH --mail-type=END

# send mail to this address
#SBATCH --mail-user=raphael.prager@uni-muenster.de

# load modules
module add palma/2020b && module add GCCcore/10.2.0 && module add Python/3.8.6

# run the application
/home/r/r_prag01/ela_norm/venv/bin/python3 /home/r/r_prag01/ela_norm/01_run_experiment.py PLACEHOLDER_ARGS