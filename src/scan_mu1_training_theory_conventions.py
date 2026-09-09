#!/usr/bin/env python3
"""Training-only fit of b1/Pshot under CIC/shot conventions, then held-out mu1 test."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from exact_window import mu1_discrete

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--ntrain',type=int,default=70); ap.add_argument('--p',type=float,default=1.12); ap.add_argument('--delta-c',type=float,default=1.686); ap.add_argument('--kmax',type=float,default=.08); a=ap.parse_args()
 root=a.root; inp=np.load(root/'inputs/quijote_fiducial_z1_theory_lattice64.npz'); kv=np.asarray(inp['kvecs']); pm=np.asarray(inp['Pm'],float); M=np.asarray(inp['M'],float); km=np.linalg.norm(kv,axis=1); n=64; L=1000.; h=L/n
 fid=np.load(root/'results/nbody_baseline_v1/nbody_fiducial_n64.npz'); kb=np.asarray(fid['k'],float); edges=np.r_[kb-.0025,kb[-1]+.0025]; ib=np.digitize(km,edges)-1; ok=(ib>=0)&(ib<len(kb))&(km>0); cic=np.sinc(kv[:,0]*h/(2*np.pi))**4*np.sinc(kv[:,1]*h/(2*np.pi))**4*np.sinc(kv[:,2]*h/(2*np.pi))**4; cnt=np.bincount(ib[ok],minlength=len(kb)); pmb=np.bincount(ib[ok],weights=pm[ok],minlength=len(kb))/np.maximum(cnt,1); tr=np.bincount(ib[ok],weights=cic[ok],minlength=len(kb))/np.maximum(cnt,1); train=np.asarray(fid['P_h'],float)[:a.ntrain].mean(0); mask=(kb<=a.kmax)&(cnt>0); rows={}; ss=np.arange(40.,300.1,20.)
 for name,clust_t,shot_t in [('cic_both',tr,tr),('cic_cluster_shot_plain',tr,np.ones_like(tr)),('plain_both',np.ones_like(tr),np.ones_like(tr))]:
  pp=pmb*clust_t; mm=train
  def fun(x): return (x[0]**2*pp[mask]+x[1]*shot_t[mask]-mm[mask])/np.maximum(mm[mask],1.)
  fit=least_squares(fun,[2.78,3603.],bounds=([0.,0.],[6.,1e6])); b1,ps=map(float,fit.x); bphi=2*a.delta_c*(b1-a.p); rows[name]={'b1':b1,'bphi':bphi,'P_shot':ps,'kmax_fit':a.kmax,'training_fit_rms':float(np.sqrt(np.mean(fun(fit.x)**2))),'nodes':{}}
  use_cic = name.startswith('cic')
  for node in ('fiducial','LC_m','LC_p'):
   d=np.load(root/f'results/nbody_baseline_v1/nbody_{node}_n64.npz'); m=np.load(root/f'results/power_real_n100_n64/moments_{node}_n64.npz'); hold=np.arange(a.ntrain,len(d['realization_ids'])); fnl=float(d['fNL']); bh=b1+fnl*bphi/np.maximum(np.abs(M),1e-30); matter_mode=cic if use_cic else np.ones_like(cic)
   shot_mode=cic if shot_t[0] != 1 else np.ones_like(cic)
   ph=bh*bh*pm*cic + ps*shot_mode; ph[(km==0)]=0.; pred=np.array([mu1_discrete(kv,ph,float(s),width=20.,boxsize=L,cell=h,nmesh=n,power_convention='mesh') for s in ss]); z=np.asarray(m['mu1'],float)[hold]; mean=z.mean(0); cr=np.cov(z,rowvar=False,ddof=1); cm=cr/len(z); se=np.sqrt(np.diag(cm)); r=mean-pred; chi=float(r@np.linalg.pinv(cm,rcond=1e-10)@r); rows[name]['nodes'][node]={'fNL':fnl,'n_holdout':len(hold),'prediction_mu1':pred.tolist(),'mean_mu1':mean.tolist(),'std_realization':np.sqrt(np.diag(cr)).tolist(),'se_mean':se.tolist(),'chi2_dof':chi/len(r),'rms_pull':float(np.sqrt(np.mean((r/np.maximum(se,1e-30))**2))),'coverage':float(np.mean(np.abs(r/np.maximum(se,1e-30))<=2))}
 out={'status':'PASS','schema':'mu1_training_theory_convention_scan_v1','nodes':rows,'scope':'training-only b1/Pshot fit; held-out mu1 test; diagnostic only','policy':{'train_ids':'real000-real069','holdout_ids':'real070-real099','no_png_response_fit':True,'no_production_promotion':True},'warning':'Convention scan isolates normalization and CIC/shot effects; it is not an independent bias calibration.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','fits':{k:{'b1':round(v['b1'],4),'Pshot':round(v['P_shot'],2),'chi2_dof':{n:round(x['chi2_dof'],2) for n,x in v['nodes'].items()}} for k,v in rows.items()}}))
if __name__=='__main__':main()
