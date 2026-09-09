#!/usr/bin/env python3
"""Summarize loop IR-cutoff sensitivity including the box fundamental mode."""
import argparse,json
from pathlib import Path
import numpy as np
ap=argparse.ArgumentParser(); ap.add_argument('--baseline',type=Path,required=True); ap.add_argument('--qmin001',type=Path,required=True); ap.add_argument('--fundamental',type=Path,required=True); ap.add_argument('--fund-validation',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
paths=[a.baseline,a.qmin001,a.fundamental]; ds=[json.loads(p.read_text()) for p in paths]
for d in ds:
 if d.get('schema')!='mu1_binned_loop_nbody_v1': raise ValueError('unexpected loop schema')
rows=[]
for d in ds:
 rows.append({'qmin':float(d['qmin']),'qmax':float(d['qmax']),'nq':int(d['nq']),'nmu':int(d['nmu']),'elapsed_seconds':float(d['elapsed_seconds']),'unique_lattice_k':int(d['unique_lattice_k'])})
comparisons=[]
for label,i in [('qmin001',1),('fundamental',2)]:
 comp=[]
 for lo,hi in zip(ds[0]['nodes'],ds[i]['nodes']):
  terms={}
  for key in ['tree','P22','P13','PNG_loop_response','total']:
   x=np.asarray(lo['predictions'][key],float); y=np.asarray(hi['predictions'][key],float); terms[key]={'rms_mu1_difference':float(np.sqrt(np.mean((x-y)**2))),'max_abs_mu1_difference':float(np.max(np.abs(x-y)))}
  comp.append({'fNL':float(lo['fNL']),'terms':terms})
 comparisons.append({'comparison':label,'against_qmin':float(ds[0]['qmin']),'terms':comp})
validation=json.loads(a.fund_validation.read_text())
out={'status':'PASS','schema':'loop_ir_cutoff_fundamental_audit_v1','cutoff_runs':rows,'comparisons':comparisons,'fundamental_nbody_validation':{'path':str(a.fund_validation),'schema':validation.get('schema'),'nodes':{n:{k:v for k,v in x['components']['total'].items() if k in ['power_rms_pull','mu1_rms_pull','mu1_chi2_dof','mu1_coverage_abs_pull_le_2']} for n,x in validation['nodes'].items()}},'scope':'Ngrid=64 exact-window binned loop IR-cutoff diagnostic; no fit or production promotion','policy':{'fundamental_kmin':'2*pi/L','fixed_qmax':True,'fixed_quadrature':True,'same_bias_inputs':True,'production_promotion':False},'conclusion':'The box-fundamental cutoff is retained as a diagnostic anchor; agreement with the qmin=1e-4 run is required before any loop promotion.'}
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','qmins':[r['qmin'] for r in rows],'fund_total_mu1_chi2_dof':{n:round(x['components']['total']['mu1_chi2_dof'],2) for n,x in validation['nodes'].items()}}))

