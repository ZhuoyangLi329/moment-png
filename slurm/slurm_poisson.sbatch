#!/bin/bash
#SBATCH --job-name=byd2pcf_poisson
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_poisson_%j.out
#SBATCH --error=results/slurm_poisson_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
for n in 128 256; do
 python src/poisson_control.py --nreal 10 --nhalo 195524 --nmesh ${n} --output results/poisson_control_batch_${SLURM_JOB_ID}_n${n}.npz
done
python - <<'PY'
import hashlib,json,os,platform
job=os.environ['SLURM_JOB_ID']; ps=[f'results/poisson_control_batch_{job}_n128.npz',f'results/poisson_control_batch_{job}_n256.npz']
def sha(p):
 h=hashlib.sha256(); h.update(open(p,'rb').read()); return h.hexdigest()
d={'schema':'slurm_poisson_provenance_v1','slurm_job_id':job,'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':ps,'outputs_sha256':{p:sha(p) for p in ps},'nreal':10,'nhalo':195524,'scales':'40--300 step20','scope':'independent iid Poisson contact control at nmesh 128/256'}
json.dump(d,open(f'results/slurm_poisson_provenance_{job}.json','w'),indent=2); print(json.dumps(d,indent=2))
PY
