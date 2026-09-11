#!/usr/bin/env python3
"""Measure exact frozen mu1/mu2 for disjoint reconstructed PNG catalogs."""
import argparse, json, time
from pathlib import Path
import numpy as np
from moments import measure

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--catalog-root',type=Path,required=True); ap.add_argument('--output-root',type=Path,required=True); ap.add_argument('--nodes',nargs='+',default=['LC_m','LC_p']); ap.add_argument('--start',type=int,default=100); ap.add_argument('--stop',type=int,default=500); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--boxsize',type=float,default=1000.); ap.add_argument('--smin',type=float,default=40.); ap.add_argument('--smax',type=float,default=300.); ap.add_argument('--ds',type=float,default=20.); a=ap.parse_args()
 if a.start < 100 or a.stop <= a.start or not set(a.nodes).issubset({'LC_m','LC_p'}): raise ValueError('Use only nonempty disjoint LC_m/LC_p blocks starting at real100 or later')
 ss=np.arange(a.smin,a.smax+0.1,a.ds); rows={}; t0=time.time(); a.output_root.mkdir(parents=True,exist_ok=True)
 for node in a.nodes:
  ids=[]; mu1=[]; mu2=[]; nh=[]
  for j in range(a.start,a.stop):
   rid=f'real{j:03d}'; p=a.catalog_root/node/rid/'positions_mpc_h.npy'
   if not p.exists(): raise FileNotFoundError(p)
   m1,m2=measure(np.load(p,mmap_mode='r'),a.boxsize,a.nmesh,ss,20.)
   ids.append(rid); mu1.append(m1); mu2.append(m2); nh.append(int(np.load(p,mmap_mode='r').shape[0]))
  out=a.output_root/f'moments_{node}_n{a.nmesh}_disjoint.npz'; np.savez_compressed(out,realization_ids=np.asarray(ids),s=ss,mu1=np.asarray(mu1),mu2=np.asarray(mu2),nmesh=a.nmesh,boxsize=a.boxsize,shell_width=20.,fNL=(-100. if node=='LC_m' else 100.),n_halo=np.asarray(nh))
  rows[node]={'nreal':len(ids),'first':ids[0],'last':ids[-1],'n_halo_min':min(nh),'n_halo_max':max(nh),'output':str(out)}
 meta={'status':'PASS','schema':'disjoint_png_moments_v1','catalog_root':str(a.catalog_root),'output_root':str(a.output_root),'nodes':rows,'start':a.start,'stop':a.stop,'nmesh':a.nmesh,'boxsize_mpc_h':a.boxsize,'s':ss.tolist(),'scope':'disjoint LC_m/LC_p response measurement; no heldout frozen IDs used','elapsed_seconds':time.time()-t0}; (a.output_root/'disjoint_png_moments_v1.json').write_text(json.dumps(meta,indent=2)+'\n'); print(json.dumps({'status':'PASS','nodes':rows,'elapsed_seconds':meta['elapsed_seconds']}))
if __name__=='__main__': main()
