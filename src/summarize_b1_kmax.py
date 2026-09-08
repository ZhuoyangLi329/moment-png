import json
from pathlib import Path
import numpy as np

def main():
 d=json.load(open('results/fiducial_b1_nbody_diagnostic_v1.json')); k=np.array(d['k']); out={'schema':'fiducial_b1_kmax_summary_v1','source':'results/fiducial_b1_nbody_diagnostic_v1.json','nmesh':d['nmesh'],'nreal':d['nreal'],'scans':{}}
 for cut in [.03,.05,.08,.1,.15]:
  m=k<=cut; out['scans'][str(cut)]={}
  for name in ['b1_raw','b1_cic_corrected']:
   x=np.array(d[name])[m]; out['scans'][str(cut)][name]={'n_k':int(m.sum()),'mean':float(x.mean()),'std_over_k':float(x.std(ddof=1)),'first':float(x[0]),'last':float(x[-1])}
 Path('results/fiducial_b1_kmax_summary_v1.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__':main()
