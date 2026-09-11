#!/usr/bin/env python3
"""Diagnostic joint b1/c=b1*bphi block covariance audit."""
import argparse, datetime, hashlib, json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def fit_b1_block(pmode, kv, pmi, lo, hi, kmax=.03, box=1000., nmesh=64):
    n=pmode.shape[1]; h=box/nmesh; k=np.linalg.norm(kv,axis=1)
    edges=np.arange(0,.3+.005,.005); kc=.5*(edges[:-1]+edges[1:]); idx=np.digitize(k,edges)-1
    ok=(idx>=0)&(idx<len(kc))&(k>0)
    cic=np.sinc(kv[:,0]*h/(2*np.pi))**4*np.sinc(kv[:,1]*h/(2*np.pi))**4*np.sinc(kv[:,2]*h/(2*np.pi))**4
    inds=[i for i in range(len(kc)) if kc[i]<=kmax and np.any(ok&(idx==i))]
    x=np.asarray(pmode[lo:hi])
    y=np.array([x[:,ok&(idx==i)].mean() for i in inds])
    real=np.array([x[:,ok&(idx==i)].mean(1) for i in inds]).T
    C=np.cov(real,rowvar=False,ddof=1)/len(x); P=np.linalg.pinv(C,rcond=1e-10)
    X=np.column_stack([pmi[inds]*np.array([cic[ok&(idx==i)].mean() for i in inds]),np.ones(len(inds))])
    # The two columns differ by O(10^4) in scale (P_m versus a constant
    # shot term).  Scale before the pseudoinverse, then transform the
    # coefficient covariance back; otherwise rcond silently drops P_shot.
    scales=np.maximum(np.linalg.norm(X,axis=0),1.0)
    eig,u=np.linalg.eigh(C); keep=eig>max(float(eig.max()),1e-30)*1e-10
    R=(u[:,keep]/np.sqrt(eig[keep])).T
    def residual(theta): return R@(y-X@(theta/scales))
    init=np.array([2.8**2*scales[0],4000.*scales[1]])
    fit=least_squares(residual,init,bounds=([0.,0.],[36.*scales[0],1e6*scales[1]]),x_scale='jac')
    beta=fit.x/scales; J=fit.jac; cov_theta=np.linalg.pinv(J.T@J,rcond=1e-12); cov=np.diag(1.0/scales)@cov_theta@np.diag(1.0/scales); aa=max(float(beta[0]),0.0)
    b1=float(np.sqrt(aa)); sigma_a=float(np.sqrt(max(cov[0,0],0.0)))
    return {'b1':b1,'b1_sigma_gls':sigma_a/(2*b1) if b1>0 else None,'P_shot':float(beta[1]),'cov_a_pshot':cov.tolist(),'design_column_scales':scales.tolist(),'shot_boundary_active':bool(beta[1] <= 1e-8),'chi2_dof':float(np.sum(residual(fit.x)**2)/max(len(inds)-2,1)),'nreal':hi-lo,'n_bins':len(inds)}

def fit_c_block(response, template):
    x=np.asarray(response,float); y=x.mean(0); C=np.cov(x,rowvar=False,ddof=1)/len(x); P=np.linalg.pinv(C,rcond=1e-10); den=float(template@P@template); c=float(template@P@y/den); return {'c':c,'sigma_c':float(np.sqrt(1/den)),'chi2_dof':float((y-c*template)@P@(y-c*template)/13),'nreal':len(x)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--power',type=Path,required=True); ap.add_argument('--moments-root',type=Path,required=True); ap.add_argument('--theory',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    mp=np.load(a.power); kv=np.asarray(mp['kvecs'],float); Pmode=np.asarray(mp['Pmode'],float); ids=np.asarray(mp['realization_ids']).astype(str)
    if ids.tolist()!=[f'real{i:03d}' for i in range(100,500)]: raise ValueError('power IDs must be real100-real499')
    tab=np.load(a.theory); kt=np.asarray(tab['k'],float) if 'k' in tab else None; pm=np.asarray(tab['Pm'],float)
    if kt is None: raise ValueError('theory must contain k and Pm')
    kc=.5*(np.arange(0,.3+.005,.005)[:-1]+np.arange(0,.3+.005,.005)[1:]); pmi=np.interp(kc,kt,pm)
    lm=np.load(a.moments_root/'moments_LC_m_n64_disjoint.npz'); lp=np.load(a.moments_root/'moments_LC_p_n64_disjoint.npz')
    if not np.array_equal(lm['realization_ids'].astype(str),ids) or not np.array_equal(lp['realization_ids'].astype(str),ids): raise ValueError('response and power IDs must be paired')
    response=(np.asarray(lp['mu1'],float)-np.asarray(lm['mu1'],float))/200.
    from exact_window import mu1_discrete
    cell=1000./64.; transfer=np.sinc(kv[:,0]*cell/(2*np.pi))**4*np.sinc(kv[:,1]*cell/(2*np.pi))**4*np.sinc(kv[:,2]*cell/(2*np.pi))**4
    inp=np.load(a.theory); M=np.asarray(inp['M'],float); per_c=np.zeros_like(pm); kvec_norm=np.linalg.norm(kv,axis=1); per_c[kvec_norm>0]=2*pm[kvec_norm>0]*transfer[kvec_norm>0]/M[kvec_norm>0]
    scales=np.arange(40.,300.1,20.); template=np.array([mu1_discrete(kv,per_c,float(s),width=20.,boxsize=1000.,cell=cell,nmesh=64,power_convention='mesh') for s in scales])
    blocks=[]
    for lo in range(0,400,100):
        b1=fit_b1_block(Pmode,kv,pmi,lo,lo+100); c=fit_c_block(response[lo:lo+100],template); bphi=c['c']/b1['b1']; blocks.append({'row_start':lo,'row_stop':lo+100,'start_id':ids[lo],'stop_id':ids[lo+99],'b1_fit':b1,'c_fit':c,'bphi_conditional':bphi})
    vals=np.array([[z['b1_fit']['b1'],z['c_fit']['c']] for z in blocks]); mean=vals.mean(0); cov=np.cov(vals,rowvar=False,ddof=1)/len(vals); b1,c=mean; grad=np.array([-c/(b1*b1),1/b1]); out={'schema':'b1_bphi_crosscov_disjoint_audit_v1','status':'DIAGNOSTIC','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blocks':blocks,'block_mean_b1':float(b1),'block_mean_c':float(c),'block_mean_bphi':float(c/b1),'block_covariance_b1_c':cov.tolist(),'delta_method_sigma_bphi_with_block_cov':float(np.sqrt(max(grad@cov@grad,0.0))),'delta_method_gradient':[float(x) for x in grad],'block_correlation_b1_c':float(cov[0,1]/np.sqrt(cov[0,0]*cov[1,1])),'inputs':{'power':str(a.power),'power_sha256':sha(a.power),'moments_LC_m':str(a.moments_root/'moments_LC_m_n64_disjoint.npz'),'moments_LC_m_sha256':sha(a.moments_root/'moments_LC_m_n64_disjoint.npz'),'moments_LC_p':str(a.moments_root/'moments_LC_p_n64_disjoint.npz'),'moments_LC_p_sha256':sha(a.moments_root/'moments_LC_p_n64_disjoint.npz'),'theory':str(a.theory),'theory_sha256':sha(a.theory)},'policy':{'n_blocks':4,'block_covariance_is_low_sample_diagnostic':True,'response_shape_gate_unchanged':True,'production_promotion':False,'b1_cross_covariance_source':'same disjoint realization blocks'}}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'b1':out['block_mean_b1'],'c':out['block_mean_c'],'bphi':out['block_mean_bphi'],'sigma_delta':out['delta_method_sigma_bphi_with_block_cov'],'corr':out['block_correlation_b1_c']}))
if __name__=='__main__': main()
