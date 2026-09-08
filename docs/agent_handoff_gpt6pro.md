# Agent handoff for GPT-6 Pro

## Repository and scientific context

This repository develops a ConKer-style density-moment analysis for the Quijote local-PNG halo simulations. The observable is built from a halo overdensity field and a periodic spherical-shell convolution. For each shell radius s, eta_s(x) = delta_h(x) [K_s * delta_h](x). The normalized field Gamma is the ConKer random-normalized pair estimator. The primary observables are the first moment mu1(s) and second moment mu2(s); mu3 is deferred.

The native validation sample is Quijote PNG at z=1, snapshot 002, periodic box L=1000 Mpc/h, FoF halos with M_h >= 1e13 Msun/h. Position products live on NERSC under /pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions. Current native nodes are fiducial fNL=0, LC_m=-100, and LC_p=+100. Products currently contain 500 fiducial and 100 each for LC_m and LC_p, with 100 common paired realization IDs.

## Core goal

The final goal is a publishable pure-analytic prediction of mu1 and mu2 from independently specified cosmology, transfer function, halo-bias parameters, shot-noise/contact terms, and the exact measurement window. Coefficients fitted to the same PNG response being explained are forbidden in the final model.

The motivating paper used empirical quadratic response fits in fNL on FastPM simulations. Those fits remain diagnostics only.

## Planned method

1. Freeze data conventions: redshift, mass cut, box, real/RSD choice, CIC convention, shell width, grid, zero mode, random normalization, and scale cuts.
2. Measure realization-level Gamma, mu1, and mu2 with CIC plus periodic FFT shell convolution.
3. Validate the Fourier window identity and Gaussian Wick baseline mu2_G = sigma0^2 sigma_s^2 + xi_s^2 using independent Gaussian fields.
4. Quantify resolution, shell-width, CIC, finite-volume, and Poisson/contact effects with Ngrid=64,128,256 and matched Poisson controls.
5. Build pure-analytic mu1 from P_h(k;fNL) = [b1 + fNL bphi/M(k)]^2 P_m(k) + shot noise with exact discrete mesh projection and fixed-cutoff halo loop corrections.
6. Build mu2 from Gaussian, primordial trispectrum, halo-bias connected four-point, and discrete contact contractions.
7. Freeze analytic inputs before PNG validation, then evaluate held-out coverage and covariance-aware likelihoods.

## Current implementation and evidence

Operational and tested layers include:

- src/moments.py: CIC and periodic shell moment measurement.
- src/exact_window.py: exact discrete mesh/window projection with zero-mode handling.
- src/theory_mu2_gaussian.py: Gaussian Wick prediction.
- src/halo_kernels.py, src/halo_p13.py, src/halo_two_point.py: intermediate halo K2/P22/P13 layers.
- src/theory_mu1_bphi.py: independent-parameter PNG-bias interface and universal-mass-function helper.
- src/validate_mu1_analytic_holdout.py: held-out comparison against a frozen prediction; it never fits the PNG response.
- Gaussian, Poisson, permutation, finite-difference, covariance, and exact-window tests.
- configs/baseline_v1_frozen.yaml: frozen diagnostic measurement configuration.
- slurm/run_mu1_composite_n32.sbatch: compute-node recipe for the composite smoke test.

External z=1 theory input has been copied with provenance to inputs/ from the MARISA-B table containing k, P_L, P_phi, and M(k,z=1). The explicit universal tracer branch p=1.12 gives bphi=5.4425682328; reconstruction p=1.0 gives 5.8472082328. These are assumptions only and are not adopted in production config.

Held-out evidence on 100 paired products:

- The held-out workflow runs successfully.
- Tree-level universal-bphi predictions show large RMS pulls, roughly 5--9 even at fNL=0 and much larger pulls at fNL=+100.
- A Ngrid=32 composite P22/P13 smoke job completed successfully (Slurm job 58071293, ExitCode 0:0) but did not improve held-out agreement; RMS pulls were 14.79, 21.01, and 11.20 for fiducial, LC_m, and LC_p.

## Open gates and review priorities

Stage 5 pure-analytic mu1 and Stage 6 pure-analytic mu2 remain open. Unresolved items are independent bphi and bphidelta calibration for the z=1 sample, audited z=1 P_m/M(k) and CIC normalization, exact-window consistency at production grid, complete MARISA-B K3/K4 and PNG-kernel-bias loop closure, halo connected four-point/contact terms for mu2, and analytic-input covariance in the final likelihood.

Do not promote universal-mass-function assumptions, empirical A/k^2 templates, or low-resolution composite smoke results to production claims. The correct current description is a reproducible measurement plus semi-analytic validation scaffold with quantified open scientific gates.

## Suggested first review actions

1. Check source modules and tests against docs/task.md.
2. Verify production predictions fail closed when bphi or bphidelta is unset.
3. Audit the external z=1 theory table and interpolation onto periodic mesh modes.
4. Compare tree-only and composite predictions on the same grid and exact window.
5. Decide whether to prioritize independent bias calibration, two-point loop closure, or the connected mu2 derivation.


## Latest validation checkpoint (2026-09-09)

The v1 protocol is frozen in configs/validation_v1.yaml and the NERSC validation manifest. A unified Ngrid=64 N-body baseline package now joins P_h(k), mu1, mu2, Gaussian mu2 baseline, R_mu2, mode counts, and realization IDs for fiducial, LC_m, and LC_p.

A first tree halo-power versus N-body mesh-spectrum comparison with the p=1.12 universal branch is stored in results/ph_nbody_tree_comparison_v1.json. Its low-k (k<=0.03) RMS pulls are 6.78, 11.00, and 3.66 for fiducial, LC_m, and LC_p. Removing the CIC transfer changes these to 5.22, 9.72, and 2.17, showing CIC convention matters but does not explain the full mismatch.

The comparison is diagnostic only. The model still lacks complete MARISA-B PNG halo-tree terms, fully audited P_m/M normalization at the mesh level, and complete shot-noise/contact closure. Do not tune bphi on these validation nodes.
