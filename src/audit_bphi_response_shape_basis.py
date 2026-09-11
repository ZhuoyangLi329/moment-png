#!/usr/bin/env python3
"""Diagnostic-only basis expansion for the disjoint PNG response shape."""
import argparse,datetime,hashlib,json
from pathlib import Path
import numpy as np

def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def gls(B,y,C):
 P=np.linalg.pinv(C,rcond=1e-10); u,s,v=np.linalg.svd(C); rank=int(np.sum(s>s[0]*1e-10)) if len(s) else 0; G=B@P@B.T; coeff=np.linalg.pinv(G,rcond=1e-10)@(B@P@y); res=y-coeff@B; chi=float(res@P@res); return {'coefficients':coeff.tolist(),'chi2':chi,'dof':max(rank-B.shape[0],1),'chi2_dof':chi/max(rank-B.shape[0],1),'covariance_rank':rank}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--moments-root',type=Path,required=True);ap.add_argument('--theory',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();inp=np.load(a.theory);kv=np.asarray(inp['kvecs'],float);pm=np.asarray(inp['Pm'],float);M=np.asarray(inp['M'],float);sc=np.arange(40.,300.1,20.);cell=1000./64.;transfer=np.sinc(kv[:,0]*cell/(2*np.pi))**4*np.sinc(kv[:,1]*cell/(2*np.pi))**4*np.sinc(kv[:,2]*cell/(2*np.pi))**4
 from exact_window import mu1_discrete
 b1=2.7317333004945543;T=np.array([mu1_discrete(kv,2*b1*pm*transfer/np.maximum(np.abs(M),1e-30),float(s),width=20.,boxsize=1000.,cell=cell,nmesh=64,power_convention='mesh') for s in sc]); minus_path=a.moments_root/'moments_LC_m_n64_disjoint.npz';plus_path=a.moments_root/'moments_LC_p_n64_disjoint.npz';minus=np.load(minus_path);plus=np.load(plus_path);resp=(np.asarray(plus['mu1'],float)-np.asarray(minus['mu1'],float))/200.;y=resp.mean(0);C=np.cov(resp,rowvar=False,ddof=1)/len(resp);x=sc/100.;bases={'template':np.array([T]),'template_plus_logtilt':np.array([T,T*np.log(x)]),'template_plus_inverse_s2':np.array([T,(x**-2)*T[0]]),'template_plus_poly_residual':np.array([T,np.ones_like(x)*T[0],x*x*T[0]])};fits={k:gls(B,y,C) for k,B in bases.items()};out={'status':'DIAGNOSTIC','schema':'bphi_response_shape_basis_audit_v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nreal':len(resp),'s':sc.tolist(),'b1_conditioning':b1,'response_definition':'(LC_p-LC_m)/200','fits':fits,'response_mean':y.tolist(),'response_se':np.sqrt(np.diag(C)).tolist(),'template':T.tolist(),'inputs':{'theory':str(a.theory),'theory_sha256':sha(a.theory),'LC_m':str(minus_path),'LC_m_sha256':sha(minus_path),'LC_p':str(plus_path),'LC_p_sha256':sha(plus_path)},'policy':{'production_promotion':False,'empirical_basis_only':True,'independent_b1_uncertainty_omitted':True,'basis_interpretation':'shape stress tests, not halo bias operators'},'warning':'Lower chi2 from flexible bases does not establish bphi_delta or a production four-point theory.'};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'chi2_dof':{k:round(v['chi2_dof'],2) for k,v in fits.items()}}))
if __name__=='__main__':main()
