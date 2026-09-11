#!/bin/bash
#SBATCH --job-name=byd2pcf_pngresp
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --output=results/slurm_pngresp_%j.out
#SBATCH --error=results/slurm_pngresp_%j.err
#SBATCH --chdir=/pscratch/sd/l/lzy/byd2pcf
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/measure_disjoint_png_moments.py --catalog-root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --output-root results/disjoint_png_moments_${SLURM_JOB_ID} --nodes LC_m LC_p --start 100 --stop 500 --nmesh 64
python src/fit_bphi_disjoint_response.py --moments-root results/disjoint_png_moments_${SLURM_JOB_ID} --input inputs/quijote_fiducial_z1_theory_lattice64.npz --b1 2.7317333004945543 --output results/bphi_disjoint_response_calibration_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,platform
from pathlib import Path
root=Path('/pscratch/sd/l/lzy/byd2pcf');j=os.environ['SLURM_JOB_ID']; paths=[f'results/disjoint_png_moments_{j}/disjoint_png_moments_v1.json',f'results/disjoint_png_moments_{j}/moments_LC_m_n64_disjoint.npz',f'results/disjoint_png_moments_{j}/moments_LC_p_n64_disjoint.npz',f'results/bphi_disjoint_response_calibration_{j}.json']; out={'schema':'slurm_bphi_disjoint_response_provenance_v1','slurm_job_id':j,'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':paths,'outputs_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},'realization_block':'LC_m/LC_p real100-real499 disjoint from frozen 70/30 split','scope':'independent bphi response calibration; no heldout response fit'}; (root/f'results/slurm_bphi_disjoint_response_provenance_{j}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
PY
