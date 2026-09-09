#!/usr/bin/env python3
"""Plot training-only best-fit P_h calibration against held-out mean mu1."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

src = Path('results/mu1_training_ph_calibration_holdout_v1.json')
out = Path('results/mu1_training_bestfit_vs_measured.pdf')
d = json.loads(src.read_text())
s = np.asarray(d['s'], float)
order = [('fiducial', 'Fiducial (fNL=0)', '#1f77b4'), ('LC_m', r'LC$_m$ (fNL=-100)', '#d62728'), ('LC_p', r'LC$_p$ (fNL=+100)', '#2ca02c')]
fig, axes = plt.subplots(3, 1, figsize=(7.4, 8.2), sharex=True, constrained_layout=True)
for ax, (node, label, color) in zip(axes, order):
    row = d['nodes'][node]
    y = np.asarray(row['mean_nbody_mu1'], float)
    e = np.asarray(row.get('std_realization', row['se_mean']), float)
    fit = np.asarray(row['prediction_mu1'], float)
    ax.axhline(0, color='0.75', lw=0.8, zorder=0)
    ax.errorbar(s, y, yerr=e, fmt='o', ms=4.0, capsize=2.0, lw=1.0, color='k', label='held-out mean +/- sigma_real (30)')
    ax.plot(s, fit, color=color, lw=2.0, marker='s', ms=3.0, label='training $P_h(k)$ calibrated curve')
    ax.set_ylabel(r'$mu_1(s)$')
    ax.set_yscale('symlog', linthresh=1e-4, linscale=1.0)
    ax.set_title(f'{label}; $\chi^2/\mathrm{{dof}}={row["chi2_dof"]:.2f}$', loc='left', fontsize=10)
    ax.grid(True, axis='y', alpha=0.25)
    ax.legend(loc='best', fontsize=8, frameon=False)
axes[-1].set_xlabel(r'$s\ [h^{-1}\,\mathrm{Mpc}]$')
fig.suptitle('Leakage-free training calibration vs held-out N-body $\mu_1$', fontsize=13)
fig.text(0.5, 0.005, 'Fit diagnostic uses only real000–real069 mean $P_h(k)$; held-out real070–real099 enters only the points and error bars.  Ngrid=64, exact periodic lattice shell window.', ha='center', va='bottom', fontsize=8)
fig.savefig(out, format='pdf', metadata={'Title':'Training P_h calibration versus held-out N-body mu1','Author':'Codex'})
plt.close(fig)
print(out, out.stat().st_size)
