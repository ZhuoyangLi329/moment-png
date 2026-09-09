#!/usr/bin/env python3
"""Plot training-fit mu1 curves for CIC/shot convention scan."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

d=json.loads(Path('results/mu1_training_theory_convention_scan_v1.json').read_text())
s=np.arange(40.,300.1,20.)
variants=[('cic_both','CIC clustering + CIC shot','#1f77b4','-'),('cic_cluster_shot_plain','CIC clustering + plain shot','#d62728','--'),('plain_both','no CIC','#2ca02c',':')]
nodes=[('fiducial','Fiducial'),('LC_m','LC_m'),('LC_p','LC_p')]
fig,axes=plt.subplots(3,1,figsize=(8.4,8.2),sharex=True,constrained_layout=True)
for ax,(node,label) in zip(axes,nodes):
  # Measured heldout data are shared across convention variants.
  ref=d['nodes']['cic_both']['nodes'][node]
  y=np.asarray(ref['mean_mu1'],float); e=np.asarray(ref['std_realization'],float)
  ax.errorbar(s,y,yerr=e,fmt='o',ms=4,capsize=2,color='black',label='held-out mean +/- sigma_real (30)')
  ax.axhline(0,color='0.72',lw=.8)
  for key,vlabel,color,ls in variants:
    row=d['nodes'][key]['nodes'][node]
    ax.plot(s,row['prediction_mu1'],ls=ls,lw=2,color=color,label=f'{vlabel} (chi2/dof={row["chi2_dof"]:.2f})')
  ax.set_yscale('symlog',linthresh=1e-4,linscale=1.)
  ax.set_ylabel('mu1(s)')
  ax.set_title(label,loc='left',fontsize=10)
  ax.grid(True,axis='y',which='both',alpha=.25)
  ax.legend(fontsize=7.5,frameon=False,ncol=2,loc='best')
axes[-1].set_xlabel('s [h^-1 Mpc]')
fig.suptitle('Training-only mu1 theory convention scan vs held-out N-body',fontsize=13)
fig.text(.5,.005,'Curves fit fiducial training real000-real069 P_h at k<=0.08; points/errorbars are held-out real070-real099 mean and realization scatter. Symlog y-axis.',ha='center',va='bottom',fontsize=8)
out=Path('results/mu1_training_convention_scan_vs_nbody.pdf')
fig.savefig(out,format='pdf',metadata={'Title':'Mu1 CIC and shot convention scan','Author':'Codex'})
plt.close(fig)
print(out,out.stat().st_size)
