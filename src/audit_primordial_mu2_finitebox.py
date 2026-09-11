#!/usr/bin/env python3
"""Finite-box primordial local trispectrum diagnostic with zero-mode removal."""
import argparse, json, hashlib
from pathlib import Path
import numpy as np
from local_trispectrum import collapsed_mu2_local_mc

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--nsamp', type=int, default=20000)
    a = ap.parse_args()
    d = np.load(a.root / 'inputs/quijote_fiducial_z1_theory.npz')
    L = 1000.0
    kfund = 2 * np.pi / L
    kg0 = np.asarray(d['k'], float)
    keep = (kg0 >= kfund) & (kg0 < .3)
    kg = kg0[keep]
    pp = np.asarray(d['Pphi'], float)[keep]
    mm = np.asarray(d['M'], float)[keep]
    def pphi(q):
        q = float(q)
        return 0.0 if q < kfund / 2 else float(np.interp(q, kg, pp, left=0.0, right=pp[-1]))
    def transfer(q):
        q = float(q)
        return 0.0 if q < kfund / 2 else float(np.interp(q, kg, mm, left=0.0, right=mm[-1]))
    b1 = 2.7340475186190334
    shells = np.arange(40.0, 300.1, 20.0)
    rows = []
    for s in shells:
        window = lambda q, ss=float(s): float(np.sinc(float(q) * ss / np.pi))
        val, err = collapsed_mu2_local_mc(kg, pphi, lambda q: b1 * transfer(q), window, fnl=100.0, gnl=0.0, nsamp=a.nsamp, seed=int(s))
        rows.append({'s': float(s), 'mu2_primordial_fNL100': val, 'mc_error': err})
    c0 = np.load(a.root / 'results/resolution_clean/connected_fiducial_n64.npz')
    cm = np.load(a.root / 'results/resolution_clean/connected_LC_m_n64.npz')
    cp = np.load(a.root / 'results/resolution_clean/connected_LC_p_n64.npz')
    even = ((np.asarray(cp['mu2_connected']).mean(0) + np.asarray(cm['mu2_connected']).mean(0)) / 2 - np.asarray(c0['mu2_connected']).mean(0)) / 10000.0
    rows = [dict(x, measured_connected_even_response=float(y), difference=float(x['mu2_primordial_fNL100'] - y), abs_pull=float((x['mu2_primordial_fNL100'] - y) / max(x['mc_error'], 1e-30))) for x, y in zip(rows, even)]
    out = {'status': 'DIAGNOSTIC', 'schema': 'primordial_mu2_trispectrum_component_audit_v2', 'b1': b1, 'fNL': 100.0, 'n_samples': a.nsamp, 'inputs': {'theory': str(a.root / 'inputs/quijote_fiducial_z1_theory.npz'), 'theory_sha256': sha(a.root / 'inputs/quijote_fiducial_z1_theory.npz'), 'fiducial_connected_sha256': sha(a.root / 'results/resolution_clean/connected_fiducial_n64.npz'), 'LC_m_connected_sha256': sha(a.root / 'results/resolution_clean/connected_LC_m_n64.npz'), 'LC_p_connected_sha256': sha(a.root / 'results/resolution_clean/connected_LC_p_n64.npz')}, 'boxsize_mpc_h': L, 'kfund': kfund, 'zero_mode_policy': 'P_phi(q<kfund/2)=M(q<kfund/2)=0, including collapsed internal zero modes', 's': [float(x) for x in shells], 'components': rows, 'scope': 'finite-box continuum MC local primordial trispectrum diagnostic; no halo bias/contact closure', 'policy': {'same_nodes': True, 'response_formula': '((LC_p+LC_m)/2-fiducial)/100^2', 'no_parameter_fit': True, 'production_promotion': False}, 'warning': 'This corrected finite-box baseline is still continuum MC and does not supply halo b2/bK2/bphi/bphidelta or clustered contacts.'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    pulls = [x['abs_pull'] for x in rows]
    print(json.dumps({'status': out['status'], 'mean_abs_pull': float(np.mean(pulls)), 'max_abs_pull': float(np.max(pulls))}))

if __name__ == '__main__':
    main()

