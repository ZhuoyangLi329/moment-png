#!/usr/bin/env python3
"""Assemble Stage 8 report v2 with independent b1 and input covariance evidence."""
import argparse,hashlib,json
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); r=a.root
    base=load(r/'results/stage8_holdout_validation_report_v1.json')
    cov=load(r/'results/analytic_input_covariance_v2.json')
    b1=load(r/'results/disjoint_b1_consistency_audit_v1.json')
    b1job=load(r/'results/slurm_disjoint_b1_provenance_58104847.json')
    scope=load(r/'results/bphi_calibration_scope_audit_v1.json')
    lit=load(r/'results/bphi_literature_scope_audit_v1.json')
    out=dict(base)
    out['schema']='stage8_holdout_validation_report_v2'; out['status']='REJECTED_DIAGNOSTIC'
    out['input_uncertainty']={'source':'results/analytic_input_covariance_v2.json','status':cov.get('status'),'parameters':cov.get('input_parameters'),'mean':cov.get('input_mean'),'covariance':cov.get('input_covariance'),'derived_bphi':cov.get('derived_bphi'),'derived_bphi_sigma':cov.get('derived_bphi_sigma'),'derived_covariance_b1_bphi':cov.get('derived_covariance_b1_bphi'),'method':cov.get('method'),'scope':cov.get('scope')}
    out['independent_b1_audit']={'source':'results/disjoint_b1_consistency_audit_v1.json','status':b1.get('status'),'training_b1_kmax003':b1.get('training_b1_kmax003'),'disjoint_b1_kmax003':b1.get('fits',{}).get('0.03',{}).get('b1'),'delta_vs_training':b1.get('fits',{}).get('0.03',{}).get('delta_vs_training'),'criterion':b1.get('criterion'),'job_provenance':b1job}
    out['bphi_scope']={'local_scope_status':scope.get('status'),'local_strict_matches':scope.get('n_strict_matches'),'literature_status':lit.get('status'),'literature_strict_matches':lit.get('strict_match_count'),'decision':'BLOCKED'}
    out['source_sha256'].update({'input_covariance':sha(r/'results/analytic_input_covariance_v2.json'),'disjoint_b1_consistency':sha(r/'results/disjoint_b1_consistency_audit_v1.json'),'disjoint_b1_job':sha(r/'results/slurm_disjoint_b1_provenance_58104847.json'),'bphi_scope':sha(r/'results/bphi_calibration_scope_audit_v1.json'),'bphi_literature_scope':sha(r/'results/bphi_literature_scope_audit_v1.json'),'stage8_v1':sha(r/'results/stage8_holdout_validation_report_v1.json')})
    out['rejection_reasons']=list(dict.fromkeys(out.get('rejection_reasons',[])+['independent b1 passes only as a Gaussian audit; bphi remains uncalibrated for the frozen selection','input covariance is propagated but its bphi branch is assumption-only']))
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'n_holdout':out['n_holdout'],'derived_bphi':out['input_uncertainty']['derived_bphi'],'disjoint_b1_delta':out['independent_b1_audit']['delta_vs_training']}))
if __name__=='__main__': main()
