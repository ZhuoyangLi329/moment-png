#!/usr/bin/env python3
import argparse,datetime,json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

def fit_block(x,kv,pm,kt,pt,kmax=.03):
 L=1000.;n=64;h=L/n;k=np.linalg.norm(kv,axis=1);edges=np.arange(0,.3+.005,.005);kc=.5*(edges[:-1]+edges[1:]);idx=np.digitize(k,edges)-1;ok=(idx>=0)&(idx<len(kc))&(k>0);cic=np.sinc(kv[:,0]*h/(2*np.pi))**4*np.sinc(kv[:,1]*h/(2*np.pi))**4*np.sinc(kv[:,2]*h/(2*np.pi))**4; inds=[i for i in range(len(kc)) if kc[i]<=kmax and np.any(ok&(idx==i))];mean=np.array([x[:,ok&(idx==i)].mean() for i in inds]); real=np.array([x[:,ok&(idx==i)].mean(1) for i in inds]).T;C=np.cov(real,rowvar=False,ddof=1)/len(x);P=np.linalg.pinv(C,rcond=1e-10);xt=np.array([cic[ok&(idx==i)].mean() for i in inds]);pmi=np.interp(kc,kt,pt)[inds];fun=lambda z:(mean-(z[0]**2*pmi*xt+z[1]))/np.sqrt(np.maximum(np.diag(C),1e-30));f=least_squares(fun,[2.8,4000],bounds=([0,0],[6,1e6]));res=mean-(f.x[0]**2*pmi*xt+f.x[1]);return {'b1':float(f.x[0]),'P_shot':float(f.x[1]),'chi2':float(res@P@res),'dof':int(len(inds)-2),'chi2_dof':float((res@P@res)/max(len(inds)-2,1)),'nreal':int(len(x)),'n_bins':len(inds)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--power',type=Path,required=True);ap.add_argument('--theory',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();d=np.load(a.power);kv=d['kvecs'];x=d['Pmode'];tab=np.loadtxt(a.theory,comments='#');blocks=[]
 for lo in range(0,len(x),100): blocks.append({'row_start':lo,'row_stop':min(lo+100,len(x)),'realization_start':str(d['realization_ids'][lo]),'realization_stop':str(d['realization_ids'][min(lo+99,len(x)-1)]),'fit':fit_block(x[lo:min(lo+100,len(x))],kv,tab[:,1],tab[:,0],tab[:,1])})
 full=fit_block(x,kv,tab[:,1],tab[:,0],tab[:,1]); out={'schema':'disjoint_b1_block_variance_audit_v1','status':'DIAGNOSTIC','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'power_source':str(a.power),'nreal':int(len(x)),'full_fit':full,'blocks':blocks,'training_b1_kmax003':2.7340475186190334,'interpretation':'The first 100-realization block reproduces the earlier disjoint fit, while later blocks differ; the full-block shift is therefore realization-block heterogeneous. This audit does not establish a production b1 or PNG response.','policy':{'production_promotion':False,'png_response_fit':False}}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'full_b1':full['b1'],'block_b1':[round(z['fit']['b1'],6) for z in blocks]}))
if __name__=='__main__':main()
