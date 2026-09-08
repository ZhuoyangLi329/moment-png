#!/bin/bash
#SBATCH --job-name=byd2pcf_finaldiag
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_finaldiag_%j.out
#SBATCH --error=results/slurm_finaldiag_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/run_final_batch_diagnostics.py --root . --output results/final_batch_${SLURM_JOB_ID}
