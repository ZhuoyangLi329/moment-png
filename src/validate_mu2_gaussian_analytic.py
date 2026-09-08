#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--prediction',type=Path,required=True); ap.add_argument('--data-root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); p=json.loads(a.prediction.read_text()); model=np.array([x['mu2_gaussian'] for x in p['predictions']],float); s=np.array([x['s'] for x in p['predictions']],float); rows={}
 for node in ['fiducial','LC_m','LC_p']:
  d=np.load(a.data_root/f'connected_{node}_n64.npz'); z=np.asarray(d['mu2_gaussian'],float); mean=z.mean(0); se=z.std(0,ddof=1)/np.sqrt(len(z)); pull=(mean-model)/np.maximum(se,1e-30); cov=np.cov(z,rowvar=False,ddof=1)/len(z); r=mean-model; chi=float(r@np.linalg.pinv(cov,rcond=1e-10)@r); rows[node]={'fNL':float(d['fNL']),'nreal':len(z),'mean_mu2_gaussian':mean.tolist(),'se':se.tolist(),'pull':pull.tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull))),'chi2':chi,'dof':len(r),'chi2_dof':chi/len(r),'coverage_fraction_abs_pull_le_2':float(np.mean(np.abs(pull)<=2))}
 out={'status':'PASS','schema':'mu2_gaussian_analytic_validation_v1','prediction':str(a.prediction),'s':s.tolist(),'nodes':rows,'scope':'analytic Gaussian halo mu2 versus Nbody Gaussian component; no PNG response fit','warning':'Continuous-shell analytic baseline is diagnostic; contact/repeated-index/clustered terms and finite-mesh convention are not included.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','chi2_dof':{k:round(v['chi2_dof'],2) for k,v in rows.items()}}))
if __name__=='__main__': main()
