#!/bin/bash
#SBATCH --job-name=byd2pcf_cicconv
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_cicconv_%j.out
#SBATCH --error=results/slurm_cicconv_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/measure_cic_conventions.py --root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --nreal 10 --nmesh 64 --output results/cic_convention_audit_batch_${SLURM_JOB_ID}.json
