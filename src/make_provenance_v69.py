#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
from pathlib import Path

def sha(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--commit', required=True)
    a = ap.parse_args()
    root = a.root
    old = json.loads((root / 'results/run_provenance_v68.json').read_text())
    old['schema'] = 'run_provenance_v69'
    old['created_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    old['github_main_commit'] = a.commit
    old['completed_batch_jobs'] = list(dict.fromkeys(old.get('completed_batch_jobs', []) + [58194506, 58194794, 58195306]))
    old['latest_job'] = {'slurm_job_id': 58195306, 'state': 'COMPLETED', 'exit_code': '0:0', 'elapsed': '00:00:13', 'node': 'nid004092', 'account': 'desi', 'qos': 'shared', 'partition': 'shared_milan_ss11', 'cpus': 2, 'memory': '3810M'}
    old['stage_progress'] = 'results/stage_progress_v19.json'
    old['stage_progress_sha256'] = sha(root / 'results/stage_progress_v19.json')
    entries = {
        'reconstruction_manifest': 'results/reconstruct_png_catalogs_58194506.json',
        'reconstruction_provenance': 'results/reconstruction_provenance_v2_58194506.json',
        'bphi_inventory': 'results/bphi_disjoint_catalog_inventory_v2.json',
        'bphi_response_calibration': 'results/bphi_disjoint_response_calibration_v3_58195306.json',
        'bphi_response_provenance': 'results/slurm_bphirefit_provenance_58195306.json',
        'bphi_response_audit': 'results/bphi_disjoint_response_audit_v2_58195306.json',
        'stage6_bphi_gate': 'results/stage6_bphi_disjoint_gate_v1.json',
    }
    for key, rel in entries.items():
        old['batch_outputs'][key] = rel
        old['batch_outputs'][key + '_sha256'] = sha(root / rel)
    old['open_items'] = list(dict.fromkeys(old.get('open_items', []) + ['Disjoint LC+/- response source is available, but external Pm/M response shape fails with chi2/dof=207.04; b1 covariance is not propagated and production bphi remains blocked.']))
    old['status'] = 'PARTIAL'
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(old, indent=2) + '\n')
    print(json.dumps({'status': old['status'], 'commit': a.commit, 'latest_job': old['latest_job'], 'stage_progress_sha256': old['stage_progress_sha256']}))

if __name__ == '__main__':
    main()
