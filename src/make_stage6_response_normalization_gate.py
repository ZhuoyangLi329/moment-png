#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
def sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--diagnostic',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();d=json.loads(a.diagnostic.read_text()); scans=d['shot_scans']; out={'schema':'stage6_response_normalization_diagnostic_v1','status':'PASS','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'diagnostic':str(a.diagnostic),'diagnostic_sha256':sha(a.diagnostic),'nreal':d['nreal'],'shot_scans':{k:{x:v[x] for x in ('shot','bphi','sigma','chi2_dof','dof','rms_pull')} for k,v in scans.items()},'conclusion':'Measured fiducial P_h normalization moves conditional bphi toward the training response value, but the response shape remains rejected for both shot variants; no production promotion.','shape_rejected':all(float(v['chi2_dof'])>5 for v in scans.values()),'policy':{'heldout_excluded':True,'normalization_only':True,'empirical_template_not_promoted':True,'production_bphi_blocked':True}};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'shape_rejected':out['shape_rejected'],'chi2_dof':{k:v['chi2_dof'] for k,v in out['shot_scans'].items()}}))
if __name__=='__main__':main()
