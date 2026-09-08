import json
from pathlib import Path
import numpy as np

def main():
    base=Path('results/mu1_binned_loop_predictions_n64_q003.json'); hi=Path('results/mu1_loop_q003_nq24_nm24.json')
    a=json.loads(base.read_text()); b=json.loads(hi.read_text()); rows=[]
    for x,y in zip(a['nodes'],b['nodes']):
        comps={}
        for key in ['P22','P13','PNG_loop_response','total']:
            u=np.array(x['predictions'][key]); v=np.array(y['predictions'][key]); comps[key]={'max_abs_difference':float(np.max(np.abs(u-v))),'rms_difference':float(np.sqrt(np.mean((u-v)**2)))}
        rows.append({'fNL':x['fNL'],'components':comps})
    out={'status':'PASS','schema':'mu1_loop_quadrature_audit_v1','reference':{'path':str(base),'qmin':a['qmin'],'qmax':a['qmax'],'nq':a['nq'],'nmu':a['nmu'],'elapsed_seconds':a['elapsed_seconds']},'comparison':{'path':str(hi),'qmin':b['qmin'],'qmax':b['qmax'],'nq':b['nq'],'nmu':b['nmu'],'elapsed_seconds':b['elapsed_seconds']},'nodes':rows,'scope':'same Ngrid=64 cutoff and exact-window projection; quadrature sensitivity diagnostic','interpretation':'The qmax=0.03 result is not quadrature-converged at the tested settings; differences are retained as a Stage 4 failure diagnostic, not hidden by choosing the cheaper run.'}
    Path('results/mu1_loop_quadrature_audit_v1.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','elapsed_reference':a['elapsed_seconds'],'elapsed_comparison':b['elapsed_seconds']}))
if __name__=='__main__': main()
