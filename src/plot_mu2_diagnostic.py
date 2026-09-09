#!/usr/bin/env python3
"""Dedicated diagnostic figure for Gaussian, raw, and connected mu2."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('/pscratch/sd/l/lzy/byd2pcf'); out=root/'results/mu2_training_gaussian_raw_connected_diagnostic.pdf'; fit=json.loads((root/'results/mu2_training_ph_calibration_holdout_v2.json').read_text()); ss=np.asarray(fit['s'],float); nodes=['fiducial','LC_m','LC_p']; labels=['fiducial (fNL=0)','LC_m (fNL=-100)','LC_p (fNL=+100)']; colors=['#1f77b4','#d62728','#2ca02c']; fig,ax=plt.subplots(3,3,figsize=(13,10),sharex='col')
for j,(node,label,color) in enumerate(zip(nodes,labels,colors)):
 d=fit['nodes'][node]; pred=np.asarray(d['prediction_mu2_gaussian'],float); mean=np.asarray(d['mean_nbody_mu2_gaussian'],float); sig=np.asarray(d['std_realization'],float); c=np.load(root/f'results/resolution_clean/connected_{node}_n64.npz'); raw=np.asarray(c['mu2'])[70:100]; con=np.asarray(c['mu2_connected'])[70:100]; rawm=raw.mean(0); raws=raw.std(0,ddof=1); conm=con.mean(0); cons=con.std(0,ddof=1)
 ax[0,j].errorbar(ss,mean,yerr=sig,fmt='o',ms=3,color=color,alpha=.8,label='30 held-out mean ± sigma_real'); ax[0,j].plot(ss,pred,'k-',lw=1.8,label='70-training P_h curve'); ax[0,j].set_yscale('symlog',linthresh=1e-3); ax[0,j].grid(alpha=.25); ax[0,j].set_title(label)
 ax[1,j].errorbar(ss,rawm,yerr=raws,fmt='o',ms=3,color=color,alpha=.8,label='raw mu2 held-out'); ax[1,j].plot(ss,pred,'k--',lw=1.5,label='Gaussian baseline'); ax[1,j].set_yscale('symlog',linthresh=1e-3); ax[1,j].grid(alpha=.25)
 ax[2,j].errorbar(ss,conm,yerr=cons,fmt='o',ms=3,color=color,alpha=.8,label='connected held-out'); ax[2,j].axhline(0,color='k',lw=.8); ax[2,j].set_yscale('symlog',linthresh=1e-5); ax[2,j].grid(alpha=.25)
for j in range(3): ax[2,j].set_xlabel('s [Mpc/h]')
ax[0,0].set_ylabel('mu2_G'); ax[1,0].set_ylabel('raw mu2'); ax[2,0].set_ylabel('connected mu2')
for r in range(3): ax[r,0].legend(fontsize=7,loc='best')
fig.suptitle('mu2 diagnostic: training Gaussian baseline, raw moment, and connected residual',fontsize=14); fig.text(.5,.012,'Curves use only 70 training realizations; points/error bars use 30 held-out realizations and sigma_real. Ngrid=64, exact periodic shells, s=40-300. Connected and raw panels are not production-closed.',ha='center',fontsize=8); fig.tight_layout(rect=[0,0.035,1,.96]); fig.savefig(out,format='pdf',metadata={'Title':'Gaussian raw and connected mu2 diagnostic','Author':'Codex'}); print(json.dumps({'status':'PASS','output':str(out),'bytes':out.stat().st_size,'nodes':nodes}))
