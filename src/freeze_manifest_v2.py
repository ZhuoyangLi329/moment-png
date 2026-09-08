#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path

def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--commit',required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); parent=a.root/'results/validation_manifest_v1.json'; d=json.loads(parent.read_text()); d['schema']='validation_manifest_v2'; d['parent_manifest_sha256']=sha(parent); d['github_release_commit']=a.commit; d['protocol_sha256']=sha(a.root/'configs/validation_v1.yaml'); d['frozen_at']='2026-09-09'; d['status']='FROZEN'; d['manifest_policy']='v1 parent remains immutable; v2 rebases only repository commit metadata, split and measurement definitions are unchanged'; a.output.write_text(json.dumps(d,indent=2)+'\n'); (a.output.with_suffix(a.output.suffix+'.sha256')).write_text(sha(a.output)+'  '+str(a.output)+'\n'); print(json.dumps({'status':'PASS','sha256':sha(a.output),'parent':d['parent_manifest_sha256'],'commit':a.commit}))
if __name__=='__main__':main()
