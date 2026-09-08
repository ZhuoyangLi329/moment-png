#!/bin/bash
#SBATCH --job-name=byd2pcf_mu2per
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_mu2per_%j.out
#SBATCH --error=results/slurm_mu2per_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/validate_mu2_perreal.py --root . --output results/mu2_gaussian_perrealization_identity_v1.json
