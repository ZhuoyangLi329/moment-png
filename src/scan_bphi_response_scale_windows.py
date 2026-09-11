#!/usr/bin/env python3
"""Scan contiguous response shell windows without changing the frozen protocol."""
import argparse, datetime, hashlib, json
from pathlib import Path
import numpy as np

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def fit(template,response):
    n=len(response); mean=response.mean(0); C=np.cov(response,rowvar=False,ddof=1)/n; P=np.linalg.pinv(C,rcond=1e-10); den=float(template@P@template); c=float(template@P@mean/den); chi=float((mean-c*template)@P@(mean-c*template)); sv=np.linalg.svd(C,compute_uv=False); rank=int(np.sum(sv>sv[0]*1e-10)); hartlap=(n-len(template)-2)/(n-1) if n>len(template)+2 else None
    return {'c':c,'bphi_conditional':c/2.7317333004945543,'chi2':chi,'dof':max(rank-1,1),'chi2_dof':chi/max(rank-1,1),'hartlap_chi2_dof':chi*hartlap/max(rank-1,1) if hartlap else None,'n_shells':len(template),'hartlap':hartlap}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--moments-root',type=Path,required=True); ap.add_argument('--theory',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    m=np.load(a.moments_root/'moments_LC_m_n64_disjoint.npz'); p=np.load(a.moments_root/'moments_LC_p_n64_disjoint.npz'); resp=(np.asarray(p['mu1'],float)-np.asarray(m['mu1'],float))/200.; inp=np.load(a.theory); kv=np.asarray(inp['kvecs']); pm=np.asarray(inp['Pm'],float); M=np.asarray(inp['M'],float); cell=1000./64.; transfer=np.sinc(kv[:,0]*cell/(2*np.pi))**4*np.sinc(kv[:,1]*cell/(2*np.pi))**4*np.sinc(kv[:,2]*cell/(2*np.pi))**4
    from exact_window import mu1_discrete
    ss=np.arange(40.,300.1,20.); per_c=np.zeros_like(pm); mask=np.linalg.norm(kv,axis=1)>0; per_c[mask]=2*pm[mask]*transfer[mask]/M[mask]; T=np.array([mu1_discrete(kv,per_c,float(s),width=20.,boxsize=1000.,cell=cell,nmesh=64,power_convention='mesh') for s in ss]); rows=[]
    for length in range(4,len(ss)+1):
        for start in range(0,len(ss)-length+1):
            stop=start+length; f=fit(T[start:stop],resp[:,start:stop]); f.update({'start_s':float(ss[start]),'stop_s':float(ss[stop-1])}); rows.append(f)
    out={'schema':'bphi_response_scale_window_scan_v1','status':'DIAGNOSTIC','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'windows':rows,'inputs':{'theory':str(a.theory),'theory_sha256':sha(a.theory),'LC_m_sha256':sha(a.moments_root/'moments_LC_m_n64_disjoint.npz'),'LC_p_sha256':sha(a.moments_root/'moments_LC_p_n64_disjoint.npz')},'policy':{'frozen_protocol_unchanged':True,'window_scan_diagnostic_only':True,'production_promotion':False},'warning':'A passing sub-window cannot retroactively change the frozen 40--300 validation cut.'}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); best=sorted(rows,key=lambda x:x['hartlap_chi2_dof'] if x['hartlap_chi2_dof'] is not None else 1e99)[:5]; print(json.dumps({'status':out['status'],'best':[(x['start_s'],x['stop_s'],round(x['hartlap_chi2_dof'],3)) for x in best]}))
if __name__=='__main__': main()
