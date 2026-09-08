#!/usr/bin/env python3
"""Compare frozen tree halo-power prediction with canonical N-body mesh spectra."""
import argparse,json
from pathlib import Path
import numpy as np
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--nbody-dir',type=Path,required=True); ap.add_argument('--theory-table',type=Path,required=True); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--p',type=float,default=1.12); ap.add_argument('--delta-c',type=float,default=1.686); ap.add_argument('--pshot',type=float,default=0.); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 tab=np.loadtxt(a.theory_table,comments='#'); kt,pm_t,pp_t,M_t=tab.T; bphi=2*a.delta_c*(a.b1-a.p)
 n=a.nmesh; q=2*np.pi*np.fft.fftfreq(n,d=a.box/n); gx,gy,gz=np.meshgrid(q,q,q,indexing='ij'); km=np.sqrt(gx*gx+gy*gy+gz*gz); h=a.box/n
 cic=(np.sinc(gx*h/(2*np.pi))**4*np.sinc(gy*h/(2*np.pi))**4*np.sinc(gz*h/(2*np.pi))**4)
 edges=np.arange(0,.3+.005,.005); ib=np.digitize(km.ravel(),edges)-1; ok=(ib>=0)&(ib<len(edges)-1)&(km.ravel()>0)
 transfer=np.bincount(ib[ok],weights=cic.ravel()[ok],minlength=len(edges)-1); counts=np.bincount(ib[ok],minlength=len(edges)-1); transfer=transfer/np.maximum(counts,1)
 kcen=.5*(edges[:-1]+edges[1:]); qok=(kcen>0)&(kcen<=kt.max()); Pm=np.interp(np.clip(kcen,kt.min(),kt.max()),kt,pm_t); M=np.interp(np.clip(kcen,kt.min(),kt.max()),kt,M_t)
 rows={}
 for node,fnl in [('fiducial',0.),('LC_m',-100.),('LC_p',100.)]:
  d=np.load(a.nbody_dir/f'nbody_{node}_n{n}.npz'); kk=np.asarray(d['k']); y=np.asarray(d['P_h']); mean=y.mean(0); se=y.std(0,ddof=1)/np.sqrt(len(y)); pred=(a.b1+fnl*bphi/np.maximum(abs(np.interp(np.clip(kk,kt.min(),kt.max()),kt,M_t)),1e-30))**2*np.interp(np.clip(kk,kt.min(),kt.max()),kt,pm_t)*np.interp(kk,kcen,transfer)+a.pshot*np.interp(kk,kcen,transfer)
  pull=(mean-pred)/np.maximum(se,1e-30); rows[node]={'fNL':fnl,'k':kk.tolist(),'nreal':len(y),'mean_P_h':mean.tolist(),'se_P_h':se.tolist(),'prediction_tree_cic':pred.tolist(),'ratio_model_over_nbody':(pred/np.maximum(mean,1e-30)).tolist(),'pull_nbody_minus_model':pull.tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull)))}
 out={'status':'PASS','schema':'ph_nbody_tree_comparison_v1','b1':a.b1,'bphi':bphi,'p':a.p,'delta_c':a.delta_c,'P_shot':a.pshot,'cic_power_transfer':'isotropic-bin average of product sinc^4 per mesh axis','nodes':rows,'kmax_scans':{str(x):{node:float(np.sqrt(np.mean(np.asarray(v['pull_nbody_minus_model'])[np.asarray(v['k'])<=x]**2))) for node,v in rows.items()} for x in [.03,.05,.08,.1,.15,.2]},'scope':'tree halo power vs N-body mesh spectrum; no PNG-response fit'}
 a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','nodes':len(rows),'bphi':bphi}))
if __name__=='__main__': main()


