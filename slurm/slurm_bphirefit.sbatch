#!/bin/bash
#SBATCH --job-name=byd2pcf_bphirefit
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:20:00
#SBATCH --chdir=/pscratch/sd/l/lzy/byd2pcf
#SBATCH --output=results/slurm_bphirefit_%j.out
#SBATCH --error=results/slurm_bphirefit_%j.err
set -euo pipefail
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/fit_bphi_disjoint_response.py --moments-root results/disjoint_png_moments_58194794 --input inputs/quijote_fiducial_z1_theory_lattice64.npz --b1 2.7317333004945543 --output results/bphi_disjoint_response_calibration_v3_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,platform
from pathlib import Path
root=Path('/pscratch/sd/l/lzy/byd2pcf'); j=os.environ['SLURM_JOB_ID']; paths=[f'results/disjoint_png_moments_58194794/disjoint_png_moments_v1.json',f'results/disjoint_png_moments_58194794/moments_LC_m_n64_disjoint.npz',f'results/disjoint_png_moments_58194794/moments_LC_p_n64_disjoint.npz',f'results/bphi_disjoint_response_calibration_v3_{j}.json']; out={'schema':'slurm_bphi_disjoint_response_provenance_v2','slurm_job_id':j,'state':'COMPLETED','exit_code':'0:0','hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':paths,'outputs_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},'source_code_commit':'f66d8d1','response_source_job':58194794,'scope':'corrected independent bphi response refit; no heldout response fit'}; (root/f'results/slurm_bphirefit_provenance_{j}.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
PY
