#!/usr/bin/env python3
"""Audit CIC transfer conventions for signed loop-component projections."""
import argparse,json
from pathlib import Path
import numpy as np
from exact_window import mesh_wavevectors,shell_window
ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--loop',type=Path,required=True); ap.add_argument('--nbody',type=Path,required=True); ap.add_argument('--moments',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--pshot',type=float,default=5467.76); a=ap.parse_args()
L=1000.; n=64; h=L/n; V=L**3; ss=np.arange(40.,300.1,20.); kv=mesh_wavevectors(n,L); km=np.linalg.norm(kv,axis=1); W=np.vstack([shell_window(kv,float(s),20.,boxsize=L,nmesh=n) for s in ss]); transfer=np.prod(np.sinc(kv*h/(2*np.pi))**4,axis=1)
loop=json.loads(a.loop.read_text()); variants={'no_transfer_no_shot':(np.ones_like(transfer),0.),'cic_all_no_shot':(transfer,0.),'cic_all_poisson':(transfer,a.pshot),'cic_loop_plain_shot':(transfer,a.pshot)}; rows={}
for node,fnl in [('fiducial',0.),('LC_m',-100.),('LC_p',100.)]:
 ent=next(x for x in loop['nodes'] if float(x['fNL'])==fnl); kb=np.asarray(ent['k'],float); comps={k:np.asarray(ent['power_components'][k],float) for k in ['tree','P22','P13','PNG_loop_response','total']}; nb=np.load(a.nbody/f'nbody_{node}_n64.npz'); obsP=np.asarray(nb['P_h'],float)[70:]; nk=np.asarray(nb['k'],float); obsPm=obsP.mean(0); obsPs=obsP.std(0,ddof=1)/np.sqrt(len(obsP)); mm=np.load(a.moments/f'moments_{node}_n64.npz'); obsM=np.asarray(mm['mu1'],float)[70:]; meanM=obsM.mean(0); seM=obsM.std(0,ddof=1)/np.sqrt(len(obsM)); rows[node]={'fNL':fnl,'n_holdout':len(obsP),'variants':{}}
 for name,(tr,shot) in variants.items():
  if name=='cic_loop_plain_shot': shot_transfer=np.ones_like(transfer)
  else: shot_transfer=tr
  comp_mu={}; comp_pk={}
  for key,val in comps.items():
   grid=np.interp(km,kb,val,left=val[0],right=val[-1]); comp_mu[key]=np.sum(grid*tr[None,:]*W,axis=1)/V; comp_pk[key]=np.interp(nk,kb,val,left=val[0],right=val[-1])
  total_mu=comp_mu['total']+shot*np.sum(shot_transfer[None,:]*W,axis=1)/V; total_pk=comp_pk['total']+shot*np.ones_like(nk)
  rmu=meanM-total_mu; rp=obsPm-total_pk; cm=np.cov(obsM,rowvar=False,ddof=1)/len(obsM); chi=float(rmu@np.linalg.pinv(cm,rcond=1e-10)@rmu); pullm=rmu/np.maximum(seM,1e-30); pullp=rp/np.maximum(obsPs,1e-30)
  rows[node]['variants'][name]={'P_shot':shot,'shot_transfer':'cic_power' if shot_transfer is tr else 'plain_constant','prediction_mu1':total_mu.tolist(),'mu1_rms_pull':float(np.sqrt(np.mean(pullm*pullm))),'mu1_chi2_dof':chi/len(rmu),'mu1_coverage_abs_pull_le_2':float(np.mean(np.abs(pullm)<=2)),'P_h_rms_pull':float(np.sqrt(np.mean(pullp*pullp))),'P_h_ratio_first':float(total_pk[0]/max(abs(obsPm[0]),1e-30)),'component_mu1_rms':{k:float(np.sqrt(np.mean(v*v))) for k,v in comp_mu.items()}}
out={'status':'PASS','schema':'mu1_loop_signed_cic_transfer_audit_v1','nmesh':n,'qmin':float(loop['qmin']),'qmax':float(loop['qmax']),'nq':int(loop['nq']),'nmu':int(loop['nmu']),'P_shot':a.pshot,'nodes':rows,'scope':'signed loop-component CIC transfer diagnostic against heldout Nbody P_h and mu1','policy':{'heldout_ids':'real070-real099','same_window':True,'no_response_fit':True,'production_promotion':False},'warning':'Loop components and bias inputs remain unconverged; this audit does not promote a transfer convention or close Stage 4.'}
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','mu1_rms_pull':{n:{k:round(v['mu1_rms_pull'],2) for k,v in x['variants'].items()} for n,x in rows.items()},'P_h_rms_pull':{n:{k:round(v['P_h_rms_pull'],2) for k,v in x['variants'].items()} for n,x in rows.items()}}))
