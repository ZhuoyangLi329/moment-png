#!/bin/bash
#SBATCH --job-name=byd2pcf_phresp
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --chdir=/pscratch/sd/l/lzy/byd2pcf
#SBATCH --output=results/slurm_phresp_%j.out
#SBATCH --error=results/slurm_phresp_%j.err
set -euo pipefail
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/fit_disjoint_measured_ph.py --power results/fiducial_disjoint_modepower_full_58195613.npz --moments-root results/disjoint_png_moments_58194794 --theory inputs/quijote_fiducial_z1_theory_lattice64.npz --output results/bphi_disjoint_measured_ph_diagnostic_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,platform
from pathlib import Path
root=Path('/pscratch/sd/l/lzy/byd2pcf'); j=os.environ['SLURM_JOB_ID']; p=f'results/bphi_disjoint_measured_ph_diagnostic_{j}.json'; out={'schema':'slurm_disjoint_measured_ph_provenance_v1','slurm_job_id':j,'state':'COMPLETED','exit_code':'0:0','hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'output':p,'output_sha256':hashlib.sha256((root/p).read_bytes()).hexdigest(),'power_job':58195613,'scope':'normalization diagnostic; not production'}; (root/f'results/slurm_phresp_provenance_{j}.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
PY
