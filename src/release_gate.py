#!/usr/bin/env python3
"""Hard release gate: separate reproducible execution from scientific acceptance."""
import argparse,json
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
 checks.append({'name':'github_main_commit','status':'PASS' if prov and prov.get('github_main_commit') else 'BLOCKED','value':prov.get('github_main_commit') if prov else None})
 checks.append({'name':'batch_provenance','status':'PASS' if prov and len(prov.get('completed_batch_jobs',[]))>=8 else 'BLOCKED','value':prov.get('completed_batch_jobs',[]) if prov else []})
 checks.append({'name':'frozen_protocol','status':'PASS' if prov and prov.get('frozen_config') and prov.get('split') else 'BLOCKED'})
 align=read(r/'results/main_nersc_source_alignment_v1.json'); checks.append({'name':'source_alignment','status':'PASS' if align and align.get('status')=='PASS' and not align.get('mismatches') else 'BLOCKED'})
 stage=read(r/'results/stage_progress_v2.json'); stages=(stage or {}).get('stages',{}); scientific=[]
 for name in ['1','2','3','4','5','6','7','8']:
  status=stages.get(name,{}).get('status','MISSING'); checks.append({'name':f'stage_{name}','status':'PASS' if status=='PASS' else 'BLOCKED','stage_status':status});
  if status!='PASS': scientific.append({'stage':name,'status':status})
 out={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'BLOCKED','schema':'release_gate_v2','checks':checks,'scientific_blockers':scientific,'policy':'No production release while any stage is not PASS; diagnostics may be published with their failure labels.','scope':'release decision only; does not alter data or fit parameters'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'blocked':len(scientific)}))
if __name__=='__main__':main()
