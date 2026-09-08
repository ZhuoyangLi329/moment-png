***************************************************************************
                          NOTICE TO USERS

Lawrence Berkeley National Laboratory operates this computer system under 
contract to the U.S. Department of Energy.  This computer system is the 
property of the United States Government and is for authorized use only.
Users (authorized or unauthorized) have no explicit or implicit 
expectation of privacy.

Any or all uses of this system and all files on this system may be
intercepted, monitored, recorded, copied, audited, inspected, and disclosed
to authorized site, Department of Energy, and law enforcement personnel,
as well as authorized officials of other agencies, both domestic and foreign.
By using this system, the user consents to such interception, monitoring,
recording, copying, auditing, inspection, and disclosure at the discretion
of authorized site or Department of Energy personnel.

Unauthorized or improper use of this system may result in administrative
disciplinary action and civil and criminal penalties. By continuing to use
this system you indicate your awareness of and consent to these terms and
conditions of use. LOG OFF IMMEDIATELY if you do not agree to the conditions
stated in this warning.

*****************************************************************************

Login connection to host x3115c0s9b0n0:

"""Analytic covariance propagation for frozen bias inputs."""
from __future__ import annotations
import numpy as np

def validate_covariance(cov, n=None, tol=1e-10):
    c=np.asarray(cov,dtype=float)
    if c.ndim!=2 or c.shape[0]!=c.shape[1] or (n is not None and c.shape!=(n,n)): raise ValueError('covariance must be square')
    if not np.isfinite(c).all() or not np.allclose(c,c.T,rtol=0,atol=tol): raise ValueError('covariance must be finite symmetric')
    ev=np.linalg.eigvalsh(c)
    if ev.min() < -tol: raise ValueError('covariance is not positive semidefinite')
    return c,ev

def delta_method(mean, cov, transform, step=1e-6):
    """Propagate covariance through transform via central finite-difference Jacobian."""
    m=np.asarray(mean,dtype=float); c,_=validate_covariance(cov,len(m)); y=np.asarray(transform(m),dtype=float)
    J=np.empty((y.size,m.size))
    for i in range(m.size):
        h=step*max(1.,abs(m[i])); xp=m.copy(); xm=m.copy(); xp[i]+=h; xm[i]-=h; J[:,i]=(np.asarray(transform(xp))-np.asarray(transform(xm)))/(2*h)
    out=J@c@J.T
    return {'mean':y,'jacobian':J,'covariance':out,'eigenvalues':np.linalg.eigvalsh(out)}

def universal_bphi_transform(x, p=1.12, delta_c=1.686):
    x=np.asarray(x,dtype=float)
    if x.size!=1: raise ValueError('input must contain b1 only')
    return np.array([2*delta_c*(x[0]-p)])
def load_covariance_json(path, expected_names=None):
    """Load and validate a named parameter covariance artifact."""
    import json
    with open(path) as f: d=json.load(f)
    for key in ('parameters','mean','output_covariance'):
        if key not in d: raise ValueError(f'missing covariance artifact field: {key}')
    names=list(d['parameters']); mean=np.asarray(d['mean'],dtype=float); cov=np.asarray(d['output_covariance'],dtype=float)
    if len(names)!=len(mean): raise ValueError('parameter/mean length mismatch')
    if expected_names is not None and names!=list(expected_names): raise ValueError('parameter ordering mismatch')
    c,ev=validate_covariance(cov,len(names))
    return {'parameters':names,'mean':mean,'covariance':c,'eigenvalues':ev,'source':str(path)}