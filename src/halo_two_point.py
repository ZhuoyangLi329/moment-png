
"""Unified intermediate pure-analytic halo power/mu1 forward model."""
from __future__ import annotations
import numpy as np
from halo_kernels import halo_P22, halo_one_loop_png_directional
from halo_p13 import halo_P13_bias_collapsed
from exact_window import mu1_discrete

def predict_halo_mu1(kvecs, pm, M, b1, b2=0., bK2=0., bphi=0., fnl=0.,
                     pshot=0., box=1000., s=40., width=20., cell=None,
                     qmin=1e-4, qmax=30., nq=160, nmu=96,
                     include_p22=True, include_p13=True,
                     include_png_loop_response=True):
    """Project a declared tree plus fixed-cutoff halo one-loop spectrum.

    ``pm`` and ``M`` are arrays on the complete FFT mode list.  The loop
    response uses the explicit one-PNG-leg product rule in ``halo_kernels``;
    no coefficients are fitted to PNG validation nodes.
    """
    kv=np.asarray(kvecs,dtype=float); p=np.asarray(pm,dtype=float); m=np.asarray(M,dtype=float)
    if kv.ndim!=2 or kv.shape[1]!=3 or p.shape!=(len(kv),) or m.shape!=(len(kv),):
        raise ValueError('kvecs, pm, and M must match')
    if np.any(p<0) or np.any(~np.isfinite(p)) or np.any(~np.isfinite(m)): raise ValueError('invalid spectrum/transfer')
    k=np.linalg.norm(kv,axis=1); order=np.argsort(k); ks=k[order]; ps=p[order]; ms=m[order]
    P=lambda x: np.interp(np.asarray(x),ks,ps,left=ps[0],right=ps[-1])
    Mt=lambda x: np.interp(np.asarray(x),ks,ms,left=ms[0],right=ms[-1])
    db=bphi/np.maximum(np.abs(m),1e-30); tree=(b1+fnl*db)**2*p+pshot
    p22=np.zeros_like(p); p13=np.zeros_like(p); p13_bias=np.zeros_like(p); dloop=np.zeros_like(p)
    for i,ki in enumerate(k):
        if ki<=0: continue
        if include_p22: p22[i]=halo_P22(float(ki),P,b1,b2,bK2,qmin,qmax,nq,nmu)
        if include_p13:
            p13_parts=halo_P13_bias_collapsed(float(ki),P,b1,b2,bK2,qmin,qmax,nq,nmu)
            p13[i]=p13_parts['total']; p13_bias[i]=p13_parts['bias_D3T3']
        if include_png_loop_response:
            Pdir=lambda x: bphi/np.maximum(np.abs(Mt(x)),1e-30)*P(x)
            dloop[i]=halo_one_loop_png_directional(float(ki),P,Pdir,b1,b2,bK2,qmin,qmax,nq,nmu)
    power=tree+p22+p13+fnl*dloop
    mu1=mu1_discrete(kv,power,s,width,box,cell)
    return mu1, {'power':power,'tree':tree,'halo_P22':p22,'halo_P13':p13,
                 'halo_P13_bias_D3T3':p13_bias,
                 'png_loop_response':dloop,'metadata':{
                     'model':'tree+halo_K2_P22+halo_P13_D3T3+one_PNG_leg_loop',
                     'qmin':qmin,'qmax':qmax,'nq':nq,'nmu':nmu,
                     'include_p22':include_p22,'include_p13':include_p13,
                     'include_png_loop_response':include_png_loop_response,
                     'png_loop_scope':'internal P(k) one-leg product rule; PNG kernel bias insertions excluded',
                     'window':'exact_discrete_mesh'}}
