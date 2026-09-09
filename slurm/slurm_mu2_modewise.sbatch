#!/bin/bash
#SBATCH --job-name=byd2pcf_mu2mode
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:30:00
#SBATCH --output=results/slurm_mu2mode_%j.out
#SBATCH --error=results/slurm_mu2mode_%j.err
#SBATCH --export=ALL
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
: "${GITHUB_MAIN_COMMIT:?GITHUB_MAIN_COMMIT must be exported at submission}"
export PYTHONPATH=src
python src/validate_mu2_modewise_power.py --root . --mode-dir results --output results/mu2_modewise_power_identity_v2_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,socket
root='/pscratch/sd/l/lzy/byd2pcf'; job=os.environ['SLURM_JOB_ID']; out=f'results/mu2_modewise_power_identity_v2_{job}.json'
files=['configs/baseline_v1_frozen.yaml','results/validation_manifest_v4.json',out]
sha={p:hashlib.sha256(open(os.path.join(root,p),'rb').read()).hexdigest() for p in files}
prov={'schema':'mu2_modewise_batch_provenance_v1','slurm_job_id':job,'github_main_commit':os.environ['GITHUB_MAIN_COMMIT'],'hostname':socket.gethostname(),'account':'desi','qos':'shared','files_sha256':sha,'source':'src/validate_mu2_modewise_power.py','scope':'heldout full-lattice P_h to ensemble-centered Gaussian mu2 Wick identity; diagnostic only'}
open(os.path.join(root,f'results/mu2_modewise_batch_provenance_{job}.json'),'w').write(json.dumps(prov,indent=2)+'\n')
PY
