#!/bin/bash
#SBATCH --job-name=byd2pcf_b1full
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --chdir=/pscratch/sd/l/lzy/byd2pcf
#SBATCH --output=results/slurm_b1full_%j.out
#SBATCH --error=results/slurm_b1full_%j.err
set -euo pipefail
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/measure_fiducial_disjoint_power.py --catalog-root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --start 100 --stop 500 --nmesh 64 --output results/fiducial_disjoint_modepower_full_${SLURM_JOB_ID}.npz
python - <<'PY'
import hashlib,json,os,platform
from pathlib import Path
root=Path('/pscratch/sd/l/lzy/byd2pcf'); j=os.environ['SLURM_JOB_ID']; paths=[f'results/fiducial_disjoint_modepower_full_{j}.npz',f'results/fiducial_disjoint_modepower_full_{j}.json']; out={'schema':'slurm_disjoint_fiducial_full_provenance_v1','slurm_job_id':j,'state':'COMPLETED','exit_code':'0:0','hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':paths,'outputs_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},'realization_block':'fiducial real100-real499 disjoint from frozen real000-real099','scope':'Gaussian disjoint P_h normalization diagnostic; no PNG response fit'}; (root/f'results/slurm_b1full_provenance_{j}.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
PY
