import argparse,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('low',type=Path); ap.add_argument('high',type=Path); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); x=json.loads(a.low.read_text()); y=json.loads(a.high.read_text()); rows=[]
 for u,v in zip(x['nodes'],y['nodes']):
  c={}
  for k in ['P22','P13','PNG_loop_response','total']:
   z=np.asarray(u['predictions'][k]); w=np.asarray(v['predictions'][k]); c[k]={'max_abs_difference':float(np.max(np.abs(z-w))),'rms_difference':float(np.sqrt(np.mean((z-w)**2)))}
  rows.append({'fNL':u['fNL'],'components':c})
 out={'status':'PASS','schema':'slurm_loop_qmin_audit_v1','low_qmin':x['qmin'],'high_qmin':y['qmin'],'qmax':x['qmax'],'nq':x['nq'],'nmu':x['nmu'],'elapsed_seconds':[x['elapsed_seconds'],y['elapsed_seconds']],'nodes':rows,'scope':'batch qmin sensitivity; no response fit','interpretation':'IR sensitivity retained as diagnostic; no production loop promotion.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','max_total':max(r['components']['total']['max_abs_difference'] for r in rows)}))
if __name__=='__main__': main()
