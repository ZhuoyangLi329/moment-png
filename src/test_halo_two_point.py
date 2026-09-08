
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
