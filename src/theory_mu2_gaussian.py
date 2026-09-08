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

Login connection to host x3116c0s21b0n0:

#!/usr/bin/env python
"""Gaussian-field baseline for the variance of eta = delta * (K_s * delta)."""
from pathlib import Path
import argparse, json
import numpy as np
from moments import cic_mesh, shell_kernel

def gaussian_mu2_from_field(delta, boxsize, scales, width):
    n=delta.shape[0]; dk=np.fft.fftn(delta); norm=float(n**6)
    sigma0=float(np.mean(delta*delta)); pred=[]; measured=[]; sigmas=[]
    for s in scales:
        wk=np.fft.fftn(shell_kernel(n,boxsize,float(s),width))
        ds=np.fft.ifftn(dk*wk).real
        c=float(np.mean(delta*ds))
        sigs=float(np.mean(ds*ds))
        m2=float(np.mean((delta*ds-c)**2))
        pred.append(sigma0*sigs+c*c); measured.append(m2); sigmas.append((sigma0,sigs,c))
    return np.asarray(measured),np.asarray(pred),np.asarray(sigmas)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('catalog',type=Path); ap.add_argument('--nmesh',type=int,default=64)
    ap.add_argument('--boxsize',type=float,default=1000.); ap.add_argument('--smin',type=float,default=20.)
    ap.add_argument('--smax',type=float,default=300.); ap.add_argument('--ds',type=float,default=20.)
    ap.add_argument('--shell-width',type=float,default=20.); ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args(); scales=np.arange(a.smin,a.smax+0.1,a.ds)
    delta=cic_mesh(np.load(a.catalog,mmap_mode='r'),a.nmesh,a.boxsize)
    m,p,c=gaussian_mu2_from_field(delta,a.boxsize,scales,a.shell_width)
    ratio=m/np.maximum(p,1e-30); a.output.parent.mkdir(parents=True,exist_ok=True)
    np.savez(a.output,s=scales,mu2_grid=m,mu2_gaussian=p,ratio=ratio,
             sigma0sq=c[:,0],sigmasq=c[:,1],xi_shell=c[:,2],nmesh=a.nmesh,
             boxsize=a.boxsize,shell_width=a.shell_width)
    print(json.dumps({'s':scales.tolist(),'mu2_grid':m.tolist(),'mu2_gaussian':p.tolist(),
                      'ratio':ratio.tolist(),'sigma0sq':float(c[0,0])}))
if __name__=='__main__': main()

