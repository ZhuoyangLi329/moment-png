#!/usr/bin/env python3
import argparse, datetime, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--commit',required=True); a=ap.parse_args()
    r=a.root; d=json.loads((r/'results/stage_progress_v23.json').read_text()); d['schema']='stage_progress_v24'; d['github_main_commit']=a.commit; d['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    s=d['stages']['6']; s['status']='BLOCKED_DISJOINT_SHAPE'; s['evidence']=list(dict.fromkeys(s.get('evidence',[])+['results/bphi_normalization_refit_58197556/calibration.json','results/bphi_normalization_refit_58197556/shape_diagnostic.json','results/bphi_normalization_refit_58197556/run_provenance.json','results/bphi_disjoint_response_audit_v3_58197556.json','results/stage6_bphi_disjoint_gate_v2.json'])); s['open']='corrected c=b1*bphi refit gives conditional bphi=3.74848, but frozen external response shape remains rejected at chi2/dof=207.04; b1 uncertainty and cross-covariance remain open'
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(d,indent=2)+'\n'); print(json.dumps({'status':s['status'],'commit':a.commit}))
if __name__=='__main__': main()
