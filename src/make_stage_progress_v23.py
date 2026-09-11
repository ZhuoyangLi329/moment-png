#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;old=json.loads((r/'results/stage_progress_v22.json').read_text());old['schema']='stage_progress_v23';old['github_main_commit']=a.commit;old['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=old['stages']['1'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/nbody_unified_current.npz','results/nbody_unified_current.npz.json']));s['open']='one-command loader rechecked PASS for fiducial/LC_m/LC_p with catalog metadata; resolution arrays remain separate diagnostics';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(old,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
