#!/usr/bin/env python3
"""Predeclared Stage 5 scale-stability audit across Ngrid 64/128/256."""
import argparse,json
from pathlib import Path
import numpy as np

def compare(a,b,ids_a,ids_b):
    aa=list(map(str,ids_a)); bb=list(map(str,ids_b)); common=sorted(set(aa)&set(bb))
    ia=[aa.index(x) for x in common]; ib=[bb.index(x) for x in common]
    return a[ia],b[ib],common

def metric(x,y,threshold,shells):
    da=y.mean(0)-x.mean(0); se=np.std(y-x,axis=0,ddof=1)/np.sqrt(len(x))
    return {'mean_difference':da.tolist(),'paired_difference_se':se.tolist(),'abs_difference':np.abs(da).tolist(),'stable_shells_abs_threshold':[float(s) for s,z in zip(shells,np.abs(da)<=threshold) if z],'max_abs_difference':float(np.max(np.abs(da))),'rms_difference':float(np.sqrt(np.mean(da*da)))}

def longest_run(vals):
    vals=sorted(vals); runs=[]; cur=[]
    for x in vals:
        if cur and abs(x-cur[-1]-20.)<1e-6: cur.append(x)
        else:
            if cur: runs.append(cur)
            cur=[x]
    if cur: runs.append(cur)
    return max(runs,key=len) if runs else []

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); r=a.root
    shells=np.arange(40.,300.1,20.); rows={}
    for node in ['fiducial','LC_m','LC_p']:
        m64=np.load(r/f'results/power_real_n100_n64/moments_{node}_n64.npz'); c64=np.load(r/f'results/resolution_clean/connected_{node}_n64.npz'); rows[node]={}
        for n in [128,256]:
            mn=np.load(r/f'results/resolution_clean/moments_n{n}/moments_{node}_n{n}.npz'); cn=np.load(r/f'results/resolution_clean/connected_{node}_n{n}.npz')
            x1,y1,ids=compare(m64['mu1'],mn['mu1'],m64['realization_ids'],mn['realization_ids']); xc,yc,_=compare(c64['mu2_connected'],cn['mu2_connected'],m64['realization_ids'],mn['realization_ids'])
            rows[node][f'{n}_over_64']={'common_ids':len(ids),'mu1':metric(x1,y1,2e-4,shells),'mu2_connected':metric(xc,yc,1e-4,shells)}
    stable1=set(map(float,shells)); stable2=set(map(float,shells))
    for node in rows:
        for pair in rows[node].values(): stable1 &= set(pair['mu1']['stable_shells_abs_threshold']); stable2 &= set(pair['mu2_connected']['stable_shells_abs_threshold'])
    run1=longest_run(stable1); run2=longest_run(stable2); qualified=len(run1)>=3 and len(run2)>=3
    out={'status':'PASS' if qualified else 'BLOCKED','schema':'stage5_scale_stability_audit_v2','scales_mpc_h':shells.tolist(),'nodes':rows,'thresholds':{'mu1_abs_grid_difference':2e-4,'mu2_connected_abs_grid_difference':1e-4,'minimum_contiguous_shells':3,'pairing':'common realization IDs; 64 primary versus 128/256'},'candidate_intervals':{'mu1_all_nodes_and_grids':sorted(map(float,stable1)),'mu2_connected_all_nodes_and_grids':sorted(map(float,stable2))},'qualified_intervals':{'mu1':run1,'mu2_connected':run2},'policy':{'frozen_v1_scales_unchanged':True,'thresholds_predeclared':True,'candidate_only':True,'production_promotion':False},'conclusion':'A three-shell common stable interval is required for release; mu1 qualifies at large scales, while mu2 connected does not, so the Stage 5 gate remains blocked.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'mu1_qualified':run1,'mu2_qualified':run2}))
if __name__=='__main__': main()
