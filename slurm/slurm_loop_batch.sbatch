#!/bin/bash
#SBATCH --job-name=byd2pcf_loopbatch
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_loopbatch_%j.out
#SBATCH --error=results/slurm_loopbatch_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
for qm in 0.0001 0.001; do
 tag=$(echo ${qm} | tr . p)
 python src/compare_mu1_binned_loops.py --theory inputs/quijote_fiducial_z1_plin_pphi_M.dat --nmesh 64 --b1 2.7340475186190334 --b2 -0.665 --bK2 0.516666666666667 --bphi 5.44256823278338 --qmin ${qm} --qmax 0.03 --nq 24 --nmu 24 --output results/loop_batch_${SLURM_JOB_ID}_qmin${tag}.json
done
python - <<'PY'
import hashlib,json,os,platform
job=os.environ['SLURM_JOB_ID']; ps=[f'results/loop_batch_{job}_qmin0p0001.json',f'results/loop_batch_{job}_qmin0p001.json']
def sha(p):
 h=hashlib.sha256(); h.update(open(p,'rb').read()); return h.hexdigest()
d={'schema':'slurm_loop_provenance_v1','slurm_job_id':job,'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':ps,'outputs_sha256':{p:sha(p) for p in ps},'nmesh':64,'qmax':0.03,'qmin_values':[0.0001,0.001],'nq':24,'nmu':24,'scope':'batch loop component calculation; no response fit'}
json.dump(d,open(f'results/slurm_loop_provenance_{job}.json','w'),indent=2); print(json.dumps(d,indent=2))
PY
