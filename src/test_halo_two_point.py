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

Login connection to host x3113c0s5b0n0:

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from halo_two_point import predict_halo_mu1

def main():
    L=1000.; n=8; ix=np.arange(n); signed=np.where(ix<n//2,ix,ix-n)
    g=np.array(np.meshgrid(signed,signed,signed,indexing='ij')).reshape(3,-1).T
    kv=2*np.pi*g/L; kk=np.linalg.norm(kv,axis=1)
    pm=np.exp(-(kk/.03)**2)+.1; M=1.+1000*kk**2
    mu,p=predict_halo_mu1(kv,pm,M,2.,-.2,.1,1.,fnl=0.,box=L,s=125.,width=100.,cell=L/n,qmin=.001,qmax=.2,nq=20,nmu=16)
    assert np.isfinite(mu) and np.all(np.isfinite(p['power']))
    assert p['metadata']['window']=='exact_discrete_mesh'
    assert np.allclose(p['power'],p['tree']+p['halo_P22']+p['halo_P13'])
    print({'status':'PASS','mu1':float(mu),'nmode':len(kv),'metadata':p['metadata']})
if __name__=='__main__': main()
