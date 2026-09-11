#!/usr/bin/env python3
"""Create an immutable manifest successor without changing split or protocol."""
import argparse,datetime,hashlib,json
from pathlib import Path
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--commit',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();d=json.loads(a.parent.read_text());d['schema']='validation_manifest_v3';d['parent_manifest']=str(a.parent);d['parent_manifest_sha256']=sha(a.parent);d['github_release_commit']=a.commit;d['frozen_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['status']='FROZEN';d['manifest_policy']='Immutable successor of the prior manifest; split, IDs, scales, config and observable definitions are byte-for-byte inherited; only release commit and parent provenance are updated.';d['successor_reason']='Rebind frozen protocol metadata to current GitHub main after audited diagnostic commits without changing validation data or cuts.';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');(a.output.with_suffix(a.output.suffix+'.sha256')).write_text(sha(a.output)+'  '+str(a.output)+'\n');print(json.dumps({'status':'PASS','sha256':sha(a.output),'commit':a.commit,'parent_sha256':d['parent_manifest_sha256']}))
if __name__=='__main__':main()
