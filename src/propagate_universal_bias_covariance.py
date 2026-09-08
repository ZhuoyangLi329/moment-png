#!/usr/bin/env python3
"""Delta-method propagation from (b1, delta_c, p) to bphi and mu1."""
import argparse,json
from pathlib import Path
import numpy as np
from theory_mu1_marisa_b import predict

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--b1-sigma',type=float,required=True); ap.add_argument('--delta-c',type=float,default=1.686); ap.add_argument('--delta-c-sigma',type=float,default=.001); ap.add_argument('--p',type=float,default=1.12); ap.add_argument('--p-sigma',type=float,default=.05); ap.add_argument('--pshot',type=float,default=0.); ap.add_argument('--cell',type=float,default=15.625); a=ap.parse_args()
    x=np.array([a.b1,a.delta_c,a.p],float); C=np.diag([a.b1_sigma**2,a.delta_c_sigma**2,a.p_sigma**2]); d=np.load(a.input); kv=np.asarray(d['kvecs']); pm=np.asarray(d['Pm']); M=np.asarray(d['M']); ss=np.arange(40.,300.1,20.)
    def bphi(z): return 2*z[1]*(z[0]-z[2])
    bp=float(bphi(x)); Jbp=np.array([2*x[1],2*(x[0]-x[2]),-2*x[1]])
    T=np.array([[1.,0.,0.],[Jbp[0],Jbp[1],Jbp[2]]]); outcov=T@C@T.T
    nodes={}
    for fnl in [0.,-100.,100.]:
        def f(z): return np.array([predict(kv,pm,M,float(z[0]),float(bphi(z)),fnl,a.pshot,a.box if hasattr(a,'box') else 1000.,s=s,width=20.,cell=a.cell)[0] for s in ss])
        mean=f(x); J=np.empty((len(ss),3))
        for i in range(3):
            h=1e-5*max(1.,abs(x[i])); xp=x.copy(); xm=x.copy(); xp[i]+=h; xm[i]-=h; J[:,i]=(f(xp)-f(xm))/(2*h)
        V=J@C@J.T; nodes[str(int(fnl))]={'fNL':fnl,'s':ss.tolist(),'mu1_mean':mean.tolist(),'mu1_sigma':np.sqrt(np.maximum(np.diag(V),0)).tolist(),'mu1_covariance':V.tolist(),'jacobian_input':J.tolist()}
    out={'status':'ASSUMPTION_ONLY','schema':'analytic_input_covariance_v2','input_parameters':['b1','delta_c','p'],'input_mean':x.tolist(),'input_covariance':C.tolist(),'derived_bphi':bp,'derived_bphi_jacobian':Jbp.tolist(),'derived_covariance_b1_bphi':outcov.tolist(),'nodes':nodes,'pshot':a.pshot,'window':{'nmesh':64,'cell':a.cell,'s':'40--300 step20'},'method':'central finite-difference delta method','scope':'universal mass-function branch; uncertainty propagation diagnostic only','warning':'The p and delta_c uncertainties are declared sensitivity assumptions and bphi has no independent calibration; production promotion is forbidden.'}
    a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'bphi':bp,'sigma_bphi':float(np.sqrt(outcov[1,1]))}))
if __name__=='__main__': main()
