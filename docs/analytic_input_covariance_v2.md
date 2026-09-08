# Stage 6 analytic input covariance propagation

`results/analytic_input_covariance_v2.json` propagates the current candidate inputs through the declared universal branch

`b_phi = 2 delta_c (b_1 - p)`.

The input mean is `(b1, delta_c, p) = (2.7813407736, 1.686, 1.12)`. The declared diagonal sensitivity covariance uses standard deviations `(0.00171, 0.001, 0.05)` for `(b1, delta_c, p)`, giving `b_phi=5.6020411 +/- 0.1687313`. The derived covariance between `(b1,b_phi)` is retained in the JSON, together with exact-window finite-difference Jacobians and a full 14-shell μ1 covariance for fNL=0, -100, and +100.

The propagation uses the same Ngrid=64 lattice input, CIC/mesh convention, shell width 20 Mpc/h, and scales 40--300 Mpc/h as the held-out diagnostic. It records uncertainty bands without fitting any PNG response or held-out realization.

This artifact is `ASSUMPTION_ONLY`: the `p` and `delta_c` uncertainties are declared sensitivity assumptions, and no independent calibration matching the current z=1 FoF selection and bias convention has been established. Therefore the result documents the required delta-method propagation but does not unblock the Stage 5 gate or promote `b_phi` to production.
