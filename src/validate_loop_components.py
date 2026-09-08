#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--loop',type=Path,required=True); ap.add_argument('--nbody',type=Path,required=True); ap.add_argument('--moments',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); L=json.loads(a.loop.read_text()); rows={}; keys=['tree','P22','P13','PNG_loop_response','total']; mapping={'fiducial':0.,'LC_m':-100.,'LC_p':100.}
 for node,fnl in mapping.items():
  lr=next(x for x in L['nodes'] if float(x['fNL'])==fnl); m=np.load(a.moments/f'moments_{node}_n64.npz'); nb=np.load(a.nbody/f'nbody_{node}_n64.npz'); yh=np.asarray(nb['P_h'],float)[70:]; nk=np.asarray(nb['k'],float); ym0=yh.mean(0); ys0=yh.std(0,ddof=1)/np.sqrt(len(yh)); lk=np.asarray(lr['k'],float); ym=np.interp(lk,nk,ym0); ys=np.interp(lk,nk,ys0); z=np.asarray(m['mu1'],float)[70:]; mm=z.mean(0); ms=z.std(0,ddof=1)/np.sqrt(len(z)); out={}
  for k in keys:
   pv=np.asarray(lr['power_components'][k],float); uv=np.asarray(lr['predictions'][k],float); # loop k bins and Nbody k bins are both 60 at this schema
   if len(pv)!=len(ym): raise ValueError(f'power k mismatch {node}: {len(pv)} vs {len(ym)}')
   phpull=(ym-pv)/np.maximum(ys,1e-30); mupull=(mm-uv)/np.maximum(ms,1e-30); C=np.cov(z,rowvar=False,ddof=1)/len(z); r=mm-uv; chi=float(r@np.linalg.pinv(C,rcond=1e-10)@r)
   out[k]={'power_ratio_first':float(pv[0]/max(abs(ym[0]),1e-30)),'power_rms_pull':float(np.sqrt(np.mean(phpull*phpull))),'mu1_rms_pull':float(np.sqrt(np.mean(mupull*mupull))),'mu1_chi2':chi,'mu1_dof':len(r),'mu1_chi2_dof':chi/len(r),'mu1_coverage_abs_pull_le_2':float(np.mean(np.abs(mupull)<=2))}
  rows[node]={'fNL':fnl,'n_holdout':len(z),'components':out}
 out={'status':'PASS','schema':'loop_component_nbody_validation_v2','loop_source':str(a.loop),'nbody_source':str(a.nbody),'moments_source':str(a.moments),'holdout_start':70,'nodes':rows,'scope':'Ngrid64 batch loop component versus held-out Nbody P_h and mu1; no fitting','warning':'Individual loop pieces are diagnostic components; only the total is a candidate mean, and qmin/quadrature convergence remains open.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','total_mu1_chi2_dof':{n:round(v['components']['total']['mu1_chi2_dof'],2) for n,v in rows.items()}}))
if __name__=='__main__': main()
