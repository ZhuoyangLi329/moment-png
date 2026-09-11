import argparse,datetime,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/run_provenance_v87.json').read_text());d['schema']='run_provenance_v88';d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['github_main_commit']=a.commit;d['source_alignment']='results/main_nersc_source_alignment_v46.json';d['source_alignment_sha256']=sha(r/'results/main_nersc_source_alignment_v46.json');d['completion_audit']='results/completion_audit_v1.json';d['completion_audit_sha256']=sha(r/'results/completion_audit_v1.json');d['batch_outputs']['source_alignment_v46']='results/main_nersc_source_alignment_v46.json';d['batch_outputs']['completion_audit']='results/completion_audit_v1.json';d['status']='PARTIAL';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'
');print(json.dumps({'status':d['status'],'commit':a.commit}))
if __name__=='__main__':main()
