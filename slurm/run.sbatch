#!/bin/bash
# Generic compute-node wrapper:  sbatch slurm/run.sbatch python scripts/measure.py --node fiducial ...
#SBATCH --job-name=momentpng
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=results/slurm/%x_%j.out
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "${SLURM_SUBMIT_DIR}"
export PYTHONPATH="${SLURM_SUBMIT_DIR}"
echo "job ${SLURM_JOB_ID} on $(hostname) at $(git rev-parse --short HEAD): $*"
"$@"
