***************************************************************************
                          NOTICE TO USERS

Lawrence Berkeley National Laboratory operates this computer system under 
contract to the U.S. Department of Energy.  This computer system is the 
property of the United States Government and is for authorized use only.
Users (authorized or unauthorized) have no explicit or implicit 
expectation of privacy.

Any or all uses of this system and all files on this system may be
intercepted, monitored, recorded, copied, audited, inspected, and disclosed
to authorized site, Department of Energy, and law enforcement personnel,
as well as authorized officials of other agencies, both domestic and foreign.
By using this system, the user consents to such interception, monitoring,
recording, copying, auditing, inspection, and disclosure at the discretion
of authorized site or Department of Energy personnel.

Unauthorized or improper use of this system may result in administrative
disciplinary action and civil and criminal penalties. By continuing to use
this system you indicate your awareness of and consent to these terms and
conditions of use. LOG OFF IMMEDIATELY if you do not agree to the conditions
stated in this warning.

*****************************************************************************

Login connection to host x3116c0s5b0n0:

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

