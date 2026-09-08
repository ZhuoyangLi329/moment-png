
#!/usr/bin/env python3
"""Held-out validation for a frozen analytic mu1 prediction."""
import argparse,json
from pathlib import Path
import numpy as np
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--prediction",required=True,type=Path); ap.add_argument("--moments-dir",required=True,type=Path); ap.add_argument("--holdout-start",type=int,default=70); ap.add_argument("--output",required=True,type=Path); a=ap.parse_args()
 pred=json.loads(a.prediction.read_text()); s=np.asarray(pred["s"],float); model=np.asarray(pred["mu1_prediction"],float); rows=[]
 for node in ("fiducial","LC_m","LC_p"):
  d=np.load(a.moments_dir/f"moments_{node}_n64.npz"); y=np.asarray(d["mu1"],float)
  if y.shape[1]!=len(s): raise ValueError(f"scale mismatch for {node}")
  z=y[a.holdout_start:]; mean=z.mean(0); se=z.std(0,ddof=1)/np.sqrt(len(z)); pull=(mean-model)/np.maximum(se,1e-30)
  rows.append({"node":node,"fNL":float(d["fNL"]),"n_holdout":int(len(z)),"mean_mu1":mean.tolist(),"se_mu1":se.tolist(),"pull_vs_model":pull.tolist(),"rms_pull":float(np.sqrt(np.mean(pull*pull)))})
 out={"status":"PASS","prediction_source":str(a.prediction),"holdout_start":a.holdout_start,"s":s.tolist(),"nodes":rows,"scope":"held-out comparison only; no response fitting or parameter calibration","warning":"PASS means workflow ran; scientific acceptance still requires external Pm/M/bphi provenance and predeclared tolerances."}
 a.output.write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps({"status":"PASS","nodes":len(rows),"holdout":rows[0]["n_holdout"]}))
if __name__=="__main__": main()

