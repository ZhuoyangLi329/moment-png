#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); r=a.root
 out=dict(load(r/'results/stage8_holdout_validation_report_v3.json')); out['schema']='stage8_holdout_validation_report_v4'; out['status']='REJECTED_DIAGNOSTIC'
 b1=load(r/'results/disjoint_fiducial_b1_fit_full_58196436.json'); gate=load(r/'results/stage2_disjoint_b1_gate_v1.json')
 out['disjoint_gaussian_b1_full_block']={'status':gate.get('status'),'nreal':b1.get('nreal'),'realization_block':b1.get('realization_block'),'kmax003_b1':b1['fits']['0.03']['b1'],'kmax003_chi2_dof':b1['fits']['0.03']['chi2_dof'],'training_b1_kmax003':gate.get('training_b1_kmax003'),'delta_b1_kmax003':gate.get('delta_b1_kmax003'),'tolerance':gate.get('predeclared_tolerance'),'lowk_consistency':gate.get('lowk_consistency'),'source_sha256':{'fit':sha(r/'results/disjoint_fiducial_b1_fit_full_58196436.json'),'gate':sha(r/'results/stage2_disjoint_b1_gate_v1.json')}}
 out['rejection_reasons']=list(dict.fromkeys(out.get('rejection_reasons',[])+['full disjoint fiducial b1 audit differs from the frozen training b1 by 0.08774 at kmax=.03, beyond the predeclared 0.02 tolerance']))
 out['source_sha256'].update({'stage8_v3':sha(r/'results/stage8_holdout_validation_report_v3.json'),'disjoint_b1_full':sha(r/'results/disjoint_fiducial_b1_fit_full_58196436.json'),'stage2_disjoint_b1_gate':sha(r/'results/stage2_disjoint_b1_gate_v1.json')})
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'b1_delta':out['disjoint_gaussian_b1_full_block']['delta_b1_kmax003']}))
if __name__=='__main__':main()
