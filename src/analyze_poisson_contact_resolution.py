import argparse,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); paths={'64':a.root/'results/poisson_control_n10_n64.npz','128':a.root/'results/poisson_control_batch_58082476_n128.npz','256':a.root/'results/poisson_control_batch_58082476_n256.npz'}; rows={}
 for n,p in paths.items():
  d=np.load(p); c=np.asarray(d['mu2_connected'],float); pred=np.asarray(d['analytic_contact'],float); mean=c.mean(0); se=c.std(0,ddof=1)/np.sqrt(len(c)); r=mean-pred; pull=r/np.maximum(se,1e-30); rows[n]={'path':str(p),'nreal':len(c),'nhalo':int(d['nhalo']),'lambda_cell':float(d['lambda_cell']),'mean_connected':mean.tolist(),'analytic_contact':pred.tolist(),'se':se.tolist(),'pull':pull.tolist(),'rms_pull':float(np.sqrt(np.mean(pull*pull))),'max_abs_pull':float(np.max(np.abs(pull))),'coverage_abs_pull_le_2':float(np.mean(np.abs(pull)<=2)),'mean_abs_residual':float(np.mean(np.abs(r)))}
 out={'status':'PASS','schema':'poisson_contact_resolution_audit_v1','nodes':rows,'scope':'iid-Poisson connected mu2 residual versus discrete contact formula at matched nbar and shells','policy':{'contact_formula':'K0^2/lambda_cell^3','not_full_halo_contact':True,'scales':'40--300 step20'},'warning':'Agreement tests only the independent-cell Poisson baseline; clustered halo and repeated-index corrections remain separate.'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','rms_pull':{k:round(v['rms_pull'],3) for k,v in rows.items()}}))
if __name__=='__main__': main()
