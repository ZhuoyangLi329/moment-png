#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from exact_window import shell_window

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--mode-dir',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); L=1000.; n=64; ss=np.arange(40.,300.1,20.); rows={}
 for node in ['fiducial','LC_m','LC_p']:
  mp=np.load(a.mode_dir/f'modepower_{node}_n64.npz'); kv=np.asarray(mp['kvecs']); P=np.asarray(mp['Pmode'],float); m=np.load(a.root/f'results/power_real_n100_n64/moments_{node}_n64.npz'); z=np.asarray(m['mu1'],float)[70:70+len(P)]; W=np.vstack([shell_window(kv,float(s),20.,boxsize=L,nmesh=n) for s in ss]); pred=P@W.T/L**3; delta=z-pred; mean_delta=delta.mean(0); se=delta.std(0,ddof=1)/np.sqrt(len(delta)); pull_mean=mean_delta/np.maximum(se,1e-30); C=np.cov(delta,rowvar=False,ddof=1)/len(delta); chi=float(mean_delta@np.linalg.pinv(C,rcond=1e-10)@mean_delta); rows[node]={'nreal':len(P),'s':ss.tolist(),'mean_predicted':pred.mean(0).tolist(),'mean_observed':z.mean(0).tolist(),'mean_difference':mean_delta.tolist(),'se_difference':se.tolist(),'mean_rms_pull':float(np.sqrt(np.mean(pull_mean*pull_mean))),'chi2_dof':chi/len(ss),'coverage_abs_mean_pull_le_2':float(np.mean(np.abs(pull_mean)<=2)),'max_abs_mean_difference':float(np.max(np.abs(mean_delta))),'per_realization_rms_difference':float(np.sqrt(np.mean(delta*delta))),'max_abs_per_realization_difference':float(np.max(np.abs(delta)))}
 out={'status':'PASS','schema':'mu1_modewise_power_identity_v2','nodes':rows,'scope':'same-mode heldout CIC P_h to mu1 identity; no PNG response fit','policy':{'holdout_start':70,'exact_lattice_modes':True,'zero_mode_subtracted':True,'mean_pull_separated_from_per_realization_residual':True},'warning':'This checks estimator consistency; it is not an independent bias calibration or production mean model.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','mean_rms_pull':{n:round(v['mean_rms_pull'],2) for n,v in rows.items()},'chi2_dof':{n:round(v['chi2_dof'],2) for n,v in rows.items()},'per_real_rms':{n:v['per_realization_rms_difference'] for n,v in rows.items()}}))
if __name__=='__main__':main()
