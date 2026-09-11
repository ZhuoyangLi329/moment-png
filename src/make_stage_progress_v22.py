#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;old=json.loads((r/'results/stage_progress_v21.json').read_text());old['schema']='stage_progress_v22';old['github_main_commit']=a.commit;old['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=old['stages']['2'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['src/fit_disjoint_fiducial_b1_v2.py','results/disjoint_fiducial_b1_fit_full_refit_v2.json','results/stage2_disjoint_b1_gate_v2.json']));s['open']='corrected full-block metadata gives b1 delta=-0.08774 at kmax=.03; block variance remains heterogeneous and Pshot/cutoff coupling unresolved';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(old,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()

