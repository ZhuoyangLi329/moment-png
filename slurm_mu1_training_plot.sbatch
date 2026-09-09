#!/bin/bash
#SBATCH --job-name=byd2pcf_mu1plot
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --output=results/slurm_mu1plot_%j.out
#SBATCH --error=results/slurm_mu1plot_%j.err
#SBATCH --export=ALL
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
: "${GITHUB_MAIN_COMMIT:?GITHUB_MAIN_COMMIT must be exported at submission}"
export PYTHONPATH=src
python src/validate_mu1_training_power.py --root . --output results/mu1_training_ph_calibration_holdout_v1.json
python src/validate_mu2_training_power.py --root . --output results/mu2_training_ph_calibration_holdout_v1.json
python src/plot_mu1_mu2_training_bestfit.py
python - <<'PY'
import hashlib,json,os,platform
from pathlib import Path
root=Path('/pscratch/sd/l/lzy/byd2pcf'); job=os.environ['SLURM_JOB_ID']
files=['configs/baseline_v1_frozen.yaml','results/validation_manifest_v4.json','results/mu1_training_ph_calibration_holdout_v1.json','results/mu2_training_ph_calibration_holdout_v1.json','results/mu1_mu2_training_bestfit_vs_measured_symlog.pdf']
sha={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}
out={'schema':'mu1_training_plot_provenance_v1','slurm_job_id':job,'github_main_commit':os.environ['GITHUB_MAIN_COMMIT'],'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'files_sha256':sha,'scope':'training-only P_h calibration and held-out mu1 comparison figure','production_promotion':False}
(root/f'results/mu1_training_plot_provenance_{job}.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'PASS','job':job,'pdf_sha256':sha[files[-1]]}))
PY
