
"""Fixed-cutoff halo P13 contraction with an explicit collapsed K3 callback."""
from __future__ import annotations
import numpy as np

def halo_P13_from_k3(k, P, K3, qmin, qmax, nq=160, nmu=96, b1=1.0):
    """Evaluate 6*b1*P(k) int d3q K3(k,q,-q)P(q)/(2pi)^3.

    The callback is required because K3(k,q,-q) can have a regulated limiting
    prescription in a fixed-cutoff MARISA-B scheme.  No generic limit is
    silently substituted.
    """
    if k <= 0 or qmin <= 0 or qmax <= qmin: raise ValueError('invalid k/cutoff')
    if K3 is None: raise ValueError('explicit K3 callback required')
    x=np.linspace(np.log(qmin),np.log(qmax),nq); q=np.exp(x); mu=np.linspace(-1.,1.,nmu)
    kv=np.array([0.,0.,float(k)])
    rows=[]
    for qi in q:
        vals=[]
        for m in mu:
            qv=np.array([qi*np.sqrt(max(0.,1.-m*m)),0.,qi*m])
            vals.append(float(K3(kv,qv,-qv))*float(P(qi))*qi**3)
        rows.append(np.trapz(vals,mu))
    total=np.trapz(rows,x)
    return float(6.*b1*float(P(k))*total/(4.*np.pi**2))

def _f2vec(a, b):
    na=np.linalg.norm(a); nb=np.linalg.norm(b)
    if na <= 0 or nb <= 0: return 0.0
    mu=float(np.dot(a,b)/(na*nb))
    return float(5/7 + .5*mu*(na/nb+nb/na) + 2/7*mu*mu)

def _s2vec(a, b):
    na=np.linalg.norm(a); nb=np.linalg.norm(b)
    if na <= 0 or nb <= 0: return 0.0
    mu=float(np.dot(a,b)/(na*nb))
    return float(mu*mu-1/3)

def halo_P13_bias_collapsed(k, P, b1, b2, bK2, qmin, qmax, nq=160, nmu=96):
    """Halo P13 with explicit collapsed D3/T3 bias partitions.

    The matter b1^2 F3 contribution uses the audited angle-averaged EdS
    P13 primitive.  The b2 and bK2 pieces are evaluated directly from the
    MARISA-B D3/T3 partition at (k,q,-q), with the same fixed radial cutoff.
    """
    try:
        from .marisa_b_power_loop import loop_P13
    except ImportError:
        from marisa_b_power_loop import loop_P13
    if k <= 0 or qmin <= 0 or qmax <= qmin: raise ValueError('invalid k/cutoff')
    x=np.linspace(np.log(qmin),np.log(qmax),nq); q=np.exp(x); mu=np.linspace(-1.,1.,nmu)
    kv=np.array([0.,0.,float(k)]); rows=[]
    for qi in q:
        vals=[]
        for m in mu:
            qv=np.array([qi*np.sqrt(max(0.,1.-m*m)),0.,qi*m]); qm=-qv
            fp=_f2vec(kv,qv); fm=_f2vec(kv,qm)
            d3=(fp+fm)/3.0
            t3=2.0/3.0*(_s2vec(qv,kv-qv)*fm + _s2vec(qm,kv+qv)*fp)
            vals.append((b2*d3+bK2*t3)*float(P(qi))*qi**3)
        rows.append(np.trapz(vals,mu))
    bias_integral=np.trapz(rows,x)/(4*np.pi**2)
    matter=float(b1*b1*loop_P13(float(k),P,qmin,qmax,nq=nq))
    bias=float(6.*b1*float(P(k))*bias_integral)
    return {'total':matter+bias,'matter_b1sq_P13':matter,'bias_D3T3':bias,
            'cutoff':(qmin,qmax),'nq':nq,'nmu':nmu,
            'components':'b1^2 F3 + b1*b2 D3 + b1*bK2 T3'}
