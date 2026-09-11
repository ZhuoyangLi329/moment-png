#!/bin/bash
#SBATCH --job-name=byd2pcf_reconpng
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --output=results/slurm_reconpng_%j.out
#SBATCH --error=results/slurm_reconpng_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/reconstruct_fof_positions.py --input-root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1 --output-root /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions --nodes LC_m LC_p --start 100 --stop 500 --mass-threshold 1e13 --snapnum 2 --boxsize 1000 --manifest results/reconstruct_png_catalogs_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,platform
from pathlib import Path
root=Path('/pscratch/sd/l/lzy/byd2pcf'); j=os.environ['SLURM_JOB_ID']; p=root/f'results/reconstruct_png_catalogs_{j}.json'
out=json.loads(p.read_text()); out['slurm_job_id']=j; out['hostname']=platform.node(); out['account']=os.environ.get('SLURM_JOB_ACCOUNT'); out['qos']=os.environ.get('SLURM_JOB_QOS'); out['partition']=os.environ.get('SLURM_JOB_PARTITION'); out['cpus']=os.environ.get('SLURM_CPUS_PER_TASK'); out['manifest_sha256']=hashlib.sha256(p.read_bytes()).hexdigest(); (root/f'results/slurm_reconstruct_png_provenance_{j}.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'slurm_job_id':j,'rows':len(out['rows']),'manifest_sha256':out['manifest_sha256']}))
PY
