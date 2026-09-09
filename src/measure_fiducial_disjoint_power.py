#!/usr/bin/env python3
"""Measure a disjoint fiducial full-lattice CIC power block for b1 audit."""
import argparse,json
from pathlib import Path
import numpy as np
from moments import cic_mesh
from exact_window import mesh_wavevectors

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--catalog-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--start',type=int,default=100);ap.add_argument('--stop',type=int,default=200);ap.add_argument('--nmesh',type=int,default=64);a=ap.parse_args();L=1000.;V=L**3;n=a.nmesh;kv=mesh_wavevectors(n,L);rows=[];ids=[]
 for j in range(a.start,a.stop):
  rid=f'real{j:03d}';p=a.catalog_root/'fiducial'/rid/'positions_mpc_h.npy'
  if not p.exists():continue
  d=cic_mesh(np.load(p,mmap_mode='r'),n,L);dk=np.fft.fftn(d);power=V/n**6*np.abs(dk.ravel())**2;power[0]=0.;rows.append(power);ids.append(rid)
 a.output.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.output,kvecs=kv,Pmode=np.asarray(rows),realization_ids=np.asarray(ids),nmesh=n,boxsize=L)
 out={'status':'PASS','schema':'disjoint_fiducial_mode_power_v1','node':'fiducial','nmesh':n,'boxsize_mpc_h':L,'start':a.start,'stop':a.stop,'nreal':len(ids),'realization_ids':ids,'power_normalization':'V/Nmesh^6 |FFT(delta_CIC)|^2; zero mode set to zero','scope':'disjoint Gaussian fiducial b1/P_h calibration audit; no PNG response fit','output':str(a.output)};a.output.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','nreal':len(ids),'first':ids[:1],'last':ids[-1:] if ids else []}))
if __name__=='__main__':main()
