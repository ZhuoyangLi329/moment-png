#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
import numpy as np
from exact_window import mesh_wavevectors,mu1_discrete

def sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def fit(template,response):
 n=len(response); mean=response.mean(0); C=np.cov(response,rowvar=False,ddof=1)/n; s=np.linalg.svd(C,compute_uv=False); rank=int(np.sum(s>s[0]*1e-10)); inv=np.linalg.pinv(C,rcond=1e-10); den=float(template@inv@template); b=float(template@inv@mean/den); rr=mean-b*template; chi=float(rr@inv@rr); return {'bphi':b,'sigma':float(np.sqrt(max(1/den,0))),'chi2_dof':chi/max(rank-1,1),'chi2':chi,'dof':max(rank-1,1),'rank':rank,'hartlap':float((n-len(template)-2)/(n-1)),'rms_pull':float(np.sqrt(np.mean((rr/np.sqrt(np.maximum(np.diag(C),1e-30)))**2)))}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--power',type=Path,required=True);ap.add_argument('--moments-root',type=Path,required=True);ap.add_argument('--theory',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args(); p=np.load(a.power); P=np.asarray(p['Pmode'],float).mean(0); kv=np.asarray(p['kvecs'],float); n=64; L=1000.; cell=L/n; km=np.linalg.norm(kv,axis=1); cic=np.sinc(kv[:,0]*cell/(2*np.pi))**4*np.sinc(kv[:,1]*cell/(2*np.pi))**4*np.sinc(kv[:,2]*cell/(2*np.pi))**4; inp=np.load(a.theory); M=np.asarray(inp['M'],float); lm=np.load(a.moments_root/'moments_LC_m_n64_disjoint.npz'); lp=np.load(a.moments_root/'moments_LC_p_n64_disjoint.npz'); ids=lm['realization_ids'].astype(str); response=(lp['mu1']-lm['mu1'])/200.; ss=np.arange(40.,300.1,20.); b1=2.7317333004945543; rows={}
 for shot in [0.,6719.475115627377]:
  peff=P-shot*cic; peff[km==0]=0.; per_bphi=2*peff/(b1*np.maximum(np.abs(M),1e-30)); template=np.array([mu1_discrete(kv,per_bphi,float(s),width=20.,boxsize=L,cell=cell,nmesh=n,power_convention='mesh') for s in ss]); rows[str(shot)]={'shot':shot,**fit(template,response),'template':template.tolist()}
 out={'schema':'bphi_disjoint_measured_ph_diagnostic_v1','status':'PASS','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nreal':len(ids),'ids_first_last':[str(ids[0]),str(ids[-1])],'b1_conditioning':b1,'shot_scans':rows,'power_source':str(a.power),'power_sha256':sha(a.power),'moments_root':str(a.moments_root),'moments_sha256':{'LC_m':sha(a.moments_root/'moments_LC_m_n64_disjoint.npz'),'LC_p':sha(a.moments_root/'moments_LC_p_n64_disjoint.npz')},'scope':'normalization-only diagnostic using disjoint measured fiducial P_h; not production theory or heldout response fit','policy':{'heldout_excluded':True,'empirical_template_not_promoted':True,'production_promotion':False}}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'chi2_dof':{k:v['chi2_dof'] for k,v in rows.items()},'bphi':{k:v['bphi'] for k,v in rows.items()}}))
if __name__=='__main__':main()
