#!/usr/bin/env python3
"""Consolidate predeclared Stage 4 loop cutoff scans."""
import argparse,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=a.root
 qmax=json.loads((r/'results/mu1_loop_qmax_validation_v1.json').read_text()); qmin=json.loads((r/'results/loop_ir_cutoff_fundamental_audit_v1.json').read_text()); comp=json.loads((r/'results/loop_component_nbody_validation_qfund_58097316.json').read_text())
 qmax_score={k:sum(v[n]['rms_pull_s40_s80'] for n in ['fiducial','LC_m','LC_p'])/3 for k,v in qmax['results'].items()}
 out={'schema':'stage4_loop_cutoff_gate_v1','status':'BLOCKED','nmesh':64,'qmax_scan':{'source':'results/mu1_loop_qmax_validation_v1.json','runs':qmax['runs'],'mean_rms_pull_s40_s80':qmax_score,'raw':qmax['results']},'qmin_scan':{'source':'results/loop_ir_cutoff_fundamental_audit_v1.json','cutoff_runs':qmin['cutoff_runs'],'comparisons':qmin['comparisons']},'nbody_validation':{'source':'results/loop_component_nbody_validation_qfund_58097316.json','nodes':comp['nodes']},'selection_policy':{'qmax_tested':[0.03,0.05,0.08],'qmin_tested':[0.0001,0.001,2*3.141592653589793/1000.],'quadrature_nq':24,'quadrature_nmu':24,'same_bias_inputs':True,'production_promotion':False},'conclusion':'qmax=0.03 is the least discrepant tested UV cutoff but remains a diagnostic choice: qmin sensitivity is material and qfund heldout chi2/dof remains 162.3, 374.6, 69.2; no loop cutoff is promoted.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print({'status':out['status'],'qmax_score':qmax_score})
if __name__=='__main__':main()
