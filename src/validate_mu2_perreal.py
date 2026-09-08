#!/usr/bin/env python3
import argparse,json,os,platform,hashlib
from pathlib import Path
import numpy as np
from exact_window import mu2_gaussian_discrete,mesh_wavevectors

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); kv=mesh_wavevectors(64,1000.); km=np.linalg.norm(kv,axis=1); ss=np.arange(40.,300.1,20.); rows={}
 for node in ['fiducial','LC_m','LC_p']:
  p=np.load(a.root/f'results/power_real_n100_n64/power_{node}_n64.npz'); m=np.load(a.root/f'results/resolution_clean/connected_{node}_n64.npz'); ids=[str(x) for x in p['realization_ids']]; hold=[i for i,x in enumerate(ids) if int(x[4:])>=70]; obs=np.asarray(m['mu2_gaussian'],float)[hold]; pred=[]
  for i in hold:
   pk=np.interp(km,np.asarray(p['k'],float),np.asarray(p['P'],float)[i],left=0.,right=float(np.asarray(p['P'],float)[i][-1])); pk[km==0]=0.; pred.append([mu2_gaussian_discrete(kv,pk,float(s),width=20.,boxsize=1000.,cell=15.625,nmesh=64,power_convention='mesh',sample_centered=True)[0] for s in ss])
  pred=np.asarray(pred); delta=obs-pred; mean=delta.mean(0); se=delta.std(0,ddof=1)/np.sqrt(len(delta)); pull=mean/np.maximum(se,1e-30); C=np.cov(delta,rowvar=False,ddof=1)/len(delta); chi=float(mean@np.linalg.pinv(C,rcond=1e-10)@mean); rows[node]={'fNL':float(p['fNL']),'n_holdout':len(hold),'mean_paired_residual':mean.tolist(),'se_paired_residual':se.tolist(),'rms_pull_vs_zero':float(np.sqrt(np.mean(pull*pull))),'chi2_dof':chi/len(mean),'coverage_abs_pull_le_2':float(np.mean(np.abs(pull)<=2)),'mean_observed_mu2G':obs.mean(0).tolist(),'mean_predicted_from_own_Ph':pred.mean(0).tolist()}
 out={'status':'PASS','schema':'mu2_gaussian_perrealization_identity_v1','s':ss.tolist(),'nodes':rows,'scope':'paired heldout identity using each realization P_h(k) to predict its own exact-discrete Gaussian mu2','policy':{'holdout_start':70,'sample_centered_wick':True,'no_response_fit':True},'warning':'Any residual is diagnostic of finite-mesh/contact/covariance effects; this is not a production connected four-point model.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','chi2_dof':{n:round(v['chi2_dof'],2) for n,v in rows.items()},'rms_pull':{n:round(v['rms_pull_vs_zero'],2) for n,v in rows.items()}}))
if __name__=='__main__':main()
