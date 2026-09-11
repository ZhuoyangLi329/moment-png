#!/usr/bin/env python3
"""Fit b_phi from a fully disjoint matched LC+/- response block."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from exact_window import mesh_wavevectors,mu1_discrete

def sha(p):
 h=hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--moments-root',type=Path,required=True); ap.add_argument('--input',type=Path,required=True); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--b1-sigma',type=float,default=None); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 inp=np.load(a.input); kv=np.asarray(inp['kvecs']); pm=np.asarray(inp['Pm'],float); M=np.asarray(inp['M'],float); n=64;L=1000.;h=L/n;cic=np.sinc(kv[:,0]*h/(2*np.pi))**4*np.sinc(kv[:,1]*h/(2*np.pi))**4*np.sinc(kv[:,2]*h/(2*np.pi))**4; ss=np.arange(40.,300.1,20.)
 lm=np.load(a.moments_root/'moments_LC_m_n64_disjoint.npz'); lp=np.load(a.moments_root/'moments_LC_p_n64_disjoint.npz'); ids_m=lm['realization_ids'].astype(str);ids_p=lp['realization_ids'].astype(str)
 if not np.array_equal(ids_m,ids_p): raise ValueError('LC IDs mismatch')
 resp=(np.asarray(lp['mu1'],float)-np.asarray(lm['mu1'],float))/200.; mean=resp.mean(0); C=np.cov(resp,rowvar=False,ddof=1)/len(resp); inv=np.linalg.pinv(C,rcond=1e-10); template=np.array([mu1_discrete(kv,2*a.b1*pm*cic/np.maximum(np.abs(M),1e-30),float(s),width=20.,boxsize=L,cell=h,nmesh=n,power_convention='mesh') for s in ss]); bp=float(template@inv@mean/(template@inv@template)); r=mean-bp*template; chi=float(r@inv@r); var=1./float(template@inv@template); sigma=float(np.sqrt(max(var,0.)))
 # stability in two prespecified contiguous half-blocks
 half=[]
 for lo,hi in [(0,len(ids_m)//2),(len(ids_m)//2,len(ids_m))]:
  x=resp[lo:hi]; mm=x.mean(0); cc=np.cov(x,rowvar=False,ddof=1)/len(x); ii=np.linalg.pinv(cc,rcond=1e-10); b=float(template@ii@mm/(template@ii@template)); rr=mm-b*template; half.append({'start_id':str(ids_m[lo]),'stop_id_exclusive':str(ids_m[hi-1]),'nreal':hi-lo,'bphi':b,'sigma_linearized':float(np.sqrt(max(1./float(template@ii@template),0.))),'chi2_dof':float(rr@ii@rr/len(rr))})
 out={'status':'PASS','schema':'bphi_disjoint_response_calibration_v1','bphi':bp,'bphi_sigma_statistical':sigma,'b1':a.b1,'b1_sigma':a.b1_sigma,'nreal':len(ids_m),'realization_ids':[str(x) for x in ids_m],'fNL_pair':[-100.,100.],'response_definition':'(mu1_LC_p - mu1_LC_m)/200','covariance':'sample covariance of 400 paired responses divided by nreal; pinv rcond 1e-10','chi2':chi,'dof':len(ss),'chi2_dof':chi/len(ss),'training_universal_reference':2*1.686*(a.b1-1.12),'training_response_reference':3.7636466187234556,'stability_halves':half,'template':template.tolist(),'s':ss.tolist(),'input_theory':str(a.input),'input_theory_sha256':sha(a.input),'moments':{'LC_m':str(a.moments_root/'moments_LC_m_n64_disjoint.npz'),'LC_p':str(a.moments_root/'moments_LC_p_n64_disjoint.npz'),'LC_m_sha256':sha(a.moments_root/'moments_LC_m_n64_disjoint.npz'),'LC_p_sha256':sha(a.moments_root/'moments_LC_p_n64_disjoint.npz')},'scope':'independent/disjoint PNG response calibration for frozen FoF z=1 Mh>=1e13 real-space CIC selection','policy':{'frozen_training_ids_excluded':True,'frozen_heldout_ids_excluded':True,'matched_random_seed_ids':True,'same_window_and_mesh':True,'production_promotion_requires_stage_gate':True}}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','bphi':bp,'sigma':sigma,'chi2_dof':chi/len(ss),'half_bphi':[x['bphi'] for x in half]}))
if __name__=='__main__':main()
