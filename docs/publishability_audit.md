***************************************************************************
                          NOTICE TO USERS

Lawrence Berkeley National Laboratory operates this computer system under 
contract to the U.S. Department of Energy.  This computer system is the 
property of the United States Government and is for authorized use only.
Users (authorized or unauthorized) have no explicit or implicit 
expectation of privacy.

Any or all uses of this system and all files on this system may be
intercepted, monitored, recorded, copied, audited, inspected, and disclosed
to authorized site, Department of Energy, and law enforcement personnel,
as well as authorized officials of other agencies, both domestic and foreign.
By using this system, the user consents to such interception, monitoring,
recording, copying, auditing, inspection, and disclosure at the discretion
of authorized site or Department of Energy personnel.

Unauthorized or improper use of this system may result in administrative
disciplinary action and civil and criminal penalties. By continuing to use
this system you indicate your awareness of and consent to these terms and
conditions of use. LOG OFF IMMEDIATELY if you do not agree to the conditions
stated in this warning.

*****************************************************************************

Login connection to host x3115c0s7b0n0:

# Publishability audit: Quijote local-PNG mu1/mu2

This file maps the requested deliverables to current, reproducible evidence. Paths are relative to the project root `/pscratch/sd/l/lzy/byd2pcf`.

| Requirement | Evidence | Current interpretation / remaining limitation |
|---|---|---|
| Catalog and paired-realization organization | `src/make_quijote_manifest.py`, `results/quijote_manifest.json`, `docs/upstream_and_data.md` | Manifest records node, realization, shape, box, redshift, and halo count. Fiducial/LC± pairing is explicit; source catalogs remain immutable. |
| ConKer-style Γ, μ1, μ2 measurements | `src/moments.py`, `src/batch_moments.py`, `results/resolution_clean/` | Γ/shell moments and batch outputs are reproducible. The connected μ2 estimator is accompanied by Gaussian and Poisson controls. |
| Ngrid/shell-width/scale convergence | `src/plot_normalized_mu2_resolution.py`, `results/figures/normalized_mu2_resolution.pdf`, `results/resolution_clean/` | Raw connected μ2 is grid-sensitive; normalized `R_mu2=μ2/μ2_G` is the resolution-matched statistic. Width and scale sweeps are retained in the connected-response products. |
| Shot-noise diagnosis | `src/poisson_control.py`, `docs/theory_mu1_mu2.md` | Matched uniform-Poisson controls isolate contact terms; residual is near zero at the quoted scales. |
| Gaussian random-field μ2 theory | `src/theory_mu2_gaussian.py`, `docs/theory_mu1_mu2.md` | Implements and validates `μ2,G=σ0²σs²+ξs²` against independent Gaussian fields. |
| Halo-Gaussian μ2 theory | `src/theory_mu2_gaussian.py`, `src/connected_residual.py` | Halo-field Gaussian baseline is computed from measured spectra and compared with connected residual; discrete contact terms are kept separate. |
| Halo-power + local-PNG scale-dependent-bias μ1 model | `src/theory_mu1_power.py`, `src/theory_mu1_modewise.py`, `src/project_real_png_mu1.py` | Real-space `P_h` response and `k^-2` fit provide a semi-analytic, empirically calibrated template. Current projected template has poor χ², so finite-window/nonlinear-bias corrections remain required before claiming a precision model. |
| Connected four-point/trispectrum μ2 residual | `src/local_trispectrum.py`, `src/fit_mu2_response_quadratic.py`, `results/connected_n100_w20/quadratic_response.json` | Local-PNG trispectrum scaffold and empirical `A fNL²+B fNL+C` response target are present. First-principles halo-bias closure and calibrated projection are still open. |
| Covariance and paired PNG response | `src/covariance_diagnostics.py`, `src/normalized_mu2_response.py`, `results/connected_n100_w20/normalized_quadratic_response.json` | Paired odd/even response and covariance diagnostics are operational; finite-sample shrinkage is documented. |
| μ1+μ2 fNL likelihood/MCMC prototype | `src/mcmc_grid_likelihood.py`, `src/mcmc_quadratic_likelihood.py`, coverage JSON and PDF | Grid and quadratic posterior prototypes run end-to-end. Coverage is diagnostic (not yet publication-grade), motivating larger ensembles and a non-Gaussian likelihood. |
| Reproducibility and figures | `configs/baseline.yaml`, `slurm/*.sbatch`, `results/figures/*.pdf`, `docs/long_term_roadmap.md` | Canonical config, safe 8-CPU SLURM recipes, PDF-only figures, and compile checks are present. |

## Verification commands

```bash
cd /pscratch/sd/l/lzy/byd2pcf
python -m py_compile src/*.py
python src/make_quijote_manifest.py --help
python src/fit_mu2_response_quadratic.py --help
ls results/figures/*.pdf
```

The audit intentionally distinguishes operational evidence from unresolved scientific limitations; it is not a claim that the open model-calibration items are complete.

## Terminology correction

The halo-power PNG construction is deliberately called a **semi-analytic, empirically calibrated template**. The shell projection and the k-dependent functional form are analytic, but its amplitudes and finite-k correction are fitted to Quijote. A first-principles analytic model still requires an independent prediction for b_phi and a validated nonlinear/window closure.

## First-principles bias interface

`src/theory_mu1_bphi.py` now provides the independent-parameter theory interface: given matter P(k), transfer M(k), b1, and independently calibrated b_phi, it evaluates Delta b/fNL = 2 delta_c (b1-1)b_phi/M(k), dP_h/P_h, and the shell projection. This is the route to replace the empirical A coefficient; no Quijote response is used internally to set b_phi.
