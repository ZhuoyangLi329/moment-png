
#!/usr/bin/env python
"""First-principles local-PNG scale-dependent-bias template.

Given matter P(k), transfer M(k), and halo parameters, predicts the linear
odd response of halo P(k) and optionally projects it through a shell window.
This is a theory scaffold: b_phi must be supplied independently, never fit
from the same response being tested.
"""
import argparse,json
from pathlib import Path
import numpy as np


def universal_bphi(b1,delta_c=1.686,p=1.0,sigma_b1=0.,sigma_delta_c=0.,sigma_p=0.):
    """Universal-mass-function b_phi and linear propagated 1-sigma error."""
    value=2.*delta_c*(b1-p)
    error=float(np.sqrt((2.*delta_c*sigma_b1)**2+(2.*(b1-p)*sigma_delta_c)**2+(2.*delta_c*sigma_p)**2))
    return float(value),error

def response(k, M, b1, bphi, delta_c=1.686):
    # bphi is the full PNG bias coefficient: Delta b/fNL=bphi/M(k); dP/P=2 Delta b/b1.
    return 2.0*bphi/(b1*np.maximum(np.abs(M),1e-30))

def shell_window(k,s,width):
    r=np.linspace(s-width/2,s+width/2,257)
    return np.mean(np.sinc(np.outer(k,r)/np.pi),axis=1)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('input',type=Path,help='NPZ with k, Pm, M'); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--bphi',type=float,required=True); ap.add_argument('--delta-c',type=float,default=1.686); ap.add_argument('--shells',default='40,60,80,100'); ap.add_argument('--width',type=float,default=20); ap.add_argument('--output',required=True); a=ap.parse_args()
 d=np.load(a.input); k=np.asarray(d['k']); Pm=np.asarray(d['Pm']); M=np.asarray(d['M']); q=(k>0)&np.isfinite(k)&np.isfinite(Pm)&np.isfinite(M)&(Pm>=0)
 k=k[q]; Pm=Pm[q]; M=M[q]; r=response(k,M,a.b1,a.bphi,a.delta_c); shells=[float(x) for x in a.shells.split(',')]
 proj=[]
 for s in shells: proj.append(float(np.trapz(k*k*Pm*r*shell_window(k,s,a.width),k)/(2*np.pi**2)))
 out={'model':'local PNG halo bias from independent b_phi','b1':a.b1,'bphi':a.bphi,'delta_c':a.delta_c,'shell_width':a.width,'k_bins':len(k),'fractional_response_per_fNL':r.tolist(),'s':shells,'mu1_response_per_fNL':proj,'equations':{'Delta_b_per_fNL':'bphi / M(k)' ,'dP_over_P_per_fNL':'2 Delta_b / b1','mu1':'integral dk k^2 Pm(k) [dP/P] W_shell(k)/(2 pi^2)'},'warning':'b_phi must be calibrated independently; do not fit it and validate on the same realizations.'}
 Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'model':out['model'],'k_bins':len(k),'shells':shells},indent=2))
if __name__=='__main__': main()
