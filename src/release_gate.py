#!/usr/bin/env python3
"""Hard release gate: separate reproducible execution from scientific acceptance."""
import argparse,json,re
from pathlib import Path

def read(p):
 try:return json.loads(p.read_text())
 except Exception:return None

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path('.')); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); r=a.root; checks=[]
 prov=None
 for p in sorted(r.glob('results/run_provenance_v*.json'), key=lambda p:int(p.stem.split('_v')[-1]), reverse=True):
  prov=read(p)
  if prov is not None: break
 commit=(prov or {}).get('github_main_commit','')
 checks.append({'name':'github_main_commit','status':'PASS' if re.fullmatch(r'[0-9a-f]{7,40}',str(commit)) else 'BLOCKED','value':commit or None})
 jobs=(prov or {}).get('completed_batch_jobs',[])
 checks.append({'name':'batch_provenance','status':'PASS' if len(jobs)>=8 and all(str(x).isdigit() for x in jobs) else 'BLOCKED','value':jobs})
 checks.append({'name':'frozen_protocol','status':'PASS' if prov and prov.get('frozen_config') and prov.get('split') and prov.get('protocol') else 'BLOCKED'})
 latest=(prov or {}).get('latest_job',{})
 resource_ok=bool(latest.get('slurm_job_id') and latest.get('state')=='COMPLETED' and latest.get('exit_code') in ('0:0','0') and latest.get('node') and latest.get('cpus') and latest.get('memory'))
 checksum_ok=all(re.fullmatch(r'[0-9a-f]{64}',str((prov or {}).get(k,''))) for k in ('frozen_config_sha256','manifest_sha256'))
 checks.append({'name':'provenance_fields','status':'PASS' if resource_ok and checksum_ok else 'BLOCKED','resource_record':resource_ok,'checksum_record':checksum_ok})
 manifests=sorted(r.glob('results/validation_manifest_v*.json'),key=lambda p:int(p.stem.split('_v')[-1]),reverse=True)
 manifest=read(manifests[0]) if manifests else None
 nodes=(manifest or {}).get('nodes',{})
 split_ok=bool(manifest and manifest.get('status')=='FROZEN' and set(nodes)=={'fiducial','LC_m','LC_p'} and all(v.get('n')==100 and len(v.get('ids',[]))==100 for v in nodes.values()))
 checks.append({'name':'immutable_validation_manifest','status':'PASS' if split_ok else 'BLOCKED','manifest':str(manifests[0]) if manifests else None})
 align_path=next((p for p in (r/'results/main_nersc_source_alignment_v3.json',r/'results/main_nersc_source_alignment_v2.json',r/'results/main_nersc_source_alignment_v1.json') if p.exists()),None); align=read(align_path) if align_path else None; checks.append({'name':'source_alignment','status':'PASS' if align and align.get('status')=='PASS' and not align.get('mismatches') else 'BLOCKED','evidence':str(align_path) if align_path else None})
 stage=read(r/'results/stage_progress_v2.json'); stages=(stage or {}).get('stages',{}); scientific=[]
 for name in ['1','2','3','4','5','6','7','8']:
  status=stages.get(name,{}).get('status','MISSING'); checks.append({'name':f'stage_{name}','status':'PASS' if status=='PASS' else 'BLOCKED','stage_status':status})
  if status!='PASS': scientific.append({'stage':name,'status':status})
 out={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'BLOCKED','schema':'release_gate_v3','checks':checks,'scientific_blockers':scientific,'policy':'No production release while any stage is not PASS; diagnostics may be published with their failure labels.','scope':'release decision only; does not alter data or fit parameters'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'blocked':len(scientific),'execution_checks':sum(x['status']=='PASS' for x in checks)}))
if __name__=='__main__':main()
