# Exact mode-power to μ1 identity audit (v2)

This batch audit uses the same discrete lattice modes used by the CIC halo measurement. For each held-out realization (`real070`--`real099`) and each node (`fiducial`, `LC_m`, `LC_p`), it forms the shell-window projection

\[
\mu_1(s)=L^{-3}\sum_{\mathbf k}P_h(\mathbf k)W_s(\mathbf k)
\]

from that realization's mode power and compares it with the stored direct μ1 estimator at `s=40`--`300` Mpc/h in steps of 20 Mpc/h. The zero mode is excluded and the exact lattice shell window is shared by prediction and measurement. This is an estimator-consistency check; it does not calibrate `b1`, `bφ`, or fit a PNG response.

The approved batch mode-power job `58087691` ran on NERSC and produced 30 realizations per node. The v2 validator separates the numerical identity residual from uncertainty in the mean residual. The per-realization RMS residuals are `2.07e-16`, `2.14e-16`, and `2.51e-16` for fiducial, LC_m, and LC_p. Mean RMS pulls are `1.21`, `0.95`, and `1.18`; covariance-aware χ²/dof values are `2.69`, `2.10`, and `1.46`, with 0.93, 1.00, and 0.93 of shell means within |pull|≤2. Maximum absolute mean residual is below `2.7e-16`.

The machine-readable result is `results/mu1_modewise_power_identity_v2.json`. The identity passes at floating-point precision, so remaining μ1 discrepancies in theory comparisons cannot be attributed to a mismatch between the stored direct estimator and the measured mode-power projection. The audit does not close the analytic mean-model or independent-bias gates.
