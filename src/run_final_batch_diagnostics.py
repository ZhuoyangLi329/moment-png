#!/usr/bin/env python3
import argparse,hashlib,json,os,platform,subprocess
from pathlib import Path

def run(cmd):
    subprocess.run(cmd,check=True)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path('/pscratch/sd/l/lzy/byd2pcf')); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    inp=a.root/'inputs/quijote_fiducial_z1_theory_lattice64.npz'; bias=a.root/'configs/bias_inputs_v1_pklinear_kmax008.yaml'; sh='40,60,80,100,120,140,160,180,200,220,240,260,280,300'
    for shot,tag in [(0,'0'),(5114.24,'5114p24'),(3603,'3603')]:
      for fnl in (-100,0,100):
        run(['python','src/theory_mu1_marisa_b.py',str(inp),'--bias',str(bias),'--bphi-universal','--fNL',str(fnl),'--pshot',str(shot),'--cell','15.625','--shells',sh,'--output',str(a.output/f'mu1_shot_{tag}_fnl{fnl}.json')])
    run(['python','src/theory_mu2_halo_analytic.py',str(a.root/'inputs/quijote_fiducial_z1_theory.npz'),'--b1','2.7813407736','--pshot','3603','--nmesh','64','--cic','--shells',sh,'--width','20','--output',str(a.output/'mu2_gaussian_analytic_mesh.json')])
    run(['python','src/validate_mu1_shotnoise_variants.py','--prediction-dir',str(a.output),'--moments-dir',str(a.root/'results/power_real_n100_n64'),'--output',str(a.output/'mu1_shot_noise_variant_audit.json')])
    run(['python','src/validate_mu2_gaussian_analytic.py','--prediction',str(a.output/'mu2_gaussian_analytic_mesh.json'),'--data-root',str(a.root/'results/resolution_clean'),'--output',str(a.output/'mu2_gaussian_validation.json')])
    run(['python','src/validate_joint_mu1_mu2.py','--data-root',str(a.root/'results/power_real_n100_n64'),'--mu1-dir',str(a.output),'--mu2-prediction',str(a.output/'mu2_gaussian_analytic_mesh.json'),'--output',str(a.output/'joint_mu1_mu2G_validation.json')])
    files=[p for p in a.output.rglob('*') if p.is_file()]
    out={'schema':'final_batch_diagnostics_provenance_v1','slurm_job_id':os.environ.get('SLURM_JOB_ID'),'hostname':platform.node(),'account':os.environ.get('SLURM_JOB_ACCOUNT'),'qos':os.environ.get('SLURM_JOB_QOS'),'partition':os.environ.get('SLURM_JOB_PARTITION'),'cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'output_dir':str(a.output),'files_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'scope':'batch regeneration of tree mu1 shot variants, mesh Gaussian mu2, and heldout joint diagnostics','production_promotion':False}
    (a.output/'provenance.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','job':out['slurm_job_id'],'files':len(files)}))
if __name__=='__main__': main()
