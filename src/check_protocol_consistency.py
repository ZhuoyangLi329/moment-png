#!/usr/bin/env python3
"""Validate the immutable v1 configuration and manifest as one protocol."""
import argparse, hashlib, json
from pathlib import Path
import yaml
EXPECTED_S=[40+20*i for i in range(14)]
EXPECTED_IDS=[f'real{i:03d}' for i in range(100)]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path('.')); ap.add_argument('--config',default='configs/baseline_v1_canonical.yaml'); ap.add_argument('--manifest',default='results/validation_manifest_v5.json'); ap.add_argument('--output',required=True); a=ap.parse_args(); r=a.root; checks=[]
 cp=r/a.config; mp=r/a.manifest
 try: cfg=yaml.safe_load(cp.read_text()); man=json.loads(mp.read_text())
 except Exception as e:
  out={'schema':'protocol_consistency_audit_v1','status':'BLOCKED','error':str(e)}; Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out)); return
 def check(name,ok,value=None): checks.append({'name':name,'status':'PASS' if ok else 'BLOCKED','value':value})
 check('config_exists',cp.exists(),str(cp)); check('manifest_exists',mp.exists(),str(mp)); check('config_sha256',sha(cp)==man.get('canonical_config_sha256'),sha(cp)); check('manifest_schema',man.get('schema')=='validation_manifest_v3',man.get('schema')); check('manifest_frozen',man.get('status')=='FROZEN',man.get('status')); check('manifest_config_path',man.get('canonical_config')==a.config,man.get('canonical_config')); check('redshift',cfg.get('redshift')==1.0,cfg.get('redshift')); check('boxsize',cfg.get('boxsize_mpc_h')==1000.0,cfg.get('boxsize_mpc_h')); check('mass_cut',float(cfg.get('mass_min_msun_h'))==1e13,cfg.get('mass_min_msun_h')); check('fof_real_cic',cfg.get('halo_finder')=='FoF' and cfg.get('space')=='real' and cfg.get('estimator')=='CIC_count_over_cell_mean_minus_one'); check('shells',cfg.get('shell_width_mpc_h')==20.0 and cfg.get('s_mpc_h')==EXPECTED_S,cfg.get('s_mpc_h')); check('grid_roles',cfg.get('primary_nmesh')==64 and cfg.get('convergence_nmesh')==128 and cfg.get('supplement_nmesh')==256); check('zero_mode',cfg.get('zero_mode_subtracted') is True); check('split',cfg.get('train_realizations')==70 and cfg.get('holdout_realizations')==30 and cfg.get('train_ids')=='real000-real069' and cfg.get('holdout_ids')=='real070-real099'); check('no_holdout_response_fit',cfg.get('fit_png_response_on_holdout') is False); nodes=man.get('nodes',{}); check('node_set',set(nodes)=={'fiducial','LC_m','LC_p'},list(nodes)); check('node_shapes_ids',all(v.get('n')==100 and v.get('ids')==EXPECTED_IDS and v.get('shape_mu1')==[100,14] and v.get('shape_mu2')==[100,14] for v in nodes.values())); check('fnl_labels',nodes.get('fiducial',{}).get('fNL')==0.0 and nodes.get('LC_m',{}).get('fNL')==-100.0 and nodes.get('LC_p',{}).get('fNL')==100.0)
 out={'schema':'protocol_consistency_audit_v1','status':'PASS' if all(x['status']=='PASS' for x in checks) else 'BLOCKED','config':a.config,'manifest':a.manifest,'config_sha256':sha(cp),'manifest_sha256':sha(mp),'checks':checks,'scope':'single canonical v1 protocol gate','policy':{'immutable_manifest':True,'same_config_split_scales_required':True,'production_promotion':False}}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'pass':sum(x['status']=='PASS' for x in checks),'total':len(checks)}))
if __name__=='__main__': main()
