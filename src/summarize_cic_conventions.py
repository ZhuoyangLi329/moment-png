import json
from pathlib import Path
import numpy as np

def main():
 d=json.load(open('results/cic_convention_audit_batch_58081876.json')); out={'schema':'cic_convention_summary_v1','source':'results/cic_convention_audit_batch_58081876.json','nodes':{}}
 for node,v in d['nodes'].items():
  c=v['conventions']; row={}
  for mode in ['ngp','cic_deconv']:
   row[mode]={'mu1_rms_abs_difference_vs_cic':float(np.sqrt(np.mean((np.asarray(c[mode]['mean_mu1'])-np.asarray(c['cic']['mean_mu1']))**2))),'mu2_rms_abs_difference_vs_cic':float(np.sqrt(np.mean((np.asarray(c[mode]['mean_mu2'])-np.asarray(c['cic']['mean_mu2']))**2))),'mu1_mean_abs_fractional_vs_cic':float(np.mean(np.abs((np.asarray(c[mode]['mean_mu1'])-np.asarray(c['cic']['mean_mu1']))/np.maximum(np.abs(c['cic']['mean_mu1']),1e-30)))),'mu2_mean_abs_fractional_vs_cic':float(np.mean(np.abs((np.asarray(c[mode]['mean_mu2'])-np.asarray(c['cic']['mean_mu2']))/np.maximum(np.abs(c['cic']['mean_mu2']),1e-30))))}
  out['nodes'][node]=row
 Path('results/cic_convention_summary_58081876.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
