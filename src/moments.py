
#!/usr/bin/env python
"""Periodic-box ConKer-style shell moments for Quijote position catalogs."""
import argparse, json
from pathlib import Path
import numpy as np

def cic_mesh(pos, nmesh, boxsize):
    grid = np.zeros((nmesh, nmesh, nmesh), dtype=np.float64)
    u = np.asarray(pos, dtype=float) / boxsize * nmesh
    i0 = np.floor(u).astype(np.int64); f = u - i0
    for dx in (0,1):
      wx = (1-f[:,0]) if dx == 0 else f[:,0]
      for dy in (0,1):
       wy = (1-f[:,1]) if dy == 0 else f[:,1]
       for dz in (0,1):
        wz = (1-f[:,2]) if dz == 0 else f[:,2]
        ind = (i0[:,0]+dx)%nmesh, (i0[:,1]+dy)%nmesh, (i0[:,2]+dz)%nmesh
        np.add.at(grid, ind, wx*wy*wz)
    return grid / grid.mean() - 1.

def shell_kernel(nmesh, boxsize, radius, width):
    x = np.fft.fftfreq(nmesh, d=boxsize/nmesh) * nmesh
    # centered periodic coordinate in mesh cells
    q = np.arange(nmesh)
    q = np.minimum(q, nmesh-q) * boxsize/nmesh
    xx, yy, zz = np.meshgrid(q,q,q,indexing='ij')
    rr = np.sqrt(xx*xx+yy*yy+zz*zz)
    mask = (rr >= radius-width/2) & (rr < radius+width/2)
    k = mask.astype(float)
    if not k.any(): raise ValueError(f"empty shell radius={radius} width={width}")
    return k / k.sum()

def measure(positions, boxsize, nmesh, scales, width):
    delta = cic_mesh(positions, nmesh, boxsize)
    dk = np.fft.fftn(delta)
    out1=[]; out2=[]
    for s in scales:
        ker = shell_kernel(nmesh, boxsize, s, width)
        ds = np.fft.ifftn(dk*np.fft.fftn(ker)).real
        eta = delta*ds
        m1 = float(eta.mean())
        out1.append(m1); out2.append(float(((eta-m1)**2).mean()))
    return np.asarray(out1), np.asarray(out2)

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('catalog', type=Path)
    ap.add_argument('--nmesh',type=int,default=128)
    ap.add_argument('--boxsize',type=float,default=1000.)
    ap.add_argument('--smin',type=float,default=20.)
    ap.add_argument('--smax',type=float,default=300.)
    ap.add_argument('--ds',type=float,default=20.)
    ap.add_argument('--shell-width',type=float,default=20.)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    pos=np.load(a.catalog)
    scales=np.arange(a.smin,a.smax+0.1,a.ds)
    m1,m2=measure(pos,a.boxsize,a.nmesh,scales,a.shell_width)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    np.savez(a.output,s=scales,mu1=m1,mu2=m2,nmesh=a.nmesh,boxsize=a.boxsize,
             shell_width=a.shell_width,n_halo=len(pos))
    print(json.dumps({'catalog':str(a.catalog),'n_halo':len(pos),'nmesh':a.nmesh,
                      'scales':scales.tolist(),'mu1':m1.tolist(),'mu2':m2.tolist()}))

