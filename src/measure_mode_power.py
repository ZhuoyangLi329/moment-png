#!/usr/bin/env python3
import argparse,json,os,platform
from pathlib import Path
import numpy as np
from moments import cic_mesh
from exact_window import mesh_wavevectors,shell_window

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--catalog-root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--start',type=int,default=70); ap.add_argument('--stop',type=int,default=100); a=ap.parse_args(); a.output.parent.mkdir(parents=True,exist_ok=True); n=a.nmesh; L=1000.; V=L**3; kv=mesh_wavevectors(n,L); rows={}
 for node in ['fiducial','LC_m','LC_p']:
  ids=[]; powers=[]
  for j in range(a.start,a.stop):
   rid=f'real{j:03d}'; f=a.catalog_root/node/rid/'positions_mpc_h.npy'
   if not f.exists(): continue
   d=cic_mesh(np.load(f,mmap_mode='r'),n,L); dk=np.fft.fftn(d); p=V/n**6*np.abs(dk.ravel())**2; p[0]=0.; ids.append(rid); powers.append(p)
  np.savez(a.output.with_name(a.output.stem+f'_{node}_n{n}.npz'),kvecs=kv,Pmode=np.asarray(powers),realization_ids=np.asarray(ids),nmesh=n,boxsize=L)
  rows[node]={'nreal':len(ids),'ids':ids}
 out={'status':'PASS','schema':'mode_power_measurement_v1','nmesh':n,'catalog_root':str(a.catalog_root),'start':a.start,'stop':a.stop,'nodes':rows,'scope':'heldout full lattice CIC power; zero mode removed'}; a.output.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
if __name__=='__main__':main()
