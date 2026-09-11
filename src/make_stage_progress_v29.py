#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/stage_progress_v28.json').read_text());d['schema']='stage_progress_v29';d['github_main_commit']=a.commit;d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=d['stages']['0'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/validation_manifest_v6.json','results/validation_manifest_v6.json.sha256']));s['open']='frozen successor manifest v6 rebinds the protocol metadata to current GitHub main while preserving split, IDs, scales and checksums';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
