#!/usr/bin/env python3
"""Plot universal vs training-response bphi on CIC-both mu1 model."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

d=json.loads(Path('results/mu1_training_bphi_response_diagnostic_v2.json').read_text())
s=np.arange(40.,300.1,20.)
# Reconstruct universal-bphi prediction from the same stored inputs/parameters is avoided;
# the diagnostic stores the fitted prediction, while convention scan stores universal output.
# Both files are generated under the same CIC-both b1/Pshot convention.
uni=json.loads(Path('results/mu1_training_theory_convention_scan_v1.json').read_text())['nodes']['cic_both']
order=[('fiducial','Fiducial','#1f77b4'),('LC_m','LC_m','#d62728'),('LC_p','LC_p','#2ca02c')]
fig,axes=plt.subplots(3,1,figsize=(8.4,8.2),sharex=True,constrained_layout=True)
for ax,(node,label,color) in zip(axes,order):
  fitrow=d['nodes'][node]; urow=uni['nodes'][node]
  y=np.asarray(fitrow['mean_mu1'],float); e=np.asarray(fitrow['std_realization'],float)
  ax.errorbar(s,y,yerr=e,fmt='o',ms=4,capsize=2,color='black',label='held-out mean +/- sigma_real (30)')
  ax.plot(s,urow['prediction_mu1'],lw=1.8,ls='--',color='0.35',label=f'universal bphi={d["bphi_universal_reference"]:.3f}')
  ax.plot(s,fitrow['prediction_mu1'],lw=2.2,ls='-',color=color,label=f'training bphi={d["bphi_training_fit"]:.3f}')
  ax.axhline(0,color='0.75',lw=.8); ax.set_yscale('symlog',linthresh=1e-4,linscale=1.); ax.set_ylabel('mu1(s)'); ax.set_title(label,loc='left',fontsize=10); ax.grid(True,axis='y',which='both',alpha=.25); ax.legend(fontsize=7.5,frameon=False,ncol=2,loc='best')
axes[-1].set_xlabel('s [h^-1 Mpc]')
fig.suptitle('Training-response bphi correction vs universal branch',fontsize=13)
fig.text(.5,.005,'Both curves use CIC on clustering and shot, b1=2.7413 and Pshot=5467.8 from fiducial training power. Points/errorbars are held-out mean and realization scatter; no held-out response fit.',ha='center',va='bottom',fontsize=8)
out=Path('results/mu1_bphi_training_vs_universal.pdf'); fig.savefig(out,format='pdf',metadata={'Title':'Training versus universal bphi mu1 comparison','Author':'Codex'}); plt.close(fig); print(out,out.stat().st_size)
