#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--nbody-dir',type=Path,required=True); ap.add_argument('--prediction-dir',type=Path,required=True); ap.add_argument('--holdout-start',type=int,default=70); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 mapping={'fiducial':0,'LC_m':-100,'LC_p':100}; rows={}
 for node,fnl in mapping.items():
  d=np.load(a.nbody_dir/f'nbody_{node}_n64.npz'); y=np.asarray(d['mu1'],float); z=y[a.holdout_start:]; mean=z.mean(0); cov=np.cov(z,rowvar=False,ddof=1)/len(z); p=json.loads((a.prediction_dir/f'mu1_universal_p112_exact_n64_fnl{fnl}.json').read_text()); s=np.array([x['s'] for x in p['predictions']],float); model=np.array([x['mu1'] for x in p['predictions']],float); r=mean-model; prec=np.linalg.pinv(cov,rcond=1e-10); pull=r/np.sqrt(np.maximum(np.diag(cov),1e-30)); rows[node]={'fNL':fnl,'n_holdout':len(z),'s':s.tolist(),'mean_mu1':mean.tolist(),'model_mu1':model.tolist(),'se_mean':np.sqrt(np.diag(cov)).tolist(),'pull':pull.tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull))),'chi2':float(r@prec@r),'dof':int(len(r)),'chi2_dof':float(r@prec@r/len(r)),'covariance_condition_number':float(np.linalg.cond(cov)),'covariance_inverse':'pinv_rcond_1e-10'}
 out={'status':'PASS','schema':'mu1_nbody_tree_validation_v1','model':'tree exact discrete mesh + universal bphi p=1.12','nbody_dir':str(a.nbody_dir),'prediction_dir':str(a.prediction_dir),'holdout_start':a.holdout_start,'nodes':rows,'scope':'node-matched N-body held-out mean validation; no response fitting','policy':{'same_split_all_nodes':True,'png_response_fit':False,'scale_list_frozen':True}}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print({'status':'PASS','chi2_dof':{n:round(v['chi2_dof'],2) for n,v in rows.items()}})
if __name__=='__main__': main()


