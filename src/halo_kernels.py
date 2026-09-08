
"""General MARISA-B halo K2 and fixed-cutoff P22 contractions."""
from __future__ import annotations
import numpy as np
try:
    from .marisa_b_power_loop import F2
except ImportError:
    from marisa_b_power_loop import F2

def S2(q, r):
    qn=np.linalg.norm(q); rn=np.linalg.norm(r)
    if qn==0 or rn==0: return 0.0
    mu=float(np.dot(q,r)/(qn*rn))
    return mu*mu-1.0/3.0

def K2(q, r, b1, b2, bK2):
    return b1*F2(q,r)+0.5*b2+bK2*S2(q,r)

def halo_P22(k, P, b1, b2, bK2, qmin, qmax, nq=160, nmu=96):
    k=float(k)
    x=np.linspace(np.log(qmin),np.log(qmax),nq); q=np.exp(x)
    mu=np.linspace(-1,1,nmu)
    qq,mm=np.meshgrid(q,mu,indexing='ij')
    r=np.sqrt(k*k+qq*qq-2*k*qq*mm)
    f2=5/7+0.5*mm*(qq/np.maximum(r,1e-30)+r/np.maximum(qq,1e-30))+2/7*mm*mm
    s2=mm*mm-1/3
    kh=b1*f2+0.5*b2+bK2*s2
    integrand=qq**3*kh*kh*np.asarray(P(qq))*np.asarray(P(r))
    val=np.trapz(np.trapz(integrand,mu,axis=1),x)/(2*np.pi)**3*2*2*np.pi
    return float(val)
def halo_P22_directional(k, P, Pdir, b1, b2, bK2, qmin, qmax, nq=160, nmu=96):
    """Derivative of halo P22 under P -> P + lambda Pdir (product rule)."""
    k=float(k); x=np.linspace(np.log(qmin),np.log(qmax),nq); q=np.exp(x); mu=np.linspace(-1,1,nmu)
    qq,mm=np.meshgrid(q,mu,indexing='ij'); r=np.sqrt(k*k+qq*qq-2*k*qq*mm)
    f2=5/7+0.5*mm*(qq/np.maximum(r,1e-30)+r/np.maximum(qq,1e-30))+2/7*mm*mm
    kh=b1*f2+0.5*b2+bK2*(mm*mm-1/3)
    integ=qq**3*kh*kh*(np.asarray(Pdir(qq))*np.asarray(P(r))+np.asarray(P(qq))*np.asarray(Pdir(r)))
    return float(np.trapz(np.trapz(integ,mu,axis=1),x)/(2*np.pi)**3*2*2*np.pi)
def halo_P13_gaussian(k, P, b1, qmin, qmax, nq=160):
    """Gaussian halo P13 baseline: b1^2 times the EdS matter P13."""
    try:
        from .marisa_b_power_loop import loop_P13
    except ImportError:
        from marisa_b_power_loop import loop_P13
    return float(b1*b1*loop_P13(float(k), P, qmin, qmax, nq=nq))
def halo_one_loop_gaussian(k, P, b1, b2, bK2, qmin, qmax, nq=160, nmu=96):
    """Gaussian fixed-cutoff halo one-loop baseline P22[K2]+b1^2 P13."""
    return halo_P22(k,P,b1,b2,bK2,qmin,qmax,nq,nmu)+halo_P13_gaussian(k,P,b1,qmin,qmax,nq)
def halo_one_loop_png_directional(k, P, Pdir, b1, b2, bK2, qmin, qmax, nq=160, nmu=96):
    """One-PNG-leg directional derivative of the current halo one-loop baseline."""
    try:
        from .marisa_b_power_loop import loop_P13_directional
    except ImportError:
        from marisa_b_power_loop import loop_P13_directional
    d22=halo_P22_directional(k,P,Pdir,b1,b2,bK2,qmin,qmax,nq,nmu)
    d13=b1*b1*loop_P13_directional(float(k),P,Pdir,qmin,qmax,nq=nq)
    return float(d22+d13)