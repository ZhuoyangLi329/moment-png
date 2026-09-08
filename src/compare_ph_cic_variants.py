#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--nbody-dir',type=Path,required=True); ap.add_argument('--theory-table',type=Path,required=True); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--p',type=float,default=1.12); ap.add_argument('--delta-c',type=float,default=1.686); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 tab=np.loadtxt(a.theory_table,comments='#'); kt,pm_t,pp_t,M_t=tab.T; bp=2*a.delta_c*(a.b1-a.p); n=a.nmesh; q=2*np.pi*np.fft.fftfreq(n,d=a.box/n); gx,gy,gz=np.meshgrid(q,q,q,indexing='ij'); h=a.box/n; km=np.sqrt(gx*gx+gy*gy+gz*gz); cic=np.sinc(gx*h/(2*np.pi))**4*np.sinc(gy*h/(2*np.pi))**4*np.sinc(gz*h/(2*np.pi))**4; edges=np.arange(0,.3+.005,.005); ib=np.digitize(km.ravel(),edges)-1; ok=(ib>=0)&(ib<len(edges)-1)&(km.ravel()>0); cnt=np.bincount(ib[ok],minlength=len(edges)-1); tr=np.bincount(ib[ok],weights=cic.ravel()[ok],minlength=len(edges)-1)/np.maximum(cnt,1); kc=.5*(edges[:-1]+edges[1:]); Pm=np.interp(np.clip(kc,kt.min(),kt.max()),kt,pm_t); M=np.interp(np.clip(kc,kt.min(),kt.max()),kt,M_t); rows={}
 for node,fnl in [('fiducial',0.),('LC_m',-100.),('LC_p',100.)]:
  d=np.load(a.nbody_dir/f'nbody_{node}_n{n}.npz'); k=np.asarray(d['k']); y=np.asarray(d['P_h']); mean=y.mean(0); se=y.std(0,ddof=1)/np.sqrt(len(y)); m=np.interp(np.clip(k,kt.min(),kt.max()),kt,pm_t); mt=np.interp(np.clip(k,kt.min(),kt.max()),kt,M_t); base=(a.b1+fnl*bp/np.maximum(abs(mt),1e-30))**2*m
  variants={}
  for label,transfer in [('no_cic',np.ones_like(k)),('cic',np.interp(k,kc,tr))]:
   pred=base*transfer; pull=(mean-pred)/np.maximum(se,1e-30); variants[label]={'prediction':pred.tolist(),'ratio_model_over_nbody':(pred/np.maximum(mean,1e-30)).tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull))),'rms_pull_kmax_003':float(np.sqrt(np.mean(pull[k<=.03]**2))),'rms_pull_kmax_005':float(np.sqrt(np.mean(pull[k<=.05]**2)))}
  rows[node]={'fNL':fnl,'k':k.tolist(),'variants':variants}
 out={'status':'PASS','schema':'ph_nbody_cic_variant_comparison_v1','b1':a.b1,'bphi':bp,'p':a.p,'nodes':rows,'scope':'tree halo power N-body comparison isolating CIC power transfer; no PNG response fit'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print({'status':'PASS','nodes':len(rows)})
if __name__=='__main__': main()


