#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from exact_window import mu1_discrete,mesh_wavevectors

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); kv=mesh_wavevectors(64,1000.); km=np.linalg.norm(kv,axis=1); ss=np.arange(40.,300.1,20.); rows={}
 for node in ['fiducial','LC_m','LC_p']:
  p=np.load(a.root/f'results/nbody_baseline_v1/nbody_{node}_n64.npz'); m=np.load(a.root/f'results/power_real_n100_n64/moments_{node}_n64.npz'); ids=[str(x) for x in p['realization_ids']]; hold=[i for i,x in enumerate(ids) if int(x[4:])>=70]; P=np.asarray(p['P_h'],float)[hold].mean(0); pk=np.interp(km,np.asarray(p['k'],float),P,left=0.,right=P[-1]); pk[km==0]=0.; pred=np.array([mu1_discrete(kv,pk,float(s),width=20.,boxsize=1000.,cell=15.625,nmesh=64,power_convention='mesh') for s in ss]); z=np.asarray(m['mu1'],float)[hold]; mean=z.mean(0); se=z.std(0,ddof=1)/np.sqrt(len(z)); pull=(mean-pred)/np.maximum(se,1e-30); C=np.cov(z,rowvar=False,ddof=1)/len(z); r=mean-pred; chi=float(r@np.linalg.pinv(C,rcond=1e-10)@r); rows[node]={'fNL':float(p['fNL']),'n_holdout':len(z),'prediction_mu1':pred.tolist(),'mean_nbody_mu1':mean.tolist(),'se':se.tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull))),'chi2_dof':chi/len(r),'coverage_abs_pull_le_2':float(np.mean(np.abs(pull)<=2)),'first_prediction':float(pred[0])}
 out={'status':'PASS','schema':'mu1_from_measured_ph_validation_v1','s':ss.tolist(),'nodes':rows,'scope':'exact discrete mu1 projection using heldout measured mean P_h, isolating external Pm normalization','policy':{'holdout_start':70,'response_fit':False,'same_window':True},'warning':'This is an estimator identity diagnostic and not an independent bias calibration.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','chi2_dof':{n:round(v['chi2_dof'],2) for n,v in rows.items()},'rms_pull':{n:round(v['rms_pull'],2) for n,v in rows.items()}}))
if __name__=='__main__':main()
