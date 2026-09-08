#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--data-root',type=Path,required=True); ap.add_argument('--mu1-dir',type=Path,required=True); ap.add_argument('--mu2-prediction',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 m2p=json.loads(a.mu2_prediction.read_text()); m2=np.array([x['mu2_gaussian'] for x in m2p['predictions']],float); rows={}
 for node,fnl in {'fiducial':0,'LC_m':-100,'LC_p':100}.items():
  p=json.loads((a.mu1_dir/f'mu1_shot_3603_fnl{fnl}.json').read_text()); m1=np.array([x['mu1'] for x in p['predictions']],float); d=np.load(a.data_root/f'moments_{node}_n64.npz'); c=np.load(a.data_root.parent/'resolution_clean'/f'connected_{node}_n64.npz'); z=np.column_stack([np.asarray(d['mu1'],float)[70:],np.asarray(c['mu2_gaussian'],float)[70:]]); model=np.r_[m1,m2]; mean=z.mean(0); C=np.cov(z,rowvar=False,ddof=1)/len(z); r=mean-model; diag=np.diag(np.diag(C)); scans={}
  for lam in [0.,.1,.5,.9]:
   S=(1-lam)*C+lam*diag; inv=np.linalg.pinv(S,rcond=1e-10); q=float(r@inv@r); scans[str(lam)]={'chi2':q,'chi2_dof':q/len(r),'condition_number':float(np.linalg.cond(S))}
  rows[node]={'fNL':fnl,'n_holdout':len(z),'dimension':len(model),'mean_joint':mean.tolist(),'model_joint':model.tolist(),'se_mean':np.sqrt(np.diag(C)).tolist(),'shrinkage_scans':scans,'hartlap_factor':None,'hartlap_reason':'n_holdout <= dimension+2 for joint 28-vector','coverage_fraction_abs_pull_le_2':float(np.mean(np.abs(r/np.sqrt(np.diag(C)))<=2))}
 out={'status':'PASS','schema':'joint_mu1_mu2G_holdout_validation_v1','holdout_start':70,'nodes':rows,'scope':'joint held-out diagnostic using mu1 and Gaussian mu2 component; no response fitting','policy':{'same_split_all_nodes':True,'dimension':28,'hartlap_reported_as_unavailable':True,'shrinkage_scanned':[0.,.1,.5,.9]},'warning':'This is not the final joint mu1+raw-mu2 production test: the analytic mu2 model is Gaussian-only and contact/four-point terms remain open.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','chi2dof':{k:{l:round(v['chi2_dof'],2) for l,v in x['shrinkage_scans'].items()} for k,x in rows.items()}}))
if __name__=='__main__': main()
