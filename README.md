# PNG Quijote density-moment model

This repository contains the measurement engine and semi-analytic theory scaffold for ConKer-style shell moments of Quijote local-PNG halos. The primary observables are the first two moments, mu1(s) and mu2(s), at z=1 for FoF halos with M_h >= 1e13 Msun/h.

## Current status

The reproducible measurement, Gaussian/Poisson controls, exact discrete shell window, paired realization products, covariance diagnostics, and a held-out mu1 validation workflow are operational. The pure-analytic production gates remain open: independent b_phi/b_phi-delta calibration and the complete halo connected four-point closure are still required.

The canonical diagnostic baseline is in configs/baseline_v1_frozen.yaml. Large catalogs and NERSC-generated binary products are intentionally excluded; see inputs/README.md for external provenance.

## Layout

- src/: measurement, theory, diagnostics, and validation scripts
- tests/: regression tests (to be consolidated from src/test_*.py)
- configs/: frozen estimator and bias-input configurations
- docs/: task, methods, roadmap, handoff, and audit notes
- results/: selected lightweight JSON reports and publication PDF figures
- slurm/: reproducible compute-node recipes

All paths to NERSC data are configuration inputs, not bundled data.
