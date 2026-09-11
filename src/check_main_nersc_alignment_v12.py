#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--previous',type=Path,required=True);ap.add_argument('--commit',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();old=json.loads(a.previous.read_text());extra={'src/freeze_manifest_v3.py','src/make_stage_progress_v29.py','src/check_main_nersc_alignment_v12.py','src/make_provenance_v85.py'};paths=sorted(set(x['path'] for x in old.get('files',[]))|extra);rows=[]
 for rel in paths:
  rp=a.repo/rel;np=a.root/rel;rh=sha(rp) if rp.exists() else None;nh=sha(np) if np.exists() else None;rows.append({'path':rel,'repo_sha256':rh,'nersc_sha256':nh,'match':bool(rh and nh and rh==nh)})
 out={'schema':'main_nersc_source_alignment_v12','status':'PASS' if all(x['match'] for x in rows) else 'BLOCKED','github_main_commit':a.commit,'n_files':len(rows),'n_matches':sum(x['match'] for x in rows),'n_mismatches':sum(not x['match'] for x in rows),'mismatches':[x for x in rows if not x['match']],'files':rows,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'n_files':len(rows),'mismatches':out['n_mismatches']}))
if __name__=='__main__':main()
