#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--nmesh',type=int,default=64); a=ap.parse_args()
 a.output.mkdir(parents=True,exist_ok=True); rows={}; project=a.root.parent
 for node in ('fiducial','LC_m','LC_p'):
  m=np.load(a.root/f'moments_{node}_n{a.nmesh}.npz'); cp=project/'resolution_clean'/f'connected_{node}_n{a.nmesh}.npz'; c=np.load(cp) if cp.exists() else None; p=np.load(a.root/f'power_{node}_n{a.nmesh}.npz')
  ids=np.asarray(m['realization_ids']).astype(str)
  if not np.array_equal(ids,np.asarray(p['realization_ids']).astype(str)): raise ValueError(f'ID mismatch {node}')
  if c is not None and len(c['mu2'])==len(ids):
   mu2g=np.asarray(c['mu2_gaussian']); mu2c=np.asarray(c['mu2_connected'])
  else: mu2g=np.full_like(m['mu2'],np.nan); mu2c=np.full_like(m['mu2'],np.nan)
  R=m['mu2']/np.maximum(mu2g,1e-30)
  np.savez(a.output/f'nbody_{node}_n{a.nmesh}.npz',fNL=m['fNL'],realization_ids=ids,s=m['s'],k=p['k'],P_h=p['P'],nmodes=p['nmodes'],mu1=m['mu1'],mu2=m['mu2'],mu2_gaussian=mu2g,mu2_connected=mu2c,R_mu2=R)
  rows[node]={'fNL':float(m['fNL']),'nreal':len(ids),'n_s':int(len(m['s'])),'n_k':int(len(p['k'])),'has_mu2_gaussian':bool(np.isfinite(mu2g).all())}
 json.dump({'schema':'nbody_baseline_v1','nmesh':a.nmesh,'nodes':rows,'scope':'packaging of canonical realization products; no PNG response fit'},open(a.output/'manifest.json','w'),indent=2); print({'status':'PASS','nodes':len(rows),'nmesh':a.nmesh})
if __name__=='__main__': main()



