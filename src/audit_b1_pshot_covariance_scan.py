#!/usr/bin/env python3
"""Full covariance, physically bounded b1/Pshot scan for Stage 2."""
import argparse, datetime, hashlib, json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def fit_one(pmode,kv,pmi,lo,hi,kmax,box=1000.,nmesh=64):
    h=box/nmesh; k=np.linalg.norm(kv,axis=1); edges=np.arange(0,.3+.005,.005); kc=.5*(edges[:-1]+edges[1:]); idx=np.digitize(k,edges)-1
    ok=(idx>=0)&(idx<len(kc))&(k>0); cic=np.sinc(kv[:,0]*h/(2*np.pi))**4*np.sinc(kv[:,1]*h/(2*np.pi))**4*np.sinc(kv[:,2]*h/(2*np.pi))**4; inds=[i for i in range(len(kc)) if kc[i]<=kmax and np.any(ok&(idx==i))]
    x=np.asarray(pmode[lo:hi]); y=np.array([x[:,ok&(idx==i)].mean() for i in inds]); real=np.array([x[:,ok&(idx==i)].mean(1) for i in inds]).T; C=np.cov(real,rowvar=False,ddof=1)/len(x); eig,u=np.linalg.eigh(C);keep=eig>max(float(eig.max()),1e-30)*1e-10;R=(u[:,keep]/np.sqrt(eig[keep])).T
    X=np.column_stack([pmi[inds]*np.array([cic[ok&(idx==i)].mean() for i in inds]),np.ones(len(inds))]); scales=np.maximum(np.linalg.norm(X,axis=0),1.); residual=lambda z:R@(y-X@(z/scales)); init=np.array([2.8**2*scales[0],4000*scales[1]]); fit=least_squares(residual,init,bounds=([0.,0.],[36*scales[0],1e6*scales[1]]),x_scale='jac'); beta=fit.x/scales; J=fit.jac; covz=np.linalg.pinv(J.T@J,rcond=1e-12); cov=np.diag(1/scales)@covz@np.diag(1/scales); b1=float(np.sqrt(max(beta[0],0))); return {'b1':b1,'b1_sigma':float(np.sqrt(max(cov[0,0],0))/(2*b1)) if b1>0 else None,'P_shot':float(beta[1]),'P_shot_sigma':float(np.sqrt(max(cov[1,1],0))),'b1_pshot_corr':float(cov[0,1]/np.sqrt(max(cov[0,0]*cov[1,1],1e-300))),'chi2_dof':float(np.sum(residual(fit.x)**2)/max(len(inds)-2,1)),'n_bins':len(inds),'shot_boundary_active':bool(beta[1]<=1e-8),'nreal':hi-lo}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--power',type=Path,required=True); ap.add_argument('--theory',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    d=np.load(a.power); tab=np.load(a.theory); kv=np.asarray(d['kvecs'],float); pm=np.asarray(tab['Pm'],float); kt=np.asarray(tab['k'],float); edges=np.arange(0,.3+.005,.005); kc=.5*(edges[:-1]+edges[1:]); order=np.argsort(kt); pmi=np.interp(kc,kt[order],pm[order]); ids=np.asarray(d['realization_ids']).astype(str); rows={}
    for kmax in [.03,.05,.08,.10,.15]:
        rows[str(kmax)]={'full':fit_one(d['Pmode'],kv,pmi,0,len(ids),kmax),'blocks':[fit_one(d['Pmode'],kv,pmi,lo,lo+100,kmax) for lo in range(0,len(ids),100)]}
    out={'schema':'b1_pshot_covariance_scan_v1','status':'DIAGNOSTIC','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'power_source':str(a.power),'power_sha256':sha(a.power),'theory_source':str(a.theory),'theory_sha256':sha(a.theory),'realization_block':f'{ids[0]}-{ids[-1]}','kmax_scan':rows,'policy':{'full_covariance':True,'physical_bounds':{'b1':'0<=b1<=6','Pshot':'0<=Pshot<=1e6'},'production_promotion':False},'warning':'The scan is an input audit; large b1/Pshot covariance, boundary solutions, or poor chi2 prevent production calibration.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'full_b1':{k:round(v['full']['b1'],4) for k,v in rows.items()},'full_chi2':{k:round(v['full']['chi2_dof'],2) for k,v in rows.items()}}))
if __name__=='__main__':main()

