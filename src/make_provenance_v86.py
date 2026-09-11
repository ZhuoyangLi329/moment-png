#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/run_provenance_v85.json').read_text());d['schema']='run_provenance_v86';d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['github_main_commit']=a.commit;d['validation_manifest']='results/validation_manifest_v7.json';d['validation_manifest_sha256']=sha(r/'results/validation_manifest_v7.json');d['stage_progress']='results/stage_progress_v30.json';d['stage_progress_sha256']=sha(r/'results/stage_progress_v30.json');d['batch_outputs']['validation_manifest_v7']='results/validation_manifest_v7.json';d['batch_outputs']['stage_progress_v30']='results/stage_progress_v30.json';d['status']='PARTIAL';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':d['status'],'commit':a.commit}))
if __name__=='__main__':main()
