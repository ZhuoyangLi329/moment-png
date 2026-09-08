#!/usr/bin/env python3
"""Compare declared shot-noise conventions in held-out mu1 validation."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.stats import chi2

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--prediction-dir',type=Path,required=True); ap.add_argument('--moments-dir',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    variants={'shot0':0.0,'shot_inv_nbar':5114.24,'shot_fit3603':3603.0}
    nodes={'fiducial':(0,'fnl0'),'LC_m':(-100,'fnl-100'),'LC_p':(100,'fnl100')}; rows={}
    for tag,shot in variants.items():
        rows[tag]={'P_shot':shot,'nodes':{}}
        for node,(fnl,suffix) in nodes.items():
            p=a.prediction_dir/f'mu1_shot_{tag.replace("shot", "")}_{suffix}.json'
            if tag=='shot0': p=a.prediction_dir/f'mu1_shot_0_{suffix}.json'
            if tag=='shot_fit3603': p=a.prediction_dir/f'mu1_shot_3603_{suffix}.json'
            if tag=='shot_inv_nbar': p=a.prediction_dir/f'mu1_shot_5114p24_{suffix}.json'
            pred=json.loads(p.read_text()); model=np.array([x['mu1'] for x in pred['predictions']],float)
            z=np.asarray(np.load(a.moments_dir/f'moments_{node}_n64.npz')['mu1'],float)[70:]; n=len(z); mean=z.mean(0); cov=np.cov(z,rowvar=False,ddof=1)/n; r=mean-model; inv=np.linalg.pinv(cov,rcond=1e-10); c=float(r@inv@r); d=len(r); h=(n-d-2)/(n-1); hc=h*c
            rows[tag]['nodes'][node]={'rms_pull':float(np.sqrt(np.mean((r/np.sqrt(np.diag(cov)))**2))),'chi2_dof':c/d,'hartlap_chi2_dof':hc/d,'hartlap_pvalue':float(chi2.sf(hc,d)),'coverage_fraction_abs_pull_le_2':float(np.mean(np.abs(r/np.sqrt(np.diag(cov)))<=2))}
    out={'status':'PASS','schema':'mu1_shot_noise_variant_audit_v1','holdout':'real070-real099','variants':rows,'scope':'held-out diagnostic only; no response fitting','policy':{'same_split_all_nodes':True,'nbar_inverse':5114.24,'frozen_scales':'40--300 Mpc/h','production_promotion':False},'warning':'P_shot choices are compared as diagnostics; this does not close clustered-contact or full mu2 shot-noise terms.'}
    a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','hartlap_chi2_dof':{k:{n:round(v['hartlap_chi2_dof'],2) for n,v in x['nodes'].items()} for k,x in rows.items()}}))
if __name__=='__main__': main()
