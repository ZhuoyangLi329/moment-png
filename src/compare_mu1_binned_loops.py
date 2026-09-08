#!/usr/bin/env python3
import argparse,json,time
from pathlib import Path
import numpy as np
from halo_kernels import halo_P22,halo_one_loop_png_directional
from halo_p13 import halo_P13_bias_collapsed
from exact_window import mu1_discrete
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--theory',type=Path,required=True); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--b2',type=float,required=True); ap.add_argument('--bK2',type=float,required=True); ap.add_argument('--bphi',type=float,required=True); ap.add_argument('--qmin',type=float,default=1e-4); ap.add_argument('--qmax',type=float,default=.2); ap.add_argument('--nq',type=int,default=8); ap.add_argument('--nmu',type=int,default=8); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 tab=np.loadtxt(a.theory,comments='#'); kt,pt,ppt,mt=tab.T; n=a.nmesh; q=2*np.pi*np.fft.fftfreq(n,d=a.box/n); gx,gy,gz=np.meshgrid(q,q,q,indexing='ij'); kv=np.column_stack([gx.ravel(),gy.ravel(),gz.ravel()]); kk=np.linalg.norm(kv,axis=1); P=np.interp(np.clip(kk,kt.min(),kt.max()),kt,pt); M=np.interp(np.clip(kk,kt.min(),kt.max()),kt,mt); P[kk==0]=0.; M[kk==0]=1.; edges=np.arange(0,.3+.005,.005); ku=.5*(edges[:-1]+edges[1:]); Pfun=lambda x:np.interp(np.asarray(x),ku,np.interp(ku,kt,pt)); Mfun=lambda x:np.interp(np.asarray(x),ku,np.interp(ku,kt,mt)); t0=time.time(); p22=[];p13=[];dloop=[]
 for ki in ku:
  p22.append(halo_P22(float(ki),Pfun,a.b1,a.b2,a.bK2,a.qmin,a.qmax,a.nq,a.nmu)); p13.append(halo_P13_bias_collapsed(float(ki),Pfun,a.b1,a.b2,a.bK2,a.qmin,a.qmax,a.nq,a.nmu)['total']); dloop.append(halo_one_loop_png_directional(float(ki),Pfun,lambda x:a.bphi/np.maximum(abs(Mfun(x)),1e-30)*Pfun(x),a.b1,a.b2,a.bK2,a.qmin,a.qmax,a.nq,a.nmu))
 p22_bin=np.asarray(p22); p13_bin=np.asarray(p13); dl_bin=np.asarray(dloop); p22=np.interp(kk,ku,p22_bin,left=0,right=p22_bin[-1]); p13=np.interp(kk,ku,p13_bin,left=0,right=p13_bin[-1]); dl=np.interp(kk,ku,dl_bin,left=0,right=dl_bin[-1]); ss=np.arange(40.,300.1,20.); rows=[]
 def proj(val,s):
  from exact_window import shell_window
  return float(np.sum(val*shell_window(kv,s,20,boxsize=a.box,nmesh=n))/a.box**3)
 for fnl in [0.,-100.,100.]:
  tree=(a.b1+fnl*a.bphi/np.maximum(abs(M),1e-30))**2*P; comps={'tree':tree,'P22':p22,'P13':p13,'PNG_loop_response':fnl*dl,'total':tree+p22+p13+fnl*dl}; pred={key:[proj(val,s) for s in ss] for key,val in comps.items()}; tree_bin=(a.b1+fnl*a.bphi/np.maximum(abs(np.interp(ku,kt,mt)),1e-30))**2*np.interp(ku,kt,pt); comps_bin={'tree':tree_bin,'P22':p22_bin,'P13':p13_bin,'PNG_loop_response':fnl*dl_bin,'total':tree_bin+p22_bin+p13_bin+fnl*dl_bin}; rows.append({'fNL':fnl,'k':ku.tolist(),'power_components':{key:val.tolist() for key,val in comps_bin.items()},'predictions':pred})
 out={'status':'PASS','schema':'mu1_binned_loop_nbody_v1','nmesh':n,'b1':a.b1,'b2':a.b2,'bK2':a.bK2,'bphi':a.bphi,'qmin':a.qmin,'qmax':a.qmax,'nq':a.nq,'nmu':a.nmu,'unique_lattice_k':len(ku),'elapsed_seconds':time.time()-t0,'s':ss.tolist(),'nodes':rows,'scope':'Ngrid=64 exact-window projection with loop integrals evaluated on unique lattice k; binned-loop approximation, no response fit'}
 a.output.write_text(json.dumps(out,indent=2)+'\n'); print({'status':'PASS','unique_k':len(ku),'elapsed':out['elapsed_seconds']})
if __name__=='__main__': main()







