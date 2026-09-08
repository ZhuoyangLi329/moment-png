#!/bin/bash
#SBATCH --job-name=byd2pcf_resbatch
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_resbatch_%j.out
#SBATCH --error=results/slurm_resbatch_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
for n in 128 256; do
  out=results/resolution_batch_${SLURM_JOB_ID}_n${n}
  python src/batch_moments.py --root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --nreal 10 --nmesh ${n} --smin 40 --smax 300 --ds 20 --shell-width 20 --output ${out}
done
python - <<'PY'
import hashlib,json,os,platform
job=os.environ['SLURM_JOB_ID']; root='results'; outs=[]
for n in (128,256):
 p=f'results/resolution_batch_{job}_n{n}/summary.json'; outs.append(p)
def sha(p):
 h=hashlib.sha256(); h.update(open(p,'rb').read()); return h.hexdigest()
d={'schema':'slurm_resolution_provenance_v1','slurm_job_id':job,'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':outs,'outputs_sha256':{p:sha(p) for p in outs},'nreal':10,'scales':'40--300 step20','scope':'batch N-body moment generation at Ngrid 128 and 256'}
json.dump(d,open(f'results/slurm_resolution_provenance_{job}.json','w'),indent=2); print(json.dumps(d,indent=2))
PY
