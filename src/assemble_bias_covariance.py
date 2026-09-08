#!/usr/bin/env python3
import json,glob
from pathlib import Path
import numpy as np

def main():
    d=Path('results/power_real_n100_n64'); b1=2.7813407736; sb1=.00171; dc=1.686; sdc=.001; p=1.12; sp=.05; bp=2*dc*(b1-p); sbp=float(np.sqrt((2*dc*sb1)**2+(2*(b1-p)*sdc)**2+(2*dc*sp)**2)); outnodes={}
    for fnl in [0,-100,100]:
      base=json.load(open(d/f'mu1_prop_base_fnl{fnl}.json')); plus=json.load(open(d/f'mu1_prop_b1plus_fnl{fnl}.json')); minus=json.load(open(d/f'mu1_prop_b1minus_fnl{fnl}.json')); pp=json.load(open(d/f'mu1_prop_bpplus_fnl{fnl}.json')); pm=json.load(open(d/f'mu1_prop_bpminus_fnl{fnl}.json'))
      s=np.array([x['s'] for x in base['predictions']]); y=np.array([x['mu1'] for x in base['predictions']]); jb1=(np.array([x['mu1'] for x in plus['predictions']])-np.array([x['mu1'] for x in minus['predictions']]))/(2*sb1); jbp=(np.array([x['mu1'] for x in pp['predictions']])-np.array([x['mu1'] for x in pm['predictions']]))/(2*sbp); V=sb1**2*np.outer(jb1,jb1)+sbp**2*np.outer(jbp,jbp); outnodes[str(fnl)]={'fNL':fnl,'s':s.tolist(),'mu1_mean':y.tolist(),'mu1_sigma':np.sqrt(np.maximum(np.diag(V),0)).tolist(),'mu1_covariance':V.tolist(),'jacobian_b1':jb1.tolist(),'jacobian_bphi':jbp.tolist()}
    Jbp=[2*dc,2*(b1-p),-2*dc]; C=np.diag([sb1**2,sdc**2,sp**2]); T=np.array([[1,0,0],Jbp]); out={'status':'ASSUMPTION_ONLY','schema':'analytic_input_covariance_v2','input_parameters':['b1','delta_c','p'],'input_mean':[b1,dc,p],'input_covariance':C.tolist(),'derived_bphi':bp,'derived_bphi_sigma':sbp,'derived_bphi_jacobian':Jbp,'derived_covariance_b1_bphi':(T@C@T.T).tolist(),'nodes':outnodes,'pshot':3603,'window':{'nmesh':64,'cell':15.625,'s':'40--300 step20'},'method':'central finite-difference exact-window Jacobian plus delta method','scope':'universal mass-function branch; uncertainty propagation diagnostic only','warning':'p and delta_c uncertainties are declared sensitivity assumptions; bphi has no independent calibration and production promotion is forbidden.'}; Path('results/analytic_input_covariance_v2.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'bphi':bp,'bphi_sigma':sbp}))
if __name__=='__main__': main()
