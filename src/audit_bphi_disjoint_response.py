#!/usr/bin/env python3
"""Audit a disjoint b_phi response fit before any production promotion."""
import argparse, hashlib, json, math
from pathlib import Path

def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--inventory',type=Path,required=True); ap.add_argument('--calibration',type=Path,required=True); ap.add_argument('--job-provenance',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 inv=json.loads(a.inventory.read_text()); cal=json.loads(a.calibration.read_text()); job=json.loads(a.job_provenance.read_text())
 ids=[str(x) for x in cal.get('realization_ids',[])]; expected=[f'real{i:03d}' for i in range(100,500)]
 checks=[]
 checks.append({'name':'inventory_disjoint_pair','status':'PASS' if inv.get('disjoint_png_pair_available') is True and inv.get('decision')=='AVAILABLE_FOR_CALIBRATION' else 'BLOCKED'})
 checks.append({'name':'calibration_schema','status':'PASS' if cal.get('schema') in ('bphi_disjoint_response_calibration_v1','bphi_disjoint_response_calibration_v2','bphi_disjoint_response_calibration_v3') and cal.get('status')=='PASS' else 'BLOCKED'})
 checks.append({'name':'calibration_ids','status':'PASS' if ids==expected and len(ids)==400 else 'BLOCKED','nreal':len(ids),'first':ids[:1],'last':ids[-1:]})
 finite=all(math.isfinite(float(cal.get(k,float('nan')))) for k in ('bphi','bphi_sigma_statistical','chi2_dof'))
 checks.append({'name':'finite_fit_and_error','status':'PASS' if finite and float(cal.get('bphi_sigma_statistical',0))>0 else 'BLOCKED'})
 halves=cal.get('stability_halves',[]); half_delta=abs(float(halves[0].get('bphi_conditional',halves[0].get('bphi')))-float(halves[1].get('bphi_conditional',halves[1].get('bphi')))) if len(halves)==2 else None
 checks.append({'name':'half_block_report','status':'PASS' if len(halves)==2 and half_delta is not None else 'BLOCKED','half_delta':half_delta})
 checks.append({'name':'batch_provenance','status':'PASS' if str(job.get('slurm_job_id','')).isdigit() and job.get('scope') else 'BLOCKED','slurm_job_id':job.get('slurm_job_id')})
 structural='PASS' if all(x['status']=='PASS' for x in checks) else 'BLOCKED'
 chi2_dof=float(cal.get('fit',{}).get('chi2_dof',cal.get('chi2_dof',float('inf'))))
 fit_quality='PASS' if math.isfinite(chi2_dof) and chi2_dof<=5.0 else 'REJECTED_SHAPE'
 checks.append({'name':'predeclared_shape_quality','status':fit_quality,'chi2_dof':chi2_dof,'threshold':5.0})
 status='PASS' if structural=='PASS' and fit_quality=='PASS' else 'BLOCKED'
 decision='CALIBRATION_AVAILABLE_REVIEW_REQUIRED' if status=='PASS' else ('CALIBRATION_SOURCE_AVAILABLE_SHAPE_REJECTED' if structural=='PASS' else 'BLOCKED')
 out={'schema':'bphi_disjoint_response_audit_v2','status':status,'decision':decision,'checks':checks,'bphi':cal.get('bphi_conditional',cal.get('bphi')),'bphi_sigma_statistical':cal.get('bphi_sigma_statistical_conditional',cal.get('bphi_sigma_statistical')),'chi2_dof':chi2_dof,'half_delta':half_delta,'inventory':str(a.inventory),'inventory_sha256':sha(a.inventory),'calibration':str(a.calibration),'calibration_sha256':sha(a.calibration),'job_provenance':str(a.job_provenance),'job_provenance_sha256':sha(a.job_provenance),'scope':'independent/disjoint LC+/- response calibration for the frozen FoF z=1 Mh>=1e13 real-space CIC selection','policy':{'heldout_response_fit':False,'universal_mass_function_not_promoted':True,'production_requires_shape_quality_and_convention':True,'predeclared_shape_threshold_chi2_dof_le_5':True,'freeze_timestamp_recorded':True}}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':status,'decision':out['decision'],'bphi':out['bphi'],'half_delta':half_delta}))
if __name__=='__main__': main()
