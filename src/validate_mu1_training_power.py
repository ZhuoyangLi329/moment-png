#!/usr/bin/env python3
"""Leakage-free training P_h(k) calibration diagnostic for held-out mu1."""
import argparse, json
from pathlib import Path
import numpy as np
from exact_window import mesh_wavevectors, mu1_discrete

NODES=("fiducial","LC_m","LC_p")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--ntrain',type=int,default=70); a=ap.parse_args()
 kv=mesh_wavevectors(64,1000.); ss=np.arange(40.,300.1,20.); rows={}
 for node in NODES:
  p=np.load(a.root/f'results/nbody_baseline_v1/nbody_{node}_n64.npz'); m=np.load(a.root/f'results/power_real_n100_n64/moments_{node}_n64.npz'); ids=np.asarray(p['realization_ids']).astype(str); train=np.arange(a.ntrain); hold=np.arange(a.ntrain,len(ids));
  if not np.array_equal(ids,np.asarray(m['realization_ids']).astype(str)): raise ValueError(f'{node}: ID mismatch')
  if len(hold)==0: raise ValueError('empty holdout')
  train_ph=np.asarray(p['P_h'],float)[train].mean(0); pk=np.interp(np.linalg.norm(kv,axis=1),np.asarray(p['k'],float),train_ph,left=0.,right=train_ph[-1]); pk[np.linalg.norm(kv,axis=1)==0]=0.
  pred=np.array([mu1_discrete(kv,pk,float(s),width=20.,boxsize=1000.,cell=15.625,nmesh=64,power_convention='mesh') for s in ss]); z=np.asarray(m['mu1'],float)[hold]; mean=z.mean(0); se=z.std(0,ddof=1)/np.sqrt(len(z)); r=mean-pred; C=np.cov(z,rowvar=False,ddof=1)/len(z); pull=r/np.maximum(se,1e-30); chi=float(r@np.linalg.pinv(C,rcond=1e-10)@r); rows[node]={'fNL':float(p['fNL']),'n_train':int(len(train)),'n_holdout':int(len(hold)),'train_ids':[str(x) for x in ids[train]],'holdout_ids':[str(x) for x in ids[hold]],'prediction_mu1':pred.tolist(),'mean_nbody_mu1':mean.tolist(),'se_mean':se.tolist(),'pull':pull.tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull))),'chi2_dof':chi/len(r),'coverage_abs_pull_le_2':float(np.mean(np.abs(pull)<=2)),'training_P_h_only':True}
 out={'status':'PASS','schema':'mu1_training_ph_calibration_holdout_v1','nmesh':64,'s':ss.tolist(),'nodes':rows,'scope':'training-only mean P_h(k) projection to held-out direct mu1; diagnostic calibration, not a pure analytic model','policy':{'train_ids':'real000-real069','holdout_ids':'real070-real099','heldout_response_fit':False,'production_promotion':False},'warning':'Training P_h includes empirical tracer physics and is used only to isolate normalization/systematic effects; it is not promoted as the analytic mean.'}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','chi2_dof':{n:round(v['chi2_dof'],2) for n,v in rows.items()},'rms_pull':{n:round(v['rms_pull'],2) for n,v in rows.items()}}))
if __name__=='__main__':main()
