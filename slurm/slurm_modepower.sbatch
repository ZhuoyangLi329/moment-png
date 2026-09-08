#!/bin/bash
#SBATCH --job-name=byd2pcf_modepower
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_modepower_%j.out
#SBATCH --error=results/slurm_modepower_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/measure_mode_power.py --root . --catalog-root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --output results/modepower --nmesh 64 --start 70 --stop 100
mkdir -p results/modepower_batch_tmp
cp results/modepower_fiducial_n64.npz results/modepower_batch_tmp/modepower_fiducial_n64.npz
cp results/modepower_LC_m_n64.npz results/modepower_batch_tmp/modepower_LC_m_n64.npz
cp results/modepower_LC_p_n64.npz results/modepower_batch_tmp/modepower_LC_p_n64.npz
python src/validate_mu1_modewise_power.py --root . --mode-dir results/modepower_batch_tmp --output results/mu1_modewise_power_identity_v1.json
