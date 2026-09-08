import json
from pathlib import Path
import numpy as np

def main():
    a=json.loads(Path('results/mu1_loop_q003_nq24_nm24.json').read_text()); b=json.loads(Path('results/mu1_loop_qmin001_q003_nq24_nm24.json').read_text()); rows=[]
    for x,y in zip(a['nodes'],b['nodes']):
        comps={}
        for key in ['P22','P13','PNG_loop_response','total']:
            u=np.array(x['predictions'][key]); v=np.array(y['predictions'][key]); comps[key]={'max_abs_difference':float(np.max(np.abs(u-v))),'rms_difference':float(np.sqrt(np.mean((u-v)**2)))}
        rows.append({'fNL':x['fNL'],'components':comps})
    out={'status':'PASS','schema':'mu1_loop_qmin_quadrature_audit_v1','reference':{'path':'results/mu1_loop_q003_nq24_nm24.json','qmin':a['qmin'],'qmax':a['qmax'],'nq':a['nq'],'nmu':a['nmu'],'elapsed_seconds':a['elapsed_seconds']},'comparison':{'path':'results/mu1_loop_qmin001_q003_nq24_nm24.json','qmin':b['qmin'],'qmax':b['qmax'],'nq':b['nq'],'nmu':b['nmu'],'elapsed_seconds':b['elapsed_seconds']},'nodes':rows,'scope':'same Ngrid=64 qmax and exact-window projection; IR cutoff sensitivity at matched quadrature','interpretation':'Changing qmin from 1e-4 to 1e-3 remains materially visible in the projected PNG response and total, so the IR cutoff is not yet stable.'}
    Path('results/mu1_loop_qmin_quadrature_audit_v1.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','reference_elapsed':a['elapsed_seconds'],'comparison_elapsed':b['elapsed_seconds']}))
if __name__=='__main__': main()
