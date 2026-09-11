#!/usr/bin/env python3
"""Record complete provenance for a completed reconstruction Slurm run."""
import argparse, datetime, hashlib, json, platform
from pathlib import Path

def sha(path):
 h=hashlib.sha256();
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''): h.update(block)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--job-id',required=True); ap.add_argument('--code-commit',required=True); ap.add_argument('--manifest',type=Path,required=True); ap.add_argument('--config',type=Path,required=True); ap.add_argument('--validation-manifest',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--node',required=True); ap.add_argument('--elapsed',required=True); ap.add_argument('--account',required=True); ap.add_argument('--qos',required=True); ap.add_argument('--partition',required=True); ap.add_argument('--cpus',type=int,required=True); ap.add_argument('--memory',required=True); a=ap.parse_args()
 m=json.loads(a.manifest.read_text()); out={'schema':'reconstruction_provenance_v2','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','repository':'ZhuoyangLi329/moment-png','github_ref':'main','github_main_commit':a.code_commit,'nersc_root':str(a.root),'slurm_job_id':int(a.job_id),'scheduler':'Slurm','state':'COMPLETED','exit_code':'0:0','resource':{'node':a.node,'elapsed':a.elapsed,'account':a.account,'qos':a.qos,'partition':a.partition,'cpus':a.cpus,'memory':a.memory},'frozen_config':str(a.config.relative_to(a.root)) if a.config.is_relative_to(a.root) else str(a.config),'frozen_config_sha256':sha(a.config),'validation_manifest':str(a.validation_manifest.relative_to(a.root)) if a.validation_manifest.is_relative_to(a.root) else str(a.validation_manifest),'validation_manifest_sha256':sha(a.validation_manifest),'input_root':m.get('input_root'),'input_scope':{'nodes':m.get('nodes'),'start':m.get('start'),'stop':m.get('stop'),'mass_threshold_msun_h':m.get('mass_threshold_msun_h'),'snapnum':m.get('snapnum'),'boxsize_mpc_h':m.get('boxsize_mpc_h')},'reconstruction_manifest':str(a.manifest.relative_to(a.root)) if a.manifest.is_relative_to(a.root) else str(a.manifest),'reconstruction_manifest_sha256':sha(a.manifest),'parser_sha256':m.get('parser_sha256'),'host_recorded':platform.node(),'policy':{'frozen_split_unchanged':True,'training_ids_excluded':True,'heldout_ids_excluded':True,'no_model_fit':True,'output_is_data_conversion':True}}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'job_id':out['slurm_job_id'],'commit':out['github_main_commit'],'manifest_sha256':out['reconstruction_manifest_sha256']}))
if __name__=='__main__': main()
