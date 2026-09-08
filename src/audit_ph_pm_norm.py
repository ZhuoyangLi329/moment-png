import json
from pathlib import Path
import numpy as np

def main():
 root=Path('/pscratch/sd/l/lzy/byd2pcf'); n=np.load(root/'inputs/quijote_fiducial_z1_theory_lattice64.npz'); k=np.asarray(n['k']); pm=np.asarray(n['Pm']); h=np.load(root/'results/power_real_n100_n64/power_fiducial_n64.npz'); kh=np.asarray(h['k']); ph=np.asarray(h['mean_P']); nmode=np.asarray(h['nmodes']);
 # mean external Pm in the same half-open 0.005 k bins used by measured P_h.
 edges=np.r_[kh-0.0025,kh[-1]+0.0025]; bins=np.digitize(k,edges)-1; pmb=np.array([pm[bins==i].mean() if np.any(bins==i) else np.nan for i in range(len(kh))]); counts=np.array([(bins==i).sum() for i in range(len(kh))]); ratio=ph/np.maximum(pmb,1e-30); out={'schema':'ph_pm_normalization_audit_v1','nmesh':64,'boxsize':1000.,'power_k':kh.tolist(),'measured_mean_P_h':ph.tolist(),'external_mode_mean_Pm':pmb.tolist(),'external_mode_counts':counts.tolist(),'measured_to_external_ratio':ratio.tolist(),'b1_squared_reference':2.7340475186190334**2,'scope':'same Fourier bins; external Pm mode interpolation/binning versus measured halo mesh power','warning':'This is a normalization diagnostic; shot noise, nonlinear bias, and CIC/alias conventions are not fitted here.'}; (root/'results/ph_pm_normalization_audit_v1.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','first_rows':[(float(kh[i]),float(ph[i]),float(pmb[i]),float(ratio[i]),int(counts[i])) for i in range(5)]}))
if __name__=='__main__':main()
