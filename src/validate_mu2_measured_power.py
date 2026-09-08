#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from exact_window import mu2_gaussian_discrete

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); inp=np.load(a.root/'inputs/quijote_fiducial_z1_theory_lattice64.npz'); kv=np.asarray(inp['kvecs']); km=np.linalg.norm(kv,axis=1); ss=np.arange(40.,300.1,20.); rows={}
 for node in ['fiducial','LC_m','LC_p']:
  p=np.load(a.root/f'results/power_real_n100_n64/power_{node}_n64.npz'); kh=np.asarray(p['k']); ph=np.asarray(p['mean_P']); pk=np.interp(km,kh,ph,left=0.,right=ph[-1]); pk[km==0]=0.; pred=[]
  for s in ss: pred.append(float(mu2_gaussian_discrete(kv,pk,float(s),width=20.,boxsize=1000.,cell=15.625,nmesh=64,power_convention='mesh')[0]))
  c=np.load(a.root/f'results/resolution_clean/connected_{node}_n64.npz'); z=np.asarray(c['mu2_gaussian'],float); mean=z.mean(0); se=z.std(0,ddof=1)/np.sqrt(len(z)); r=mean-np.asarray(pred); C=np.cov(z,rowvar=False,ddof=1)/len(z); chi=float(r@np.linalg.pinv(C,rcond=1e-10)@r); rows[node]={'fNL':float(p['fNL']),'prediction_mu2_gaussian':pred,'nreal':len(z),'mean_nbody_mu2_gaussian':mean.tolist(),'se':se.tolist(),'rms_pull':float(np.sqrt(np.mean((r/np.maximum(se,1e-30))**2))),'chi2_dof':chi/len(r),'coverage_abs_pull_le_2':float(np.mean(np.abs(r/np.maximum(se,1e-30))<=2))}
 out={'status':'PASS','schema':'mu2_gaussian_from_measured_ph_validation_v1','s':ss.tolist(),'nodes':rows,'scope':'exact discrete Gaussian Wick projection using measured mean P_h(k), isolating external Pm normalization','warning':'This is a diagnostic identity test; it does not include connected halo contact or PNG four-point terms.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','chi2_dof':{n:round(v['chi2_dof'],2) for n,v in rows.items()},'rms_pull':{n:round(v['rms_pull'],2) for n,v in rows.items()}}))
if __name__=='__main__':main()
