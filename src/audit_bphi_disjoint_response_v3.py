#!/usr/bin/env python3
"""Audit the corrected c=b1*bphi disjoint response refit."""
import argparse, datetime, hashlib, json, math
from pathlib import Path

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inventory', type=Path, required=True)
    ap.add_argument('--calibration', type=Path, required=True)
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--shape', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    inv = json.loads(args.inventory.read_text())
    cal = json.loads(args.calibration.read_text())
    run = json.loads(args.run.read_text())
    shape = json.loads(args.shape.read_text())
    ids = [str(x) for x in cal.get('realization_ids', [])]
    expected = [f'real{i:03d}' for i in range(100, 500)]
    checks = [
        {'name': 'inventory_disjoint_pair', 'status': 'PASS' if inv.get('disjoint_png_pair_available') is True and inv.get('decision') == 'AVAILABLE_FOR_CALIBRATION' else 'BLOCKED'},
        {'name': 'corrected_schema', 'status': 'PASS' if cal.get('schema') == 'bphi_disjoint_response_calibration_v3' else 'BLOCKED'},
        {'name': 'paired_ids', 'status': 'PASS' if ids == expected else 'BLOCKED', 'nreal': len(ids)},
        {'name': 'immutable_batch_run', 'status': 'PASS' if str(run.get('slurm_job_id','')).isdigit() and run.get('calculation_finished') is True and len(str(run.get('code_commit',''))) == 40 else 'BLOCKED', 'slurm_job_id': run.get('slurm_job_id')},
    ]
    bphi = float(cal.get('bphi_conditional', float('nan')))
    sigma = float(cal.get('bphi_sigma_statistical_conditional', float('nan')))
    checks.append({'name': 'finite_corrected_bphi', 'status': 'PASS' if math.isfinite(bphi) and math.isfinite(sigma) and sigma > 0 else 'BLOCKED'})
    chi = float(cal.get('fit', {}).get('chi2_dof', float('inf')))
    checks.append({'name': 'predeclared_template_shape', 'status': 'PASS' if chi <= 5.0 else 'REJECTED_SHAPE', 'chi2_dof': chi, 'threshold': 5.0})
    stress = {k: float(v.get('chi2_dof', float('inf'))) for k, v in shape.get('fits', {}).items()}
    structural = all(x['status'] == 'PASS' for x in checks[:5])
    out = {
        'schema': 'bphi_disjoint_response_audit_v3',
        'status': 'PASS' if structural and chi <= 5.0 else 'BLOCKED',
        'decision': 'CALIBRATION_AVAILABLE_REVIEW_REQUIRED' if structural and chi <= 5.0 else 'CALIBRATION_SOURCE_AVAILABLE_SHAPE_REJECTED',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'checks': checks, 'bphi_conditional_corrected': bphi,
        'bphi_sigma_statistical_conditional': sigma,
        'c_b1_times_bphi': cal.get('c_b1_times_bphi'),
        'hartlap_chi2_dof': cal.get('fit', {}).get('hartlap_chi2_dof'),
        'shape_basis_stress_chi2_dof': stress,
        'inventory': str(args.inventory), 'inventory_sha256': sha(args.inventory),
        'calibration': str(args.calibration), 'calibration_sha256': sha(args.calibration),
        'run_provenance': str(args.run), 'run_provenance_sha256': sha(args.run),
        'shape_diagnostic': str(args.shape), 'shape_diagnostic_sha256': sha(args.shape),
        'scope': 'corrected independent/disjoint LC+/- response calibration for frozen FoF z=1 Mh>=1e13 real-space CIC selection',
        'policy': {'heldout_response_fit': False, 'universal_mass_function_not_promoted': True,
                   'production_requires_shape_quality_and_b1_cross_covariance': True,
                   'double_b1_division_corrected': True, 'production_promotion': False},
        'warning': 'The corrected normalization changes the conditional bphi label; the response shape remains rejected and b1 uncertainty/cross-covariance are still absent.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'status': out['status'], 'decision': out['decision'], 'bphi': bphi, 'chi2_dof': chi}))

if __name__ == '__main__':
    main()
