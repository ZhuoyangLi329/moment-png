#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--commit',required=True); a=ap.parse_args(); r=a.root
 old=json.loads((r/'results/stage_progress_v19.json').read_text()); old['schema']='stage_progress_v20'; old['github_main_commit']=a.commit; old['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 s=old['stages']['2']; s['status']='DIAGNOSTIC_OPEN'; s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/disjoint_fiducial_b1_fit_full_58196436.json','results/slurm_b1fullfit_provenance_58196436.json','results/stage2_disjoint_b1_gate_v1.json'])); s['open']='full independent fiducial block is internally fit at kmax=.03 but b1 delta=-0.08774 exceeds the frozen 0.02 tolerance; higher-k drift and Pshot/cutoff coupling remain open'
 # stage8 references the new diagnostic report later
 old['policy']='No production claim while any stage remains OPEN, BLOCKED, ASSUMPTION_ONLY, or NOT_READY.'
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(old,indent=2)+'\n'); print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
