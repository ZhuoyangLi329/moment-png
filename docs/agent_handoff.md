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

Login connection to host x3113c0s3b0n0:

# Agent handoff: PNG Quijote mu1/mu2 project

This document is the handoff point for the next agent. It is intentionally
conservative: a file existing or a smoke test passing does not mean that the
pure-analytic scientific gate has passed.

## 1. User objective and scientific standard

The project lives on NERSC at:

```text
/pscratch/sd/l/lzy/byd2pcf
```

The requested end state is a publishable PNG Quijote pipeline for the first
two ConKer-style shell moments, including catalog/pair organization,
Gamma/mu1/mu2 measurement, Ngrid/shell-width/scale convergence, shot-noise
controls, Gaussian and halo-Gaussian mu2 theory, a halo-power/local-PNG bias
mu1 model, connected four-point/trispectrum residuals, paired PNG response,
covariance, and a validated joint mu1+mu2 fNL likelihood/MCMC prototype.

The user subsequently clarified a hard requirement: the final model must be
**pure analytic**. A template whose A/k^2, amplitude, or polynomial
coefficients are fit from the same LC+/LC- response being explained is not an
acceptable final theory model. Such fits may remain as diagnostic baselines.

The current project is therefore an operational measurement and theory
scaffold, not a completed publication-grade pure-analytic model. Do not mark
the goal complete while the Stage 5/6 gates below remain open.

## 2. Read these files first, in this order

From the project root, read:

```text
docs/long_term_roadmap.md
docs/stage1_9_execution.md
docs/pure_analytic_equations.md
docs/marisa_b_png_bias_adaptation.md
docs/theory_mu1_mu2.md
docs/publishability_audit.md
docs/quickstart.md
configs/baseline.yaml
configs/bias_inputs_v1.yaml
ref/task.md                         # chronological evidence log
```

The roadmap is the authoritative plan. `ref/task.md` is a detailed running
log, but its older entries include exploratory language; use the latest
entries and the explicit gate documents to resolve conflicts.

## 3. Related upstream/reference projects

The input catalogs are under:

```text
/pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions
```

The MARISA-B reference implementation is under:

```text
/pscratch/sd/l/lzy/marisa-b-portable
```

The broader reconstruction-PNG work is under:

```text
/pscratch/sd/l/lzy/reconstruction-png
```

The MARISA-B material that matters most is:

```text
codes/produce_quijote_halo_marisa_b_bias_v1_png_response_templates.py
codes/produce_quijote_halo_marisa_b_bias_v1_gaussian_templates.py
codes/test_marisa_b_halo_bias_v1_png_1loop.py
notes/marisa_b_halo_bias_v1_fixed_cutoff_one_loop_spec_20260715.md
```

That reference freezes a field-level functional

```text
delta_h = b1 delta + 1/2 b2 delta^2 + bK2 K^2
          + epsilon + epsilon_delta delta
          + fNL (bphi phi + bphidelta phi delta + epsilon_phi phi)
```

and evaluates Gaussian kernels, advected PNG-bias kernels, the quadratic
initial-condition direction K_IC, and one-loop topologies with a fixed
cutoff. Its naming is deliberately `MARISA-B halo bias-v1 truncated
fixed-cutoff one-loop local-PNG response`; it is not a renormalized EFT or a
complete halo-PNG one-loop derivation. Preserve this boundary when adapting
it.

## 4. Catalog and pairing facts

`results/quijote_manifest.json` is the canonical manifest. Current coverage is:

```text
fiducial: 500 realizations, fNL=0
LC_m:    100 realizations, fNL=-100
LC_p:    100 realizations, fNL=+100
common paired IDs: 100 (real000 through real099)
redshift: 1.0
box: 1000 Mpc/h
mass cut: 1e13 Msun/h
positions: Nx3 float32
```

`src/validate_manifest_pairs.py` checks metadata paths, shape/dtype, and LC
ID containment. Its output is `results/manifest_pair_validation.json` and
currently passes with 100 common IDs.

Do not read all position arrays merely to inspect metadata. The pairing and
release audits are intentionally metadata-only and safe on a login node.

## 5. Resource policy

The user explicitly requires routine work on the login node, with no more than
6 cores and conservative memory use. The canonical config contains:

```yaml
slurm_max_cpus: 6
resource_policy:
  login_max_cores: 6
  login_default_threads: 1
  login_memory_conservative: true
  compute_node_only_if: ngrid_or_memory_exceeds_login_limit
```

For login-node commands, set `OMP_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, and `NUMEXPR_NUM_THREADS=1`.
Use a compute node only for a genuinely large Ngrid/memory job and record the
job ID and MaxRSS. Never submit a new large job just to reproduce a small
synthetic test.

## 6. Existing source modules and their scientific scope

Measurement and controls:

```text
src/moments.py                         # CIC + periodic shell convolution
src/batch_moments.py                   # realization batches
src/poisson_control.py                 # matched Poisson control
src/theory_mu2_gaussian.py             # Gaussian-field Wick baseline
src/exact_window.py                    # current discrete mesh/CIC window
src/test_exact_window.py               # independent window/Wick checks
src/validate_manifest_pairs.py         # catalog pairing gate
src/stage_audit.py                     # Stage 1-5 evidence summary
```

PNG bias and two-point scaffolds:

```text
src/marisa_b_kernels.py                # A_n, C_n, K_IC scaffold
src/test_marisa_kernels.py             # permutation/bphi tests
src/marisa_b_power_loop.py             # fixed-cutoff P22/P13 primitives
src/test_power_loop.py                 # loop smoke tests
src/test_p13_directional.py             # FD vs P13 PNG derivative
src/theory_mu1_bphi.py                 # bphi response + uncertainty helper
src/theory_mu1_marisa_b.py             # tree/exact-window mu1 + truncated loop
src/test_mu1_marisa_b.py               # tree algebra test
src/load_bias_inputs.py                # production input gate
src/analytic_input_cov.py              # b1,bphi covariance propagation
```

The implemented `bphi` convention is now the **full PNG bias coefficient**:

```text
Delta b_h / fNL = bphi / M(k)
dP_h/P_h per fNL = 2 bphi / (b1 M(k))
```

For an explicitly selected universal mass-function branch,

```text
bphi = 2 delta_c (b1 - p)
```

where the reconstruction-PNG reference distinguishes tracer `p=1.12` from
reconstruction `p=1.0`. The code exposes this as `--universality-p`; it must
not be silently changed. A previous implementation multiplied the full
coefficient by `(b1-1)` a second time; that was corrected and documented in
`ref/task.md`.

The current loop module has a fixed-cutoff P22 and EdS angle-averaged P13,
plus one-PNG-leg directional derivatives. This is useful infrastructure, but
it is not yet the full MARISA-B halo calculation: b2/bK2 composite kernels,
K3/K4, all topology contractions, counterterms, and a validated physical
window closure are still missing.

The mu2 side is:

```text
src/theory_mu2_marisa_b.py            # Gaussian wrapper + primordial connected interface
src/local_trispectrum.py              # local primordial T_phi and collapsed MC projection
src/test_mu2_marisa_b.py
src/test_mu2_connected_interface.py
```

The connected interface currently projects a local primordial trispectrum and
reports a Monte-Carlo error. It does not yet include the full halo-bias
four-point contraction or discrete contact terms. Treat it as a named partial
layer, not as the final halo trispectrum model.

## 7. Bias-input status and why the production gate is open

`configs/bias_inputs_v1.yaml` records the current independent inputs:

```text
b1 = 2.7340475186190334
b2 = -0.665
bK2 = 0.516666666666667
alpha3 = 0.7885698383313215
alpha4 = -0.30779796761910205
nbar = 1.95530218e-4
```

The Gaussian values came from an isolated fiducial fNL=0 MARISA-B Gaussian
one-loop fit and are recorded with provenance. They were not fit to LC+/LC-
PNG response.

`bphi` and `bphidelta` are intentionally still null. `src/search_bphi.py`
found no qualifying independent numeric values in the MARISA-B analysis tree.
The search also inspected reconstruction-PNG candidates:

* `bphi_universal=3.303097472...` at z=0.5 with only three canary
  realizations had `gate_pass=false` and does not match the current z=1
  selection.
* The z=0.5 bphidelta filter-stability audit had
  `promotion_authorized=false` and failed filter/cutoff gates.

Both are rejected and documented in `results/bphi_calibration_candidates.json`.
The universal mass-function candidate computed from the current frozen b1 is
stored separately in `results/bphi_universal_theory.json` and is marked
`CANDIDATE_UNVALIDATED`, `adopted_in_production=false`.

`src/load_bias_inputs.py --production` must continue to reject the current
config until all required parameters and independent provenance are present.
Do not bypass that rejection by inserting a guessed number.

## 8. Exact-window correction that must not be undone

An earlier `exact_window.py` used averaged continuum sinc functions. That was
not the same estimator as `moments.py`. The current remote version was
replaced with a discrete periodic shell FFT implementation that:

* uses the same `moments.shell_kernel` definition;
* maps only complete periodic FFT lattice modes;
* rejects duplicate, non-lattice, and incomplete mode lists;
* keeps CIC as a power transfer convention;
* subtracts the zero mode;
* optionally subtracts the finite-sample mean variance in centered Wick tests.

The independent nmesh=12 test reports:

```text
mu1 absolute error:              2.17e-18
centered Gaussian Wick error:    2.22e-16
old continuum-window max diff:   8.71e-2
```

This demonstrates why the continuum shortcut cannot silently return as the
default. The primordial connected radial fallback in
`theory_mu2_marisa_b.py` is explicitly labeled continuum; it is not an exact
mesh prediction.

## 9. Current reports and numerical evidence

The main provenance report is `results/pipeline_audit.json`. At the last
verified checkpoint it reported `PASS`, with 40 required artifacts present.
The release audit is `results/release_audit.json`; it checks nine release
files, six PDF figures, zero figure PNGs, and parses the <=6-core resource
policy.

The scientific stage report is different:

```text
results/stage1_5_audit.json: OPEN, 9/10 checks pass
results/stage5_gate.json:    BLOCKED for bphi and bphidelta
```

Stage 1-4 are operational/pass according to `stage_audit.py`. Stage 5 is
partial. Stage 6 is partial. Stage 7 covariance/statistics is operational,
but its mean model is not yet the pure-analytic model. Do not confuse the
provenance audit (file completeness) with scientific completion.

Existing statistical outputs include:

```text
results/connected_n100_w20/paired_response_covariance.json
results/connected_n100_w20/paired_cov_shrinkage_scan.json
results/connected_n100_w20/student_t_likelihood_coverage.json
results/connected_n100_w20/student_t_n50.json ... student_t_n80.json
```

The 100-pair response covariance has 28 features and raw condition number
about `2.50e5`; diagonal-shrinkage scans improve conditioning, but lambda
must be selected on training mocks rather than target response. The
covariance-aware Student-t prototype has better held-out coverage than the
Gaussian prototype, but this does not compensate for an incomplete analytic
mean model.

## 10. Stage tracker interpretation

The current `docs/stage1_9_execution.md` should be read as follows:

* Stage 1: PASS — manifest and pairing validator.
* Stage 2: PASS — measurement engine and realization products.
* Stage 3: PASS as a diagnostic baseline — resolution and Poisson controls
  exist; scale cuts still need a pre-registered release decision.
* Stage 4: PASS for the first Gaussian control — exact-window tests now exist.
* Stage 5: PARTIAL — kernels, tree/exact-window mu1, P22/P13 primitives and
  universal-p option exist; full MARISA-B composite closure, independent
  bphi/bphidelta, and held-out theory validation remain.
* Stage 6: PARTIAL — Gaussian and primordial connected interfaces exist;
  halo-bias four-point and contact contractions remain.
* Stage 7: OPERATIONAL STATISTICS — paired covariance/shrinkage/Student-t
  machinery exists; analytic-input covariance still needs integration into
  the pure model.
* Stage 8: operational release baseline — artifact checks exist, but a
  release is not scientifically publishable until Stages 5 and 6 pass.
* Stage 9: active execution gate.

## 11. Known traps and corrections

1. Do not call an empirical `A/k^2+B+Ck^2` fit an analytic model. It is a
   validation baseline only.
2. Do not use the z=0.5, n=3 canary bphi or failed bphidelta filter result as
   z=1 independent calibration.
3. Do not double-count the universal relation in bphi. Decide whether the
   input is the full coefficient or a dimensionless response amplitude; the
   current project uses the full coefficient.
4. Do not use `P_shot=1/nbar` as the complete mu2 correction. Repeated-index
   and contact terms need their own derivation/control.
5. Do not compare a finite hard-cutoff routing with a shifted routing as if
   the integration domain were translation invariant. Record routing and
   cutoff metadata.
6. Do not infer scientific success from `pipeline_audit.json` being PASS.
7. Keep all PDF figures PDF-only unless the user explicitly asks for PNG.
8. Keep routine commands at one thread on login nodes. Check `squeue` before
   submitting anything; existing account jobs may belong to unrelated work.

## 12. Recommended next actions

The next agent should work in this order, with a low-cost test after each
step:

1. Verify the remote `exact_window.py`, `test_exact_window.py`, and all API
   call signatures. Run the independent nmesh=12 test before changing it.
2. Implement a clean, general halo `K2` interface with the MARISA-B
   convention `K2=b1 F2+b2/2+bK2 S2`, and a fixed-cutoff halo P22
   contraction. Add an independent finite-difference derivative test.
3. Implement the missing Gaussian P13/P13-directional and K3/K4 bias pieces
   in a separately named module, carrying qmin/qmax/routing metadata.
4. Build a true two-point forward model that consumes the frozen bias-input
   file and exact discrete window. It must fail closed when bphi or
   bphidelta is unset unless the user explicitly selects a declared analytic
   assumption such as universal mass-function p.
5. Derive the halo connected four-point from the same field-level functional,
   separating primordial tau_NL/g_NL pieces, bias insertions, and every
   discrete contact contraction. Validate normalization on Gaussian and
   Poisson synthetic fields.
6. Propagate analytic-input covariance into the paired covariance/Student-t
   likelihood only after the analytic mean model is frozen.
7. Re-run the Stage 5/6 gate reports and update the tracker. Never promote a
   partial stage merely because a new smoke test passes.

## 13. Safe command sequence for a handoff check

Run this from a login node; all commands are small and metadata-focused:

```bash
cd /pscratch/sd/l/lzy/byd2pcf
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
python src/test_exact_window.py
python src/test_kernel_zero_mode.py
python src/test_marisa_kernels.py
python src/test_power_loop.py
python src/test_p13_directional.py
python src/test_mu1_marisa_b.py
python src/test_mu2_marisa_b.py
python src/test_mu2_connected_interface.py
python src/stage_audit.py --output results/stage1_5_audit.json
python src/release_audit.py --output results/release_audit.json
python src/audit_pipeline.py --output results/pipeline_audit.json
python -m py_compile src/*.py
```

Expected interpretation: the small tests should pass; Stage 1-5 remains
OPEN because the production bphi gate is intentionally blocked; release and
provenance audits should pass if no artifact is missing.

## 14. Local-versus-remote state at the last handoff

The actual scientific project is on NERSC at the path above. The Windows
workspace used to reach it is only an SSH helper workspace and is not a git
checkout of the NERSC project.

At the last interrupted turn, a local-only patch was prepared in
`work/marisa_b_power_loop.py` to add a general halo P22 kernel and its
directional derivative. It had **not** been uploaded to the remote project.
Before using it, inspect and test it locally, then deliberately upload it if
it passes review. Do not assume its presence on NERSC.

The last remote changes that were verified were the exact-window correction,
the bphi full-coefficient normalization correction, the universal-p option,
paired covariance diagnostics, release/resource audits, and the Stage 5/6
partial gate documentation.

## 15. Definition of done for this goal

Do not call `update_goal complete` until current evidence proves all of the
following:

* catalog manifest and paired IDs are complete and reproducible;
* measurement normalization and exact discrete window agree with independent
  real-space checks;
* Ngrid, shell-width, scale, CIC, cutoff, and shot-noise choices are frozen
  before PNG validation;
* the pure analytic mu1 model includes the declared MARISA-B bias functional,
  independent bias inputs, exact window, and validated fixed-cutoff loop
  closure;
* the pure analytic mu2 model includes Gaussian, halo-bias connected
  four-point, primordial trispectrum, and discrete contact terms;
* all bias parameters and their covariance have independent provenance;
* paired response and covariance are propagated into a likelihood whose mean
  is the analytic model rather than a response fit;
* Gaussian, Poisson, permutation, zero-mode, scaling, finite-difference,
  cutoff, and held-out validation tests pass;
* the documentation, PDFs, configs, SLURM recipes, checksums, and audit
  reports allow another researcher to reproduce the result.

The present state does not satisfy these conditions yet. Continue from the
open Stage 5/6 gates with the user’s <=6-core login-node policy.

## 16. Recent continuation checkpoint (2026-09-07)

Added and verified:

* src/halo_kernels.py: explicit halo K2=b1 F2+b2/2+bK2 S2, fixed-cutoff halo P22, Gaussian b1^2 P13, and one-PNG-leg directional derivative.
* src/theory_mu1_marisa_b.py: predict_with_halo_p22 intermediate two-point projection using the exact discrete mesh window.
* src/marisa_b_higher_kernels.py: fail-closed K3/K4 permutation-symmetrization interface requiring an explicit field-level callback.
* src/discrete_contact_terms.py: iid-Poisson contact correction K(0)^2/lambda^3 beyond Gaussian Wick.
* src/test_halo_kernels.py, src/test_higher_kernels.py, and src/test_discrete_contact_terms.py regression tests.
* src/poisson_control.py now records lambda_cell, kernel_zero, and nalytic_contact arrays in its NPZ output.

The halo P22/P13 directional finite-difference checks are at approximately 1e-12 relative error; the iid-Poisson contact formula agrees with a 300-realization Monte Carlo control at 0.52 sigma. These are validated intermediate layers only. Full MARISA-B K3/K4 physics, halo connected four-point contractions, independent bphi/bphidelta, and final analytic likelihood gates remain open.

The higher-kernel module now also exposes halo_bias_components through n=4, porting the MARISA-B C++ D_n/T_n partition formulas for delta2 and tidal2. For n>2 it requires an explicit matter F3/F4 callback and remains fail-closed; an n=3 permutation regression passes.

Added src/analytic_bias_covariance.py with PSD covariance validation and finite-difference delta-method propagation for frozen bias inputs. The universal bphi transform is exposed as an analytic assumption helper only; it is not promoted to the production config and does not unblock Stage 5.

Added src/analytic_bias_covariance.py and src/test_analytic_bias_covariance.py. The module validates symmetric PSD covariance matrices and propagates frozen inputs through declared transforms with a finite-difference delta method. The universal bphi transform remains an assumption helper only.

Generated esults/intermediate_regression_report.json, a single report for the new halo K2/P22/P13, higher-kernel, Poisson contact, and analytic covariance tests. All four pass under the documented single-thread login-node environment.

The higher-kernel module now includes the standard EdS F3 recursion (ds_F3 and ds_matter_kernel). Its permutation spread is below 6e-17 in the regression; F4 remains callback-only pending an independent implementation and audit.

The higher-kernel module now has a provisional standard EdS F4 recursion (with G3 support) and ds_matter_kernel supports n<=4. Random permutation spread is ~2e-16. This remains an intermediate SPT implementation pending pointwise comparison against the MARISA-B native reference and fixed-cutoff loop integration.

Native-reference audit: marisa-b-portable/codes/marisa_b/marisa_b_native.cpp contains the authoritative K3/K4 and loop formulas, but no ready-to-run native binary or build system was found within the first three directory levels. Pointwise F4 comparison therefore remains pending a controlled dependency/build setup; do not promote the Python EdS F4 implementation until that comparison is done.

Critical F4 audit: a minimal native driver was compiled from marisa_b_native.cpp and called F4edsb on the same explicit 3D vectors used by the Python provisional ds_F4. The values disagree strongly (Python 0.9326084 vs native 0.0196385; relative difference ~46.5). Therefore the Python F4 recursion is not production-ready and must remain provisional until its normalization/input convention is reconciled with the native implementation. Evidence is in esults/f4_native_comparison.json.

Follow-up correction to the F4 audit: the large discrepancy was a convention mismatch because the generic EdS recursion was compared to the native q,-q-specific F4edsb routing. A dedicated src/marisa_b_native_kernels.py adapter now mirrors the native scalar formulas, including x34=-0.9999561; its two pointwise values match native drivers to <1e-12. The generic ds_F4 remains provisional, while the dedicated native adapter is the audited reference for the fixed routing.

Added src/halo_connected_fourpoint.py and a connected_halo_components_mu2 wrapper in 	heory_mu2_marisa_b.py. The explicit collapsed projection separates primordial, halo-bias, and contact callbacks and returns MC errors and scope metadata. A linear primordial tracer test verifies b1^4 scaling. This is an interface/partial layer: clustered halo-bias contractions and the complete contact derivation remain open.

The stage audit now includes native F4 adapter and halo connected-fourpoint regression artifacts. Latest stage result is 14/15 checks PASS with only the intentional stage5 production gate OPEN; pipeline provenance remains 41/41 PASS.

Added src/halo_p13.py with a fixed-cutoff collapsed halo P13 integrator requiring an explicit K3(k,q,-q) callback. The normalization was checked with an odd-angular callback (relative error 1.3e-16), so no singular K3 limit is silently assumed. Stage audit now has 16 checks: 15 pass and only the intentional production gate remains OPEN.

Strengthened stage_audit.py: it now validates that every entry in intermediate_regression_report.json has status PASS, rather than checking only test-file existence. Latest stage result is 16/17 PASS with only the intentional production gate OPEN.

marisa_b_higher_kernels.py now exposes 
ative_matter_kernel for n<=3, converting vector inputs into the native scalar F2/F3edsb convention. The native adapter regression now also exercises this vector path. Stage audit has 17 checks (16 pass; production gate remains OPEN) and all seven intermediate regression tests pass.

Added src/halo_two_point.py and 	est_halo_two_point.py: a unified exact-window mu1 forward model combining tree halo power, explicit K2 P22, Gaussian b1^2 P13, and the one-PNG-leg loop response with cutoff metadata. The Ngrid=8 complete-FFT smoke test passes. Stage audit now has 18 checks (17 pass; only the intentional production gate OPEN), and the intermediate report contains eight PASS tests.

halo_p13.py now has halo_P13_bias_collapsed, evaluating the MARISA-B collapsed D3/T3 partitions for b2 and bK2 while using the audited matter P13 primitive. halo_two_point.py uses this composite P13 by default. The b1-only reduction to b1^2 P13 is exact in the low-order quadrature regression; a nonzero bias-component smoke test passes. The unified exact-window mu1 smoke test still passes. Stage audit is 17/18 PASS (only the intentional production gate OPEN) and pipeline audit remains 41/41 PASS.

The unified two-point model now uses the composite halo_P13_bias_collapsed (matter b1^2 P13 plus direct D3/T3 b2,bK2 terms). Its b1-only reduction is exact in the regression and the b2 derivative is finite; metadata explicitly limits the PNG loop response to internal P(k) one-leg insertion, excluding PNG kernel-bias insertions pending a full derivation.

configs/baseline.yaml now explicitly records estimator conventions (CIC count overdensity, periodic top-hat shell, zero-mode subtraction, mesh power convention, random normalization, real-space boundary), shot-noise policy, and the provisional scale-cut status. Final release cuts remain pending independent resolution/shot-noise review.
