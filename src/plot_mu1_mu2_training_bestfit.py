#!/usr/bin/env python3
"""Overlay training-only best-fit and held-out means for mu1 and Gaussian mu2."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

m1 = json.loads(Path('results/mu1_training_ph_calibration_holdout_v2.json').read_text())
m2 = json.loads(Path('results/mu2_training_ph_calibration_holdout_v2.json').read_text())
s = np.asarray(m1['s'], float)
order = [('fiducial', 'Fiducial', '#1f77b4'), ('LC_m', r'LC$_m$', '#d62728'), ('LC_p', r'LC$_p$', '#2ca02c')]
fig, axes = plt.subplots(2, 1, figsize=(8.2, 7.0), sharex=True, constrained_layout=True)
for ax, dat, ykey, fitkey, title in [
    (axes[0], m1, 'mean_nbody_mu1', 'prediction_mu1', r'$\mu_1$'),
    (axes[1], m2, 'mean_nbody_mu2_gaussian', 'prediction_mu2_gaussian', r'$\mu_{2,G}$')]:
    ax.axhline(0, color='0.72', lw=0.8, zorder=0)
    for node, label, color in order:
        row = dat['nodes'][node]
        y = np.asarray(row[ykey], float)
        e = np.asarray(row.get('std_realization', row['se_mean']), float)
        fit = np.asarray(row[fitkey], float)
        ax.errorbar(s, y, yerr=e, fmt='o', ms=3.5, capsize=1.8, lw=0.8, color=color, alpha=0.78, label=f'{label} measured mean +/- sigma_real')
        ax.plot(s, fit, '-', color=color, lw=1.9, label=f'{label} training Ph fit')
    ax.set_yscale('symlog', linthresh=1e-4, linscale=1.0)
    if ykey == 'mean_nbody_mu2_gaussian':
        ax.set_ylim(bottom=1e-3)
    ax.set_ylabel(title)
    ax.grid(True, axis='y', which='both', alpha=0.25)
    ax.legend(loc='best', ncol=2, fontsize=7.5, frameon=False)
axes[-1].set_xlabel(r'$s\ [h^{-1}\,\mathrm{Mpc}]$')
fig.suptitle('Training-only best-fit overlays vs held-out N-body means', fontsize=13)
fig.text(0.5, 0.005, 'Symlog y-axis; points are means over 30 held-out realizations and error bars are realization scatter sigma_real. Curves use only 70 training realizations. Ngrid=64 exact periodic window; lower panel is Gaussian mu2 only and ymin=1e-3.', ha='center', va='bottom', fontsize=8)
out = Path('results/mu1_mu2_training_bestfit_vs_measured_symlog.pdf')
fig.savefig(out, format='pdf', metadata={'Title':'Training-only best-fit overlays versus held-out N-body means','Author':'Codex'})
plt.close(fig)
print(out, out.stat().st_size)
