#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
def sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/run_provenance_v72.json').read_text());d['schema']='run_provenance_v73';d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['github_main_commit']=a.commit;d['source_alignment']='results/main_nersc_source_alignment_v33.json';d['source_alignment_sha256']=sha(r/'results/main_nersc_source_alignment_v33.json');d['batch_outputs']['source_alignment_v33']='results/main_nersc_source_alignment_v33.json';d['batch_outputs']['source_alignment_v33_sha256']=sha(r/'results/main_nersc_source_alignment_v33.json');d['batch_outputs']['release_gate_v45']='results/release_gate_v45.json';d['batch_outputs']['release_gate_v45_sha256']=sha(r/'results/release_gate_v45.json');d['status']='PARTIAL';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':d['status'],'commit':a.commit}))
if __name__=='__main__':main()
