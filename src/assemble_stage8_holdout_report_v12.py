#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=a.root;out=json.loads((r/'results/stage8_holdout_validation_report_v11.json').read_text());out['schema']='stage8_holdout_validation_report_v12';out['status']='REJECTED_DIAGNOSTIC';d=json.loads((r/'results/bphi_response_scale_window_scan_v1.json').read_text());best=sorted(d['windows'],key=lambda x:x['hartlap_chi2_dof'])[:5];out['posthoc_bphi_scale_window_diagnostic']={'best_windows':best,'frozen_cut_unchanged':'40--300','source_sha256':sha(r/'results/bphi_response_scale_window_scan_v1.json')};out['rejection_reasons']=list(dict.fromkeys(out.get('rejection_reasons',[])+['post hoc large-s window scan cannot replace the frozen full 40--300 validation cut']));out['source_sha256']['stage8_v11']=sha(r/'results/stage8_holdout_validation_report_v11.json');out['source_sha256']['bphi_response_scale_windows']=sha(r/'results/bphi_response_scale_window_scan_v1.json');a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'best_window':best[0]}))
if __name__=='__main__':main()
