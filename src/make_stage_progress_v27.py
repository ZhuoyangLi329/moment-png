#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--commit',required=True);a=ap.parse_args();r=a.root;d=json.loads((r/'results/stage_progress_v26.json').read_text());d['schema']='stage_progress_v27';d['github_main_commit']=a.commit;d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();s=d['stages']['2'];s['open']='sorted-lattice covariance-aware b1/Pshot scan gives chi2/dof=1.14,3.21,2.08,2.48,218.23 for kmax=.03,.05,.08,.10,.15; low-k is a diagnostic candidate but high-k nonlinear failure, b1/Pshot degeneracy and training/disjoint calibration mismatch remain open';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__':main()
