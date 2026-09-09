#!/usr/bin/env python3
"""Assemble a leakage-free Stage 8 held-out validation report."""
import argparse,hashlib,json
from pathlib import Path
import yaml

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def nodes(d):
 x=d.get('nodes',{}); return x.items() if isinstance(x,dict) else ((v.get('node',str(i)),v) for i,v in enumerate(x))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); r=a.root
 cfgp=r/'configs/baseline_v1_canonical.yaml'; manp=r/'results/validation_manifest_v5.json'; guardp=r/'results/protocol_consistency_audit_v1.json'; cfg=yaml.safe_load(cfgp.read_text()); man=load(manp); guard=load(guardp)
 if guard.get('status')!='PASS': raise RuntimeError('canonical protocol guard is not PASS')
 sources={'mu1_universal_tree':'results/power_real_n100_n64/heldout_mu1_universal_p112_covariance_v2.json','mu1_training_ph':'results/mu1_training_ph_calibration_holdout_v2.json','mu2G_training_ph':'results/mu2_training_ph_calibration_holdout_v2.json','joint_mu1_mu2G':'results/joint_mu1_mu2G_holdout_validation_v1.json','mu2_png_response':'results/mu2_png_response_holdout_covariance_v1.json'}
 data={k:load(r/v) for k,v in sources.items()}
 summary={}
 for name in ['mu1_universal_tree','mu1_training_ph','mu2G_training_ph']:
  summary[name]={}
  for node,v in nodes(data[name]):
   summary[name][node]={'n_holdout':v.get('n_holdout',30),'chi2_dof':v.get('chi2_dof'),'hartlap_chi2_dof':v.get('hartlap_chi2_dof'),'rms_pull':v.get('rms_pull'),'coverage_abs_pull_le_2':v.get('coverage_abs_pull_le_2',v.get('coverage_fraction_abs_pull_le_2')),'covariance_condition_number':v.get('covariance_condition_number'),'covariance_estimator':v.get('covariance_estimator')}
 joint={}
 for node,v in nodes(data['joint_mu1_mu2G']): joint[node]={'n_holdout':v.get('n_holdout'),'dimension':v.get('dimension'),'hartlap_factor':v.get('hartlap_factor'),'hartlap_reason':v.get('hartlap_reason'),'shrinkage_scans':v.get('shrinkage_scans'),'coverage_fraction_abs_pull_le_2':v.get('coverage_fraction_abs_pull_le_2')}
 resp=data['mu2_png_response']['nodes']['LC_p_minus_LC_m']; response={k:{'rms_pull_vs_zero':v.get('rms_pull_vs_zero'),'hartlap_corrected_chi2_dof_vs_zero':v.get('hartlap_corrected_chi2_dof_vs_zero'),'large_scale_hartlap_corrected_chi2_dof_vs_zero':v.get('large_scale_hartlap_corrected_chi2_dof_vs_zero'),'coverage_abs_pull_le_2':v.get('coverage_abs_pull_le_2')} for k,v in resp.items()}
 out={'schema':'stage8_holdout_validation_report_v1','status':'REJECTED_DIAGNOSTIC','config':'configs/baseline_v1_canonical.yaml','config_sha256':sha(cfgp),'manifest':'results/validation_manifest_v5.json','manifest_sha256':sha(manp),'protocol_guard':'results/protocol_consistency_audit_v1.json','protocol_guard_sha256':sha(guardp),'holdout_ids':man['holdout_ids'],'n_holdout':len(man['holdout_ids']),'scales_mpc_h':cfg['s_mpc_h'],'nodes':cfg['nodes'],'summary':summary,'joint_mu1_mu2G':joint,'mu2_png_response_holdout':response,'source_sha256':{k:sha(r/v) for k,v in sources.items()},'policy':{'all_models_same_config_split_scales':True,'empirical_A_over_k2_plus_B_plus_Ck2':'diagnostic_only','heldout_realizations_not_used_for_calibration':True,'bphi_independent_provenance_required':True,'production_promotion':False,'failures_retained':True},'rejection_reasons':['universal and training-only μ1/μ2G diagnostics are not an independent production model','joint μ1+μ2G and PNG response residuals remain significant','independent b_phi and full connected halo four-point closure are unavailable']}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'n_holdout':out['n_holdout'],'source_count':len(sources)}))
if __name__=='__main__':main()

