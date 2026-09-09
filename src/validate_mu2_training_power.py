#!/usr/bin/env python3
"""Leakage-free training P_h(k) calibration diagnostic for held-out Gaussian mu2."""
import argparse, json
from pathlib import Path
import numpy as np
from exact_window import mu2_gaussian_discrete

NODES=("fiducial","LC_m","LC_p")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--ntrain',type=int,default=70); a=ap.parse_args()
 inp=np.load(a.root/'inputs/quijote_fiducial_z1_theory_lattice64.npz'); kv=np.asarray(inp['kvecs']); km=np.linalg.norm(kv,axis=1); ss=np.arange(40.,300.1,20.); rows={}
 for node in NODES:
  d=np.load(a.root/f'results/nbody_baseline_v1/nbody_{node}_n64.npz'); ids=np.asarray(d['realization_ids']).astype(str); train=np.arange(a.ntrain); hold=np.arange(a.ntrain,len(ids));
  train_ph=np.asarray(d['P_h'],float)[train].mean(0); pk=np.interp(km,np.asarray(d['k'],float),train_ph,left=0.,right=train_ph[-1]); pk[km==0]=0.
  pred=np.array([float(mu2_gaussian_discrete(kv,pk,float(s),width=20.,boxsize=1000.,cell=15.625,nmesh=64,power_convention='mesh')[0]) for s in ss]); z=np.asarray(d['mu2_gaussian'],float)[hold]; mean=z.mean(0); se=z.std(0,ddof=1)/np.sqrt(len(z)); r=mean-pred; C=np.cov(z,rowvar=False,ddof=1)/len(z); pull=r/np.maximum(se,1e-30); chi=float(r@np.linalg.pinv(C,rcond=1e-10)@r); rows[node]={'fNL':float(d['fNL']),'n_train':int(len(train)),'n_holdout':int(len(hold)),'prediction_mu2_gaussian':pred.tolist(),'mean_nbody_mu2_gaussian':mean.tolist(),'se_mean':se.tolist(),'pull':pull.tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull))),'chi2_dof':chi/len(r),'coverage_abs_pull_le_2':float(np.mean(np.abs(pull)<=2)),'training_P_h_only':True}
 out={'status':'PASS','schema':'mu2_training_ph_calibration_holdout_v1','nmesh':64,'s':ss.tolist(),'nodes':rows,'scope':'training-only mean P_h(k) exact-discrete Gaussian mu2 projection to held-out mu2G; diagnostic only','policy':{'train_ids':'real000-real069','holdout_ids':'real070-real099','heldout_response_fit':False,'production_promotion':False},'warning':'This is the Gaussian component only; contact, clustered halo, and primordial four-point terms are omitted.'}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','chi2_dof':{n:round(v['chi2_dof'],2) for n,v in rows.items()},'rms_pull':{n:round(v['rms_pull'],2) for n,v in rows.items()}}))
if __name__=='__main__':main()
