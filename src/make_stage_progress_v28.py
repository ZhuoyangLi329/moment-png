#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/stage_progress_v27.json').read_text());d['schema']='stage_progress_v28';d['github_main_commit']=a.commit;d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=d['stages']['7'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/primordial_mu2_trispectrum_component_audit_v2.json']));s['open']='finite-box zero-mode correction removes the collapsed internal zero-mode artifact, but the corrected local primordial component still has mean absolute MC pull≈3.86 and max≈7.41; halo bias/contact terms remain unmodeled';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
