# Roadmap: pure analytic PNG Quijote mu1/mu2 pipeline

The target is a pure analytic prediction for mu1 and mu2 from independently specified cosmological, halo-bias, transfer, and window inputs. Empirical Quijote response fits remain validation diagnostics only.

## Current status

Operational layers include native catalog manifests, CIC and periodic shell moments, exact discrete window tests, Gaussian and Poisson controls, covariance diagnostics, held-out validation machinery, and PDF-only release audits.

The pure analytic WP5/WP6 gates remain open: independent b_phi and b_phi-delta calibration matched to the z=1 halo sample, complete halo-bias loop/trispectrum closure, and final CIC/mesh/shot-noise consistency are still required.

## Work packages

1. Data and conventions, including immutable manifests and pairing.
2. Measurement engine with explicit CIC, shell, grid, and normalization metadata.
3. Resolution and shot-noise convergence before PNG validation.
4. Gaussian and Poisson controls.
5. Pure analytic halo-power mu1 model with exact discrete window.
6. Pure analytic connected halo four-point mu2 model.
7. Covariance and held-out likelihood coverage.
8. Reproducibility package with configs, SLURM recipes, checksums, and PDF figures.

Until WP5 and WP6 pass, describe this repository as a measurement plus semi-analytic validation study.
