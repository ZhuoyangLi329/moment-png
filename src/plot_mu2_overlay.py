#!/usr/bin/env python3
from pathlib import Path
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
root=Path("/pscratch/sd/l/lzy/byd2pcf")
fit=json.loads((root/"results/mu2_training_ph_calibration_holdout_v2.json").read_text())
s=np.asarray(fit["s"],float)
nodes=[("fiducial","fNL=0","#1f77b4"),("LC_m","fNL=-100","#d62728"),("LC_p","fNL=+100","#2ca02c")]
fig,ax=plt.subplots(3,1,figsize=(10,11),sharex=True)
for node,label,color in nodes:
 d=fit["nodes"][node]; pred=np.asarray(d["prediction_mu2_gaussian"],float); mean=np.asarray(d["mean_nbody_mu2_gaussian"],float); sig=np.asarray(d["std_realization"],float)
 c=np.load(root/f"results/resolution_clean/connected_{node}_n64.npz"); raw=np.asarray(c["mu2"])[70:100]; con=np.asarray(c["mu2_connected"])[70:100]
 ax[0].errorbar(s,mean,yerr=sig,fmt="o",ms=3,color=color,label=label+" heldout"); ax[0].plot(s,pred,color=color,lw=2,label=label+" train fit")
 ax[1].errorbar(s,raw.mean(0),yerr=raw.std(0,ddof=1),fmt="o",ms=3,color=color,label=label); ax[1].plot(s,pred,color=color,ls="--",lw=1.4)
 ax[2].errorbar(s,con.mean(0),yerr=con.std(0,ddof=1),fmt="o",ms=3,color=color,label=label)
for a in ax: a.grid(alpha=.25); a.legend(ncol=3,fontsize=8)
ax[0].set_yscale("symlog",linthresh=1e-3); ax[1].set_yscale("symlog",linthresh=1e-3); ax[2].set_yscale("symlog",linthresh=1e-5); ax[2].axhline(0,color="k",lw=.8); ax[2].set_xlabel("s [Mpc/h]")
ax[0].set_ylabel("mu2_G"); ax[1].set_ylabel("raw mu2"); ax[2].set_ylabel("connected mu2")
fig.suptitle("mu2 diagnostic overlay: all three fNL curves together",fontsize=14); fig.text(.5,.012,"Training fits use 70 realizations; markers use 30 heldout realizations and sigma_real. Ngrid=64; raw and connected panels are diagnostic only.",ha="center",fontsize=8); fig.tight_layout(rect=[0,0.035,1,.96])
out=root/"results/mu2_training_gaussian_raw_connected_overlay.pdf"; fig.savefig(out,format="pdf",metadata={"Title":"mu2 all fNL overlay","Author":"Codex"}); print(json.dumps({"status":"PASS","output":str(out),"bytes":out.stat().st_size}))

