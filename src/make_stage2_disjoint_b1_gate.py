#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
def sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fit',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();d=json.loads(a.fit.read_text());f=d['fits']; btrain=2.7340475186190334; b003=float(f['0.03']['b1']); delta=b003-btrain; out={'schema':'stage2_disjoint_b1_gate_v1','status':'DIAGNOSTIC_OPEN','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fit_source':str(a.fit),'fit_sha256':sha(a.fit),'realization_block':d.get('realization_block'),'kmax_scan':{k:{x:v[x] for x in ('b1','b1_sigma_linearized','P_shot','chi2_dof')} for k,v in f.items()},'training_b1_kmax003':btrain,'disjoint_b1_kmax003':b003,'delta_b1_kmax003':delta,'predeclared_tolerance':0.02,'lowk_consistency':'PASS' if abs(delta)<=0.02 else 'BLOCKED','highk_drift':'DIAGNOSTIC_OPEN','conclusion':'The disjoint Gaussian fit is internally good at kmax=.03 but its b1 amplitude differs from the training calibration beyond the frozen tolerance; higher k shows additional nonlinear drift. No PNG response fit or production promotion is allowed.','policy':{'heldout_excluded':True,'png_response_fit':False,'same_cic_convention':True,'production_promotion':False}};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'lowk':out['lowk_consistency'],'delta_b1':delta}))
if __name__=='__main__':main()
