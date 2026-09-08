#!/bin/bash
#SBATCH --job-name=byd2pcf_identity
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=results/slurm_identity_%j.out
#SBATCH --error=results/slurm_identity_%j.err
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /pscratch/sd/l/lzy/byd2pcf
export PYTHONPATH=src
python src/validate_mu1_measured_power.py --root . --output results/mu1_from_measured_ph_validation_batch_${SLURM_JOB_ID}.json
python src/validate_mu2_measured_power.py --root . --output results/mu2_gaussian_from_measured_ph_validation_batch_${SLURM_JOB_ID}.json
python src/analyze_mu2_png_response_components.py --root . --output results/mu2_png_response_component_audit_batch_${SLURM_JOB_ID}.json
python src/analyze_halo_contact_excess.py --root . --output results/halo_contact_excess_audit_batch_${SLURM_JOB_ID}.json
python - <<'PY'
import hashlib,json,os,platform
j=os.environ['SLURM_JOB_ID']; ps=[f'results/mu1_from_measured_ph_validation_batch_{j}.json',f'results/mu2_gaussian_from_measured_ph_validation_batch_{j}.json',f'results/mu2_png_response_component_audit_batch_{j}.json',f'results/halo_contact_excess_audit_batch_{j}.json']
def h(p):
 x=hashlib.sha256(); x.update(open(p,'rb').read()); return x.hexdigest()
d={'schema':'slurm_identity_audit_provenance_v1','slurm_job_id':j,'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'outputs':ps,'outputs_sha256':{p:h(p) for p in ps},'scope':'batch measured-P_h identities, paired PNG response, and halo contact excess diagnostics'}
json.dump(d,open(f'results/slurm_identity_provenance_{j}.json','w'),indent=2); print(json.dumps(d,indent=2))
PY
