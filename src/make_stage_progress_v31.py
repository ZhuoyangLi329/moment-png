#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/stage_progress_v30.json').read_text());d['schema']='stage_progress_v31';d['github_main_commit']=a.commit;d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=d['stages']['6'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/bphi_response_scale_window_scan_v1.json']));s['open']='a post hoc diagnostic scan finds a low-response-residual window at s=180--240 with bphi≈5.30, but this cannot retroactively change the frozen 40--300 cut; full-range shape remains rejected';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
