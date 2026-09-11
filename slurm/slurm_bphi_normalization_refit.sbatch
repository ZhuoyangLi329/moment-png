#!/bin/bash
#SBATCH --job-name=bphi_norm_audit
#SBATCH --account=desi
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:20:00
#SBATCH --chdir=/pscratch/sd/l/lzy/byd2pcf
#SBATCH --output=results/bphi_norm_%j.out
#SBATCH --error=results/bphi_norm_%j.err
set -euo pipefail
root=/pscratch/sd/l/lzy/byd2pcf
repo=/pscratch/sd/l/lzy/moment-png-sync
export CODE_COMMIT="${1:?Pass the full main commit to freeze for this run}"
test "${#CODE_COMMIT}" -eq 40
git -C "$repo" cat-file -e "${CODE_COMMIT}^{commit}"
git -C "$repo" merge-base --is-ancestor "$CODE_COMMIT" origin/main
export RUN_OUT="results/bphi_normalization_refit_${SLURM_JOB_ID}"
mkdir -p "$root/$RUN_OUT/code"
git -C "$repo" archive "$CODE_COMMIT" src | tar -xf - -C "$root/$RUN_OUT/code"
export PYTHONPATH="$root/$RUN_OUT/code/src"
python -m unittest discover -s "$PYTHONPATH" -p test_bphi_response_normalization.py -v > "$RUN_OUT/regression_tests.log" 2>&1
python "$PYTHONPATH/fit_bphi_disjoint_response.py" \
  --moments-root results/disjoint_png_moments_58194794 \
  --input inputs/quijote_fiducial_z1_theory_lattice64.npz \
  --b1 2.7317333004945543 --output "$RUN_OUT/calibration.json"
python "$PYTHONPATH/audit_bphi_response_shape_basis.py" \
  --moments-root results/disjoint_png_moments_58194794 \
  --theory inputs/quijote_fiducial_z1_theory_lattice64.npz \
  --output "$RUN_OUT/shape_diagnostic.json"
python - <<'PY'
import datetime, hashlib, json, os, platform, sys
from pathlib import Path
out = Path(os.environ['RUN_OUT'])
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()
inputs = [Path('configs/baseline_v1_canonical.yaml'), Path('results/validation_manifest_v5.json'),
          Path('inputs/quijote_fiducial_z1_theory_lattice64.npz'),
          Path('results/disjoint_png_moments_58194794/moments_LC_m_n64_disjoint.npz'),
          Path('results/disjoint_png_moments_58194794/moments_LC_p_n64_disjoint.npz')]
outputs = [out/'calibration.json', out/'shape_diagnostic.json', out/'regression_tests.log']
record = {'schema': 'bphi_normalization_refit_run_v1', 'code_commit': os.environ['CODE_COMMIT'],
          'slurm_job_id': os.environ['SLURM_JOB_ID'], 'hostname': platform.node(),
          'python': sys.version, 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'resource_environment': {k: os.environ.get(k) for k in
              ['SLURM_JOB_ACCOUNT','SLURM_JOB_QOS','SLURM_JOB_PARTITION','SLURM_CPUS_PER_TASK',
               'SLURM_MEM_PER_NODE','SLURM_MEM_PER_CPU','SLURM_JOB_NODELIST']},
          'input_sha256': {str(p): digest(p) for p in inputs},
          'output_sha256': {str(p): digest(p) for p in outputs},
          'source_sha256': {str(p.relative_to(out/'code')): digest(p) for p in (out/'code/src').glob('*.py')},
          'calculation_finished': True, 'slurm_terminal_state': 'VERIFY_WITH_SACCT',
          'production_promotion': False}
(out/'run_provenance.json').write_text(json.dumps(record, indent=2)+'\n')
PY
