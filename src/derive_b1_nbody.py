#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--nbody',type=Path,required=True); ap.add_argument('--theory-table',type=Path,required=True); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 tab=np.loadtxt(a.theory_table,comments='#'); kt,pm_t,_,_=tab.T; d=np.load(a.nbody/f'nbody_fiducial_n{a.nmesh}.npz'); k=np.asarray(d['k']); y=np.asarray(d['P_h']); mean=y.mean(0); se=y.std(0,ddof=1)/np.sqrt(len(y)); n=a.nmesh; q=2*np.pi*np.fft.fftfreq(n,d=a.box/n); gx,gy,gz=np.meshgrid(q,q,q,indexing='ij'); h=a.box/n; km=np.sqrt(gx*gx+gy*gy+gz*gz); edges=np.arange(0,.3+.005,.005); ib=np.digitize(km.ravel(),edges)-1; ok=(ib>=0)&(ib<len(edges)-1)&(km.ravel()>0); cnt=np.bincount(ib[ok],minlength=len(edges)-1); cic=np.sinc(gx*h/(2*np.pi))**4*np.sinc(gy*h/(2*np.pi))**4*np.sinc(gz*h/(2*np.pi))**4; tr=np.bincount(ib[ok],weights=cic.ravel()[ok],minlength=len(edges)-1)/np.maximum(cnt,1); kc=.5*(edges[:-1]+edges[1:]); pm=np.interp(np.clip(k,kt.min(),kt.max()),kt,pm_t); tf=np.interp(k,kc,tr); raw=np.sqrt(np.maximum(mean/np.maximum(pm,1e-30),0)); corr=np.sqrt(np.maximum(mean/np.maximum(pm*tf,1e-30),0)); out={'status':'PASS','schema':'fiducial_b1_nbody_diagnostic_v1','k':k.tolist(),'P_h_mean':mean.tolist(),'P_h_se':se.tolist(),'b1_raw':raw.tolist(),'b1_cic_corrected':corr.tolist(),'nreal':len(y),'nmesh':n,'scope':'fiducial training-set bias diagnostic; no PNG response fit','warning':'P_h is a halo mesh spectrum and P_m is an external linear spectrum; interpret only after convention audit'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print({'status':'PASS','n_k':len(k),'b1_raw_lowk':raw[:5].tolist(),'b1_cic_lowk':corr[:5].tolist()})
if __name__=='__main__': main()


