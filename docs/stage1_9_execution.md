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

Login connection to host x3114c0s9b0n0:

# Stage 1-9 execution tracker

This tracker follows `docs/long_term_roadmap.md`; empirical fits never enter the pure analytic mean model.

| Stage | Current evidence | Status | Next gate |
|---|---|---|---|
| 1 Data/conventions | `results/quijote_manifest.json`, `results/manifest_pair_validation.json`, `configs/baseline.yaml`, `docs/upstream_and_data.md` | PASS | immutable input checksums remain optional follow-up |
| 2 Measurement engine | `src/moments.py`, `src/batch_moments.py`, realization NPZ products | PASS | metadata schema and repeatability check |
| 3 Convergence/shot noise | `results/resolution_clean/`, `src/poisson_control.py`, resolution PDF | PASS | freeze pre-registered scale/window cuts |
| 4 Gaussian controls | `src/theory_mu2_gaussian.py`, Gaussian validation outputs, `results/stage1_4_audit.json` | PASS | exact discrete mesh window is now implemented |
| 5 Pure analytic mu1 | `src/marisa_b_kernels.py`, `src/theory_mu1_marisa_b.py`, `src/exact_window.py`, `src/marisa_b_power_loop.py`, `src/bias_inputs_v1.yaml` | PARTIAL | universal-mass-function bphi branch is runnable but unvalidated; full b2/bK2 composite closure and held-out M(k),Pm(k) test remain |
| 6 Pure analytic mu2 | `src/theory_mu2_gaussian.py`, `src/local_trispectrum.py`, `src/theory_mu2_marisa_b.py`, connected interface test | PARTIAL | connect MARISA-B halo kernels and discrete contact contractions |
| 7 Covariance/paired response | `results/connected_n100_w20/paired_response_covariance.json`, `paired_cov_shrinkage_scan.json`, Student-t coverage JSON | OPERATIONAL STATISTICS | propagate analytic-input covariance into final pure-analytic mean model |
| 8 Robustness/release | PDFs, SLURM recipes, quickstart, provenance audit | operational baseline | regenerate after pure model port |
| 9 Execution gate | this tracker and audit artifacts | active | all prior hard gates must pass before likelihood release |

## Frozen v1 diagnostic configuration

`configs/baseline_v1_frozen.yaml` freezes the first held-out diagnostic configuration: real-space CIC count overdensity, periodic shell width 20 Mpc/h, Ngrid=64 login baseline, and s=40--300 Mpc/h. These cuts are frozen before the held-out comparison, but are not yet the publication release cuts because resolution and clustered shot-noise renormalization remain open.

## Immediate execution order

1. Write and freeze `bias_inputs_v1.yaml` from an independent calibration source.
2. Port MARISA-B kernel recursion and fixed-cutoff one-loop contractions into a two-point module.
3. Implement exact discrete mesh/CIC/shell windows and compare against continuum limits.
4. Port collapsed halo trispectrum and discrete contact terms for mu2.
5. Run invariant, cutoff, permutation, Gaussian, Poisson, and held-out response tests.
6. Update covariance and paired-response products using the frozen analytic mean model.

A stage is marked complete only when its listed artifact, test output, and documented limitation are all present.
