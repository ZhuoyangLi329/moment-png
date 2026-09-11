#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root; old=json.loads((r/'results/stage_progress_v20.json').read_text()); old['schema']='stage_progress_v21';old['github_main_commit']=a.commit;old['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=old['stages']['2'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/disjoint_b1_block_variance_audit_v1.json']));s['open']='full disjoint b1 delta=-0.08774 is driven by heterogeneous 100-realization blocks (b1≈2.7317,2.5451,2.7382,2.5591); realization-block variance and Pshot/cutoff coupling remain unresolved';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(old,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
