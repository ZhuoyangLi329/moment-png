#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/stage_progress_v25.json').read_text());d['schema']='stage_progress_v26';d['github_main_commit']=a.commit;d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=d['stages']['2'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/b1_pshot_covariance_scan_v1.json']));s['open']='covariance-aware physical b1/Pshot scan gives full kmax=.03 chi2/dof≈99.12 with corr≈-0.999 and deteriorates at higher k; the earlier diagonal-fit low chi2 is not an acceptance result';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
