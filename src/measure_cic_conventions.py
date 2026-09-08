#!/usr/bin/env python3
import argparse,json,os,platform
from pathlib import Path
import numpy as np

def ngp_mesh(pos,n,L):
 g=np.zeros((n,n,n),float); ix=np.floor(np.asarray(pos)/L*n).astype(int)%n; np.add.at(g,(ix[:,0],ix[:,1],ix[:,2]),1.); return g/g.mean()-1.
def cic_mesh(pos,n,L):
 g=np.zeros((n,n,n),float); u=np.asarray(pos)/L*n; i=np.floor(u).astype(int); f=u-i
 for dx in (0,1):
  wx=(1-f[:,0]) if dx==0 else f[:,0]
  for dy in (0,1):
   wy=(1-f[:,1]) if dy==0 else f[:,1]
   for dz in (0,1):
    wz=(1-f[:,2]) if dz==0 else f[:,2]; j=(i[:,0]+dx)%n,(i[:,1]+dy)%n,(i[:,2]+dz)%n; np.add.at(g,j,wx*wy*wz)
 return g/g.mean()-1.
def shells(n,L,s,w):
 q=np.minimum(np.arange(n),n-np.arange(n))*L/n; x,y,z=np.meshgrid(q,q,q,indexing='ij'); r=np.sqrt(x*x+y*y+z*z); k=((r>=s-w/2)&(r<s+w/2)).astype(float); return k/k.sum()
def measure(d,n,L,ss,w,mode):
 dk=np.fft.fftn(d)
 if mode=='cic_deconv':
  k=2*np.pi*np.fft.fftfreq(n,d=L/n); x,y,z=np.meshgrid(k,k,k,indexing='ij'); W=np.sinc(x*(L/n)/(2*np.pi))**2*np.sinc(y*(L/n)/(2*np.pi))**2*np.sinc(z*(L/n)/(2*np.pi))**2; W[0,0,0]=1.; dk=dk/np.maximum(W,.15); dk[0,0,0]=0.
 out1=[];out2=[]
 for s in ss:
  ds=np.fft.ifftn(dk*np.fft.fftn(shells(n,L,s,w))).real; eta=d*ds; m=eta.mean(); out1.append(float(m));out2.append(float(((eta-m)**2).mean()))
 return np.asarray(out1),np.asarray(out2)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--nreal',type=int,default=10); ap.add_argument('--nmesh',type=int,default=64); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); ss=np.arange(40.,300.1,20.); modes=['ngp','cic','cic_deconv']; out={'schema':'cic_convention_audit_v1','nmesh':a.nmesh,'nreal':a.nreal,'s':ss.tolist(),'shell_width':20.,'nodes':{},'modes':modes,'slurm_job_id':os.environ.get('SLURM_JOB_ID'),'hostname':platform.node()}
 for node,fnl in [('fiducial',0),('LC_m',-100),('LC_p',100)]:
  dirs=sorted((a.root/node).glob('real*'))[:a.nreal]; nodeout={}
  for mode in modes:
   a1=[];a2=[]
   for d in dirs:
    p=d/'positions_mpc_h.npy'; pos=np.load(p,mmap_mode='r'); field=ngp_mesh(pos,a.nmesh,1000.) if mode=='ngp' else cic_mesh(pos,a.nmesh,1000.); x,y=measure(field,a.nmesh,1000.,ss,20.,mode); a1.append(x);a2.append(y)
   nodeout[mode]={'n':len(a1),'mean_mu1':np.mean(a1,0).tolist(),'std_mu1':np.std(a1,0,ddof=1).tolist(),'mean_mu2':np.mean(a2,0).tolist(),'std_mu2':np.std(a2,0,ddof=1).tolist()}
  out['nodes'][node]={'fNL':fnl,'realization_ids':[d.name for d in dirs],'conventions':nodeout}
 a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','job':out['slurm_job_id'],'nodes':len(out['nodes']),'modes':modes}))
if __name__=='__main__': main()
