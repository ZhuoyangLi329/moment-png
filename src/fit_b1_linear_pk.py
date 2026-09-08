#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--nbody',type=Path,required=True); ap.add_argument('--theory-table',type=Path,required=True); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--train-end',type=int,default=70); ap.add_argument('--kmax',type=float,default=.08); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 tab=np.loadtxt(a.theory_table,comments='#'); kt,pm_t,_,_=tab.T; d=np.load(a.nbody/f'nbody_fiducial_n{a.nmesh}.npz'); k=np.asarray(d['k']); Y=np.asarray(d['P_h'])[:a.train_end]; mean=Y.mean(0); cov=np.cov(Y,rowvar=False,ddof=1)/len(Y); n=a.nmesh; q=2*np.pi*np.fft.fftfreq(n,d=a.box/n); gx,gy,gz=np.meshgrid(q,q,q,indexing='ij'); h=a.box/n; km=np.sqrt(gx*gx+gy*gy+gz*gz); edges=np.arange(0,.3+.005,.005); ib=np.digitize(km.ravel(),edges)-1; ok=(ib>=0)&(ib<len(edges)-1)&(km.ravel()>0); cnt=np.bincount(ib[ok],minlength=len(edges)-1); cic=np.sinc(gx*h/(2*np.pi))**4*np.sinc(gy*h/(2*np.pi))**4*np.sinc(gz*h/(2*np.pi))**4; tr=np.bincount(ib[ok],weights=cic.ravel()[ok],minlength=len(edges)-1)/np.maximum(cnt,1); kc=.5*(edges[:-1]+edges[1:]); Pm=np.interp(np.clip(k,kt.min(),kt.max()),kt,pm_t); tf=np.interp(k,kc,tr); mask=k<=a.kmax; C=cov[np.ix_(mask,mask)]; L=np.linalg.cholesky(np.linalg.pinv(C,rcond=1e-10)+1e-18*np.eye(mask.sum())); pp=Pm[mask]*tf[mask]; mm=mean[mask]
 def fun(x): return L@(x[0]**2*pp+x[1]-mm)
 fit=least_squares(fun,[2.7,3000.],bounds=([0.,0.],[6.,1e6])); x=fit.x; J=fit.jac; pc=np.linalg.pinv(J.T@J,rcond=1e-10); sig=np.sqrt(np.maximum(np.diag(pc),0)); resid=mm-(x[0]**2*pp+x[1]); chi=float(resid@np.linalg.pinv(C,rcond=1e-10)@resid); out={'status':'PASS','schema':'fiducial_linear_pk_b1_training_v1','nmesh':a.nmesh,'ntrain':len(Y),'kmax':a.kmax,'b1':float(x[0]),'b1_sigma_linearized':float(sig[0]),'P_shot':float(x[1]),'P_shot_sigma':float(sig[1]),'chi2':chi,'dof':int(mask.sum()-2),'chi2_dof':chi/max(mask.sum()-2,1),'cic_power_transfer':True,'model':'P_h_mesh=b1^2 P_m_linear |W_CIC|^2 + P_shot','holdout_excluded':'real070-real099','scope':'fiducial training-only linear P(k) calibration; no PNG response fit','warning':'Use as a declared training calibration; nonlinear kmax dependence remains a systematic.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(out)
if __name__=='__main__': main()


