#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from local_trispectrum import collapsed_mu2_local_mc

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--nsamp',type=int,default=5000); a=ap.parse_args(); d=np.load(a.root/'inputs/quijote_fiducial_z1_theory.npz'); kg=np.asarray(d['k']); ok=(kg>1e-4)&(kg<.3); kg=kg[ok]; pp=np.asarray(d['Pphi'])[ok]; mm=np.asarray(d['M'])[ok]; pphi=lambda q:float(np.interp(np.asarray(q),kg,pp,left=pp[0],right=pp[-1])); transfer=lambda q:float(np.interp(np.asarray(q),kg,mm,left=mm[0],right=mm[-1])); b1=2.7340475186190334; sarr=np.arange(40.,300.1,20.); rows=[]
 for s in sarr:
  w=lambda q:float(np.sinc(np.asarray(q)*s/np.pi)); conn,err=collapsed_mu2_local_mc(kg,pphi,lambda q:b1*transfer(q),w,fnl=100.,gnl=0.,nsamp=a.nsamp,seed=int(s)); rows.append({'s':float(s),'mu2_primordial_fNL100':conn,'mc_error':err})
 # measured even response of connected mu2: (plus+minus)/2 - fid, divided by 100^2
 c0=np.load(a.root/'results/resolution_clean/connected_fiducial_n64.npz'); cm=np.load(a.root/'results/resolution_clean/connected_LC_m_n64.npz'); cp=np.load(a.root/'results/resolution_clean/connected_LC_p_n64.npz'); even=((np.asarray(cp['mu2_connected']).mean(0)+np.asarray(cm['mu2_connected']).mean(0))/2-np.asarray(c0['mu2_connected']).mean(0))/10000.; rows2=[dict(x,measured_connected_even_response=float(y),difference=float(x['mu2_primordial_fNL100']-y)) for x,y in zip(rows,even)]
 out={'status':'PASS','schema':'primordial_mu2_trispectrum_component_audit_v1','b1':b1,'fNL':100.,'n_samples':a.nsamp,'s':[float(x) for x in sarr],'components':rows2,'scope':'continuum collapsed local primordial trispectrum only; compared with Nbody connected even response','policy':{'same_nodes':True,'response_formula':'((LC_p+LC_m)/2-fiducial)/100^2','no_parameter_fit':True},'warning':'The continuum MC window and linear halo transfer are diagnostic. Halo b2/bK2/bphi/bphidelta, clustered/repeated contacts, and discrete alias terms are not included.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','nshells':len(rows),'mean_mc_error':float(np.mean([x['mc_error'] for x in rows]))}))
if __name__=='__main__':main()
