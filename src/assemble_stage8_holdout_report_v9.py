#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=a.root;out=json.loads((r/'results/stage8_holdout_validation_report_v8.json').read_text());out['schema']='stage8_holdout_validation_report_v9';out['status']='REJECTED_DIAGNOSTIC';d=json.loads((r/'results/b1_pshot_covariance_scan_v1.json').read_text());f=d['kmax_scan'];out['covariance_aware_b1_pshot_scan']={'full_kmax003':f['0.03']['full'],'full_kmax_scan':{k:v['full'] for k,v in f.items()},'source_sha256':sha(r/'results/b1_pshot_covariance_scan_v1.json')};out['rejection_reasons']=list(dict.fromkeys(out.get('rejection_reasons',[])+['covariance-aware b1/Pshot scan rejects the full disjoint input already at kmax=.03, while b1/Pshot correlation is nearly -1']));out['source_sha256']['stage8_v8']=sha(r/'results/stage8_holdout_validation_report_v8.json');out['source_sha256']['b1_pshot_covariance_scan']=sha(r/'results/b1_pshot_covariance_scan_v1.json');a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'chi2_dof':f['0.03']['full']['chi2_dof']}))
if __name__=='__main__':main()
