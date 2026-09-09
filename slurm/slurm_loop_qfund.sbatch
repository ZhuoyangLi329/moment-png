#!/bin/bash
#SBATCH --job-name=byd2pcf_loopqfund
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_loopqfund_%j.out
#SBATCH --error=results/slurm_loopqfund_%j.err
#SBATCH --export=ALL
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
: "${GITHUB_MAIN_COMMIT:?GITHUB_MAIN_COMMIT must be exported at submission}"
export PYTHONPATH=src
python src/compare_mu1_binned_loops.py --theory inputs/quijote_fiducial_z1_plin_pphi_M.dat --nmesh 64 --b1 2.7340475186190334 --b2 -0.665 --bK2 0.516666666666667 --bphi 5.44256823278338 --qmin 0.006283185307179586 --qmax 0.03 --nq 24 --nmu 24 --output results/loop_batch_${SLURM_JOB_ID}_qminfund.json
python - <<'PY'
import hashlib,json,os,platform
root='/pscratch/sd/l/lzy/byd2pcf'; job=os.environ['SLURM_JOB_ID']; p=f'results/loop_batch_{job}_qminfund.json'; h=hashlib.sha256(open(root+'/'+p,'rb').read()).hexdigest(); d={'schema':'slurm_loop_qfund_provenance_v1','slurm_job_id':job,'github_main_commit':os.environ['GITHUB_MAIN_COMMIT'],'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'output':p,'output_sha256':h,'nmesh':64,'qmin':2*3.141592653589793/1000.,'qmax':0.03,'nq':24,'nmu':24,'scope':'fundamental-mode IR cutoff diagnostic; no production promotion'}; json.dump(d,open(root+f'/results/slurm_loop_qfund_provenance_{job}.json','w'),indent=2); print(json.dumps(d))
PY
