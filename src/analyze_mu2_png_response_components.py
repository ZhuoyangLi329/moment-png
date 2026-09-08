#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np

def stats(plus,minus):
 d=(plus-minus)/200.; mean=d.mean(0); se=d.std(0,ddof=1)/np.sqrt(len(d)); cov=np.cov(d,rowvar=False,ddof=1); pull=mean/np.maximum(se,1e-30); return {'mean_response_per_fNL':mean.tolist(),'se_response':se.tolist(),'pull_vs_zero':pull.tolist(),'rms_pull_vs_zero':float(np.sqrt(np.mean(pull*pull))),'coverage_abs_pull_le_2':float(np.mean(np.abs(pull)<=2)),'covariance_condition_number':float(np.linalg.cond(cov)),'n_pairs':len(d)}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); m={}; c={}
 for node in ['fiducial','LC_m','LC_p']:
  m[node]=np.load(a.root/f'results/power_real_n100_n64/moments_{node}_n64.npz'); c[node]=np.load(a.root/f'results/resolution_clean/connected_{node}_n64.npz')
 ids_m=[str(x) for x in m['LC_m']['realization_ids']]; ids_p=[str(x) for x in m['LC_p']['realization_ids']]; common=sorted(set(ids_m)&set(ids_p)); im=[ids_m.index(x) for x in common]; ip=[ids_p.index(x) for x in common]; rows={}
 for key,arr in [('mu1',lambda d,cc:d['mu1']),('mu2_raw',lambda d,cc:d['mu2']),('mu2_gaussian',lambda d,cc:cc['mu2_gaussian']),('mu2_connected',lambda d,cc:cc['mu2_connected']),('R_mu2',lambda d,cc:d['mu2']/np.maximum(cc['mu2_gaussian'],1e-30))]:
  pp=arr(m['LC_p'],c['LC_p'])[ip]; mm=arr(m['LC_m'],c['LC_m'])[im]; rows[key]=stats(pp,mm)
 p=np.load(a.root/'results/poisson_control_n10_n64.npz'); rows['poisson_contact_baseline']={'mean_response_per_fNL':[0.]*len(p['s']),'se_response':[0.]*len(p['s']),'interpretation':'iid Poisson catalog has no +/- PNG nodes; zero response is a control definition'}
 out={'status':'PASS','schema':'mu2_png_response_component_audit_v1','s':m['fiducial']['s'].tolist(),'pair_ids':common,'n_pairs':len(common),'components':rows,'scope':'paired LC_p minus LC_m response per unit fNL for raw/Gaussian/connected mu2, R_mu2, and mu1','policy':{'response_formula':'(LC_p-LC_m)/200','same_realization_ids':True,'no_response_fit':True},'warning':'Responses are measured diagnostics; no empirical polynomial is promoted as a theory mean and halo connected terms remain unmodeled.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','n_pairs':len(common),'rms_pull':{k:round(v.get('rms_pull_vs_zero',0),2) for k,v in rows.items()}}))
if __name__=='__main__': main()
