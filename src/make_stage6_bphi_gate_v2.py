#!/usr/bin/env python3
import argparse, datetime, hashlib, json
from pathlib import Path
def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--audit',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    d=json.loads(a.audit.read_text())
    chi=float(d.get('checks',[-1])[-1].get('chi2_dof',float('inf')) if d.get('checks') else d.get('chi2_dof',float('inf')))
    out={'schema':'stage6_bphi_disjoint_gate_v2','status':'BLOCKED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision':'NO_PRODUCTION_BPHI','audit':str(a.audit),'audit_sha256':sha(a.audit),'source_available':d.get('decision')=='CALIBRATION_SOURCE_AVAILABLE_SHAPE_REJECTED','nreal_pair':400,'conditional_bphi_corrected':d.get('bphi_conditional_corrected'),'conditional_sigma':d.get('bphi_sigma_statistical_conditional'),'chi2_dof':d.get('checks',[-1])[-1].get('chi2_dof') if d.get('checks') else None,'checks':{'disjoint_selection':'PASS' if d.get('source_available',True) else 'BLOCKED','paired_ids':'PASS' if any(x.get('name')=='paired_ids' and x.get('status')=='PASS' for x in d.get('checks',[])) else 'BLOCKED','response_shape':'PASS' if chi<=5 else 'BLOCKED','b1_uncertainty_and_cross_covariance':'BLOCKED'},'reasons':['corrected c=b1*bphi normalization is now recorded','external Pm/M response template remains rejected by the predeclared chi2/dof threshold','b1 uncertainty and b1-bphi cross-covariance remain unpropagated'],'policy':{'universal_p112_and_p100_remain_assumption_branches':True,'heldout_response_fit':False,'double_b1_division_corrected':True,'production_promotion':False}}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'bphi':out['conditional_bphi_corrected'],'chi2_dof':out['chi2_dof']}))
if __name__=='__main__':main()
