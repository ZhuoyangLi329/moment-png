#!/usr/bin/env python3
"""Covariance-aware held-out validation for the frozen tree mu1 model."""
import argparse, json
from pathlib import Path
import numpy as np
from scipy.stats import chi2 as chi2_dist

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prediction-dir', required=True, type=Path)
    ap.add_argument('--moments-dir', required=True, type=Path)
    ap.add_argument('--holdout-start', type=int, default=70)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    rows = []
    for node, fnl in {'fiducial': 0, 'LC_m': -100, 'LC_p': 100}.items():
        pred = json.loads((a.prediction_dir / f'mu1_universal_p112_exact_n64_fnl{fnl}.json').read_text())
        s = np.array([x['s'] for x in pred['predictions']], float)
        model = np.array([x['mu1'] for x in pred['predictions']], float)
        d = np.load(a.moments_dir / f'moments_{node}_n64.npz')
        z = np.asarray(d['mu1'], float)[a.holdout_start:]
        n = len(z); mean = z.mean(0); cov_real = np.cov(z, rowvar=False, ddof=1); cov = cov_real / n
        residual = mean - model
        precision = np.linalg.pinv(cov, rcond=1e-10)
        pull = residual / np.sqrt(np.maximum(np.diag(cov), 1e-30))
        chi = float(residual @ precision @ residual); dof = int(len(residual))
        hartlap = (n - dof - 2) / (n - 1) if n > dof + 2 else None
        hchi = float(hartlap * chi) if hartlap is not None else None
        rows.append({'node': node, 'fNL': fnl, 'n_holdout': n, 's': s.tolist(),
            'mean_mu1': mean.tolist(), 'model_mu1': model.tolist(),
            'se_mean': np.sqrt(np.diag(cov)).tolist(), 'pull': pull.tolist(),
            'rms_pull': float(np.sqrt(np.mean(pull * pull))), 'chi2': chi,
            'dof': dof, 'chi2_dof': chi / dof, 'hartlap_factor': hartlap,
            'hartlap_chi2': hchi, 'hartlap_chi2_dof': hchi / dof if hchi is not None else None,
            'hartlap_pvalue': float(chi2_dist.sf(hchi, dof)) if hchi is not None else None,
            'coverage_fraction_abs_pull_le_2': float(np.mean(np.abs(pull) <= 2)),
            'covariance_condition_number': float(np.linalg.cond(cov_real)),
            'covariance_inverse': 'pinv_rcond_1e-10',
            'covariance_estimator': 'sample covariance of holdout realizations divided by n_holdout'})
    out = {'status': 'PASS', 'schema': 'mu1_nbody_tree_validation_v2',
        'model': 'tree exact discrete mesh + universal bphi p=1.12',
        'prediction_dir': str(a.prediction_dir), 'holdout_start': a.holdout_start,
        'nodes': rows, 'scope': 'node-matched N-body held-out mean validation; no response fitting',
        'policy': {'same_split_all_nodes': True, 'png_response_fit': False,
                   'scale_list_frozen': True, 'hartlap_reported': True,
                   'parameter_uncertainty_propagated': False},
        'warning': 'PASS means the diagnostic ran; universal bphi remains an assumption and acceptance requires frozen independent provenance.'}
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'chi2_dof': {r['node']: round(r['chi2_dof'], 2) for r in rows},
                      'hartlap': {r['node']: r['hartlap_factor'] for r in rows}}))

if __name__ == '__main__': main()
