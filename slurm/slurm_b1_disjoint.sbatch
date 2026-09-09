#!/bin/bash
#SBATCH --job-name=byd2pcf_b1disj
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_b1disj_%j.out
#SBATCH --error=results/slurm_b1disj_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/measure_fiducial_disjoint_power.py --catalog-root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --start 100 --stop 200 --nmesh 64 --output results/fiducial_disjoint_modepower_${SLURM_JOB_ID}.npz
python - <<'PY'
import hashlib,json,os,platform
from pathlib import Path
j=os.environ['SLURM_JOB_ID'];root=Path('/pscratch/sd/l/lzy/byd2pcf'); paths=[f'results/fiducial_disjoint_modepower_{j}.npz',f'results/fiducial_disjoint_modepower_{j}.json']
def h(p): return hashlib.sha256((root/p).read_bytes()).hexdigest()
out={'schema':'slurm_disjoint_b1_provenance_v1','slurm_job_id':j,'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':paths,'outputs_sha256':{p:h(p) for p in paths},'realization_block':'fiducial real100-real199 disjoint from frozen real000-real099','scope':'Gaussian b1/P_h audit only; no PNG response fit'}
(root/f'results/slurm_disjoint_b1_provenance_{j}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
PY
