#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); r=a.root
    out=json.loads((r/'results/stage8_holdout_validation_report_v6.json').read_text()); out['schema']='stage8_holdout_validation_report_v7'; out['status']='REJECTED_DIAGNOSTIC'
    cal=json.loads((r/'results/bphi_normalization_refit_58197556/calibration.json').read_text()); aud=json.loads((r/'results/bphi_disjoint_response_audit_v3_58197556.json').read_text()); shape=json.loads((r/'results/bphi_normalization_refit_58197556/shape_diagnostic.json').read_text())
    out['corrected_disjoint_bphi_refit']={'bphi_conditional':cal.get('bphi_conditional'),'sigma_statistical':cal.get('bphi_sigma_statistical_conditional'),'c_b1_times_bphi':cal.get('c_b1_times_bphi'),'chi2_dof':cal.get('fit',{}).get('chi2_dof'),'hartlap_chi2_dof':cal.get('fit',{}).get('hartlap_chi2_dof'),'audit_decision':aud.get('decision'),'shape_basis_stress_chi2_dof':{k:v.get('chi2_dof') for k,v in shape.get('fits',{}).items()},'source_sha256':{'calibration':sha(r/'results/bphi_normalization_refit_58197556/calibration.json'),'shape':sha(r/'results/bphi_normalization_refit_58197556/shape_diagnostic.json'),'run':sha(r/'results/bphi_normalization_refit_58197556/run_provenance.json'),'audit':sha(r/'results/bphi_disjoint_response_audit_v3_58197556.json'),'gate':sha(r/'results/stage6_bphi_disjoint_gate_v2.json')}}
    out['rejection_reasons']=list(dict.fromkeys(out.get('rejection_reasons',[])+['corrected disjoint bphi normalization is recorded, but the frozen external response template still fails chi2/dof=207.04','b1 uncertainty and b1-bphi cross-covariance remain unpropagated']))
    out['source_sha256'].update({'stage8_v6':sha(r/'results/stage8_holdout_validation_report_v6.json'),'corrected_bphi_calibration':sha(r/'results/bphi_normalization_refit_58197556/calibration.json'),'corrected_bphi_audit':sha(r/'results/bphi_disjoint_response_audit_v3_58197556.json'),'corrected_stage6_gate':sha(r/'results/stage6_bphi_disjoint_gate_v2.json')})
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'bphi':cal.get('bphi_conditional'),'chi2_dof':cal.get('fit',{}).get('chi2_dof')}))
if __name__=='__main__': main()
