#!/bin/bash
#SBATCH --job-name=byd2pcf_b1diag
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_b1diag_%j.out
#SBATCH --error=results/slurm_b1diag_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/derive_b1_nbody.py --nbody results/nbody_baseline_v1 --theory-table inputs/quijote_fiducial_z1_plin_pphi_M.dat --nmesh 64 --output results/fiducial_b1_nbody_diagnostic_batch_${SLURM_JOB_ID}.json
python src/compare_ph_cic_variants.py --nbody-dir results/nbody_baseline_v1 --theory-table inputs/quijote_fiducial_z1_plin_pphi_M.dat --b1 2.7340475186190334 --output results/ph_cic_variant_batch_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,platform
j=os.environ['SLURM_JOB_ID']; ps=[f'results/fiducial_b1_nbody_diagnostic_batch_{j}.json',f'results/ph_cic_variant_batch_{j}.json']
def h(p):
 x=hashlib.sha256(); x.update(open(p,'rb').read()); return x.hexdigest()
d={'schema':'slurm_b1_diagnostic_provenance_v1','slurm_job_id':j,'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':ps,'outputs_sha256':{p:h(p) for p in ps},'scope':'training-set b1(k) and CIC/no-CIC P_h diagnostics; no PNG response fit'}
json.dump(d,open(f'results/slurm_b1_provenance_{j}.json','w'),indent=2); print(json.dumps(d,indent=2))
PY
