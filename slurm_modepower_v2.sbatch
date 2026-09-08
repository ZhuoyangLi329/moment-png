#!/bin/bash
#SBATCH --job-name=byd2pcf_modepower_v2
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_modepower_v2_%j.out
#SBATCH --error=results/slurm_modepower_v2_%j.err
#SBATCH --export=ALL
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
: "${GITHUB_MAIN_COMMIT:?GITHUB_MAIN_COMMIT must be exported at submission}"
export PYTHONPATH=src
python src/measure_mode_power.py --root . --catalog-root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --output results/modepower_v2 --nmesh 64 --start 70 --stop 100
mkdir -p results/modepower_v2_batch_tmp
cp results/modepower_v2_fiducial_n64.npz results/modepower_v2_batch_tmp/modepower_fiducial_n64.npz
cp results/modepower_v2_LC_m_n64.npz results/modepower_v2_batch_tmp/modepower_LC_m_n64.npz
cp results/modepower_v2_LC_p_n64.npz results/modepower_v2_batch_tmp/modepower_LC_p_n64.npz
python src/validate_mu1_modewise_power.py --root . --mode-dir results/modepower_v2_batch_tmp --output results/mu1_modewise_power_identity_v2_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,socket,subprocess
root='/pscratch/sd/l/lzy/byd2pcf'; job=os.environ['SLURM_JOB_ID']
files=['configs/baseline_v1_frozen.yaml','results/validation_manifest_v4.json',f'results/mu1_modewise_power_identity_v2_{job}.json']
sha={p:hashlib.sha256(open(os.path.join(root,p),'rb').read()).hexdigest() for p in files}
prov={'schema':'modepower_batch_provenance_v2','slurm_job_id':job,'github_main_commit':os.environ['GITHUB_MAIN_COMMIT'],'hostname':socket.gethostname(),'account':'desi','qos':'shared','files_sha256':sha,'source':'src/validate_mu1_modewise_power.py','scope':'heldout exact-lattice CIC mode power to direct mu1 identity'}
open(os.path.join(root,f'results/modepower_batch_provenance_v2_{job}.json'),'w').write(json.dumps(prov,indent=2)+'\n')
PY
