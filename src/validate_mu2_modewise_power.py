#!/usr/bin/env python3
"""Fast full-lattice Gaussian mu2 identity audit using ensemble-centered Wick baseline."""
import argparse,json
from pathlib import Path
import numpy as np
from exact_window import shell_window
ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--mode-dir',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
ss=np.arange(40.,300.1,20.); rows={}
for node in ['fiducial','LC_m','LC_p']:
 mp=np.load(a.mode_dir/f'modepower_{node}_n64.npz'); kv=np.asarray(mp['kvecs']); P=np.asarray(mp['Pmode'],float); ids=np.asarray(mp['realization_ids']); m=np.load(a.root/f'results/resolution_clean/connected_{node}_n64.npz'); mids=np.asarray([f'real{i:03d}' for i in range(len(m['mu2_gaussian']))])
 lookup={str(x):i for i,x in enumerate(mids)}; obs=np.asarray(m['mu2_gaussian'],float)[[lookup[str(x)] for x in ids]]
 V=1000.**3; sig0=P.sum(axis=1)/V; pred=[]
 for s in ss:
  W=shell_window(kv,float(s),20.,boxsize=1000.,nmesh=64); PW=P*W[None,:]; sigs=(PW*W[None,:]).sum(axis=1)/V; xi=PW.sum(axis=1)/V; pred.append(sig0*sigs+xi*xi)
 pred=np.asarray(pred).T; diff=obs-pred; mean=diff.mean(0); se=diff.std(0,ddof=1)/np.sqrt(len(diff)); cov=np.cov(diff,rowvar=False,ddof=1)/len(diff); chi=float(mean@np.linalg.pinv(cov,rcond=1e-10)@mean); pull=mean/np.maximum(se,1e-30)
 rows[node]={'fNL':int({'fiducial':0,'LC_m':-100,'LC_p':100}[node]),'nreal':len(P),'realization_ids':ids.tolist(),'s':ss.tolist(),'mean_observed':obs.mean(0).tolist(),'mean_predicted':pred.mean(0).tolist(),'mean_difference':mean.tolist(),'std_difference_realization':diff.std(0,ddof=1).tolist(),'se_mean_difference':se.tolist(),'covariance_mean':cov.tolist(),'pull_mean':pull.tolist(),'rms_pull_mean':float(np.sqrt(np.mean(pull*pull))),'chi2':chi,'dof':len(ss),'chi2_dof':chi/len(ss),'coverage_abs_pull_le_2':float(np.mean(np.abs(pull)<=2)),'per_realization_rms_difference':float(np.sqrt(np.mean(diff*diff))),'max_abs_per_realization_difference':float(np.max(np.abs(diff)))}
out={'status':'PASS','schema':'mu2_modewise_power_identity_v2','nmesh':64,'s':ss.tolist(),'nodes':rows,'scope':'same-realization full-lattice P_h to ensemble-centered Gaussian mu2 Wick identity; no connected/contact terms','policy':{'holdout_ids':'real070-real099','sample_centered_wick':False,'exact_lattice_modes':True,'no_response_fit':True},'warning':'This is an estimator consistency diagnostic; a residual does not promote any b_phi or close the halo four-point model.'}
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','rms_pull_mean':{n:round(v['rms_pull_mean'],3) for n,v in rows.items()},'chi2_dof':{n:round(v['chi2_dof'],3) for n,v in rows.items()},'per_realization_rms':{n:v['per_realization_rms_difference'] for n,v in rows.items()}}))
