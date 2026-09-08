#!/usr/bin/env python3
"""Analytic Gaussian halo mu2 with explicit mesh cutoff/CIC convention."""
import argparse,json
from pathlib import Path
import numpy as np

def calc(k,pm,b1,pshot,s,width,kmax=None,cic=False,cell=None):
    q=(k>0)&np.isfinite(k)&np.isfinite(pm)&(pm>=0)
    if kmax is not None: q &= k<=kmax
    k=k[q]; pm=pm[q]
    if cic:
        if cell is None: raise ValueError('cell is required with --cic')
        # isotropic approximation to the CIC power transfer.
        tr=np.sinc(k*cell/(2*np.pi))**4
    else: tr=np.ones_like(k)
    ph=(b1*b1*pm+pshot)*tr
    rr=np.linspace(s-width/2,s+width/2,257)
    w=np.sinc(np.outer(k,rr)/np.pi).mean(1)
    integ=lambda f: float(np.trapz(k*k*f,k)/(2*np.pi**2))
    sig0=integ(ph); sigs=integ(ph*w*w); xi=integ(ph*w)
    return {'s':float(s),'sigma0_sq':sig0,'sigma_s_sq':sigs,'xi_s':xi,'mu2_gaussian':sig0*sigs+xi*xi}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input',type=Path); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--pshot',type=float,required=True); ap.add_argument('--shells',default='40,60,80,100'); ap.add_argument('--width',type=float,default=20); ap.add_argument('--kmax',type=float); ap.add_argument('--nmesh',type=int); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--cic',action='store_true'); ap.add_argument('--output',required=True); a=ap.parse_args(); d=np.load(a.input); k=np.asarray(d['k']); pm=np.asarray(d['Pm']); cell=a.box/a.nmesh if a.nmesh else None; kmax=a.kmax if a.kmax is not None else (np.pi/cell if cell else None); pred=[calc(k,pm,a.b1,a.pshot,s,a.width,kmax,a.cic,cell) for s in map(float,a.shells.split(','))]; out={'model':'analytic Gaussian halo mu2 from mesh-convention P_h','b1':a.b1,'P_shot':a.pshot,'shell_width':a.width,'kmax':kmax,'nmesh':a.nmesh,'cic_power_transfer':a.cic,'predictions':pred,'equation':'mu2_G=sigma0^2 sigma_s^2+xi_s^2; finite mesh P_h=(b1^2 P_m+P_shot)|W_CIC|^2 when --cic','scope':'Gaussian component only; contact/repeated-index/clustered terms are separate'}; Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','nshell':len(pred),'kmax':kmax,'cic':a.cic}))
if __name__=='__main__': main()
