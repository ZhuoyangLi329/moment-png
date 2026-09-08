#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--nbody',type=Path,required=True); ap.add_argument('--theory-table',type=Path,required=True); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 tab=np.loadtxt(a.theory_table,comments='#'); kt,pm_t,_,_=tab.T; d=np.load(a.nbody/f'nbody_fiducial_n{a.nmesh}.npz'); k=np.asarray(d['k']); Y=np.asarray(d['P_h']); mean=Y.mean(0); cov=np.cov(Y,rowvar=False,ddof=1)/len(Y); se=np.sqrt(np.diag(cov)); n=a.nmesh; q=2*np.pi*np.fft.fftfreq(n,d=a.box/n); gx,gy,gz=np.meshgrid(q,q,q,indexing='ij'); h=a.box/n; km=np.sqrt(gx*gx+gy*gy+gz*gz); edges=np.arange(0,.3+.005,.005); ib=np.digitize(km.ravel(),edges)-1; ok=(ib>=0)&(ib<len(edges)-1)&(km.ravel()>0); cnt=np.bincount(ib[ok],minlength=len(edges)-1); cic=np.sinc(gx*h/(2*np.pi))**4*np.sinc(gy*h/(2*np.pi))**4*np.sinc(gz*h/(2*np.pi))**4; tr=np.bincount(ib[ok],weights=cic.ravel()[ok],minlength=len(edges)-1)/np.maximum(cnt,1); kc=.5*(edges[:-1]+edges[1:]); Pm=np.interp(np.clip(k,kt.min(),kt.max()),kt,pm_t); tf=np.interp(k,kc,tr); out={"status":"PASS","schema":"fiducial_b1_covariance_scan_v1","nreal":len(Y),"nmesh":n,"k":k.tolist(),"results":{},"scope":"fiducial training-set P_h fit; no PNG response fit","warning":"kmax scans expose the bias/statistics tradeoff; do not promote a fitted b1 without independent calibration."}
 for use_cic in [False,True]:
  tag='cic' if use_cic else 'no_cic'; T=tf if use_cic else np.ones_like(tf); out["results"][tag]={}
  for cut in [.03,.05,.08,.10,.15,.18]:
   mask=k<=cut; C=cov[np.ix_(mask,mask)]; prec=np.linalg.pinv(C,rcond=1e-10); mm=mean[mask]; pp=Pm[mask]*T[mask];
   def fun(x): return np.linalg.cholesky(prec+1e-18*np.eye(mask.sum()))@(x[0]**2*pp+x[1]-mm)
   fit=least_squares(fun,[2.7,500.],bounds=([0.,0.],[6.,1e6])); x=fit.x; J=fit.jac; pc=np.linalg.pinv(J.T@J,rcond=1e-10); sig=np.sqrt(np.maximum(np.diag(pc),0)); resid=mm-(x[0]**2*pp+x[1]); chi=float(resid@prec@resid); out["results"][tag][str(cut)]={"b1":float(x[0]),"b1_sigma_linearized":float(sig[0]),"pshot":float(x[1]),"pshot_sigma":float(sig[1]),"chi2":chi,"dof":int(mask.sum()-2),"chi2_dof":chi/max(mask.sum()-2,1),"n_k":int(mask.sum())}
 a.output.write_text(json.dumps(out,indent=2)+'\n'); print({tag:{c:round(v['b1'],4) for c,v in z.items()} for tag,z in out['results'].items()})
if __name__=='__main__': main()



