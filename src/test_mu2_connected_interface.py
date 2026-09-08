
import sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from theory_mu2_marisa_b import connected_local_png_mu2
k=np.linspace(.02,.08,8); p=lambda x:1/(1+x*x); t=lambda x:1.; out=connected_local_png_mu2(k,np.ones(8),40,20,p,t,1,nsamp=80,seed=1); assert np.isfinite(out['mu2_connected_primordial']) and out['mu2_connected_error']>=0; print({'status':'PASS','connected_interface':True,'error_reported':True})
