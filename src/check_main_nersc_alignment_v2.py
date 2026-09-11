#!/usr/bin/env python3
import argparse,datetime,hashlib,json,subprocess
from pathlib import Path
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--previous',type=Path,required=True);ap.add_argument('--commit',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args(); old=json.loads(a.previous.read_text()); paths=sorted(set(x['path'] for x in old.get('files',[]))|{'src/reconstruct_fof_positions.py','src/measure_disjoint_png_moments.py','src/fit_bphi_disjoint_response.py','src/inventory_bphi_disjoint_catalogs_v2.py','src/audit_bphi_disjoint_response.py','src/make_stage6_bphi_gate.py','src/make_stage_progress_v19.py','src/record_reconstruction_provenance.py','src/make_provenance_v69.py','src/make_provenance_v70.py','src/make_stage6_response_normalization_gate.py','src/fit_disjoint_measured_ph.py','src/check_main_nersc_alignment_v2.py','slurm/slurm_reconstruct_png.sbatch','slurm/slurm_pngresp.sbatch','slurm/slurm_bphirefit.sbatch','slurm/slurm_b1full.sbatch','slurm/slurm_phresp.sbatch'}); rows=[]
 for rel in paths:
  rp=a.repo/rel; np=a.root/rel; rh=sha(rp) if rp.exists() else None; nh=sha(np) if np.exists() else None; rows.append({'path':rel,'repo_sha256':rh,'nersc_sha256':nh,'match':bool(rh and nh and rh==nh)})
 out={'schema':'main_nersc_source_alignment_v2','status':'PASS' if all(x['match'] for x in rows) else 'BLOCKED','github_main_commit':a.commit,'n_files':len(rows),'n_matches':sum(x['match'] for x in rows),'n_mismatches':sum(not x['match'] for x in rows),'mismatches':[x for x in rows if not x['match']],'files':rows,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'n_files':len(rows),'mismatches':out['n_mismatches']}))
if __name__=='__main__':main()
