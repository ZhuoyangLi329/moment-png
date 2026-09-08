#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); grids={'64':('results/resolution_clean', 'results/poisson_control_n10_n64.npz'),'128':('results/resolution_clean','results/poisson_control_batch_58082476_n128.npz'),'256':('results/resolution_clean','results/poisson_control_batch_58082476_n256.npz')}; rows={}
 for node in ['fiducial','LC_m','LC_p']:
  rows[node]={}
  for n,(cdir,pp) in grids.items():
   c=np.load(a.root/cdir/f'connected_{node}_n{n}.npz'); p=np.load(a.root/pp); conn=np.asarray(c['mu2_connected'],float); contact=np.asarray(p['analytic_contact'],float); mean=conn.mean(0); se=conn.std(0,ddof=1)/np.sqrt(len(conn)); excess=mean-contact; pull=excess/np.maximum(se,1e-30); rows[node][n]={'nreal':len(conn),'n_halo_contact_control':int(len(p['mu2'])),'lambda_cell':float(p['lambda_cell']),'mean_connected':mean.tolist(),'analytic_poisson_contact':contact.tolist(),'mean_halo_excess':excess.tolist(),'se_connected':se.tolist(),'excess_pull':pull.tolist(),'rms_excess_pull':float(np.sqrt(np.mean(pull*pull))),'fraction_abs_excess_pull_le_2':float(np.mean(np.abs(pull)<=2)),'max_abs_excess':float(np.max(np.abs(excess)))}
 out={'status':'PASS','schema':'halo_contact_excess_audit_v1','nodes':rows,'scope':'real Nbody connected mu2 minus independent iid-Poisson contact baseline','policy':{'poisson_term':'K0^2/lambda_cell^3','excess_interpretation':'clustered/repeated-index candidate only','not_a_fit':True,'scales':'40--300 step20'},'warning':'The excess is not yet a closed halo four-point theory term; b1,b2,bK2,bphi,bphidelta and primordial trispectrum contributions remain unmodeled.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','rms_excess_pull':{n:{g:round(v['rms_excess_pull'],2) for g,v in x.items()} for n,x in rows.items()}}))
if __name__=='__main__': main()
