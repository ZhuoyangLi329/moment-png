#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/stage_progress_v24.json').read_text());d['schema']='stage_progress_v25';d['github_main_commit']=a.commit;d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 s=d['stages']['2'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/b1_bphi_crosscov_disjoint_audit_v1.json']));s['open']='joint b1/Pshot fits at kmax=.03 have large block uncertainty and chi2/dof 21--31; b1/Pshot degeneracy and nonlinear residual remain unresolved'
 s=d['stages']['6'];s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/b1_bphi_crosscov_disjoint_audit_v1.json']));s['open']='corrected bphi=3.74848 remains shape-rejected; block delta-method cross-covariance diagnostic gives sigma_bphi≈0.317 with corr(b1,c)≈-0.813, but four-block covariance is diagnostic only'
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':d['stages']['6']['status'],'commit':a.commit}))
if __name__=='__main__':main()
