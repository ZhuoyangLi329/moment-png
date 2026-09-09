# Canonical protocol consistency audit

`src/check_protocol_consistency.py` validates the canonical v1 configuration and immutable manifest together. It checks the actual configuration SHA256, manifest SHA256/path, frozen z=1/L=1000/FoF mass selection, real-space CIC estimator, 20 Mpc/h periodic shells, the exact 40--300 scale list, Ngrid 64/128/256 roles, zero-mode subtraction, node labels, and the 70/30 realization split.

The NERSC audit returns `PASS` for all 18 checks. New comparisons must use `configs/baseline_v1_canonical.yaml` and `results/validation_manifest_v5.json`; the older config and manifest are retained only for historical provenance.
