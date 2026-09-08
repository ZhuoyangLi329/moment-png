# Linear-P(k) b1 candidate

At the user's request, src/fit_b1_linear_pk.py fits a constant b1 and nonnegative constant P_shot to the first 70 fiducial N-body realizations, using Ngrid=64, the CIC mesh transfer, the external z=1 linear P_m table, and kmax=0.08 h/Mpc.

The result is results/fiducial_b1_linear_pk_training_kmax008.json: b1=2.7813407736, linearized sigma=0.00171, P_shot=3603.0, and chi2/dof=1.99 for 13 degrees of freedom. This is a training-set calibration candidate, not an independent external bias input.

Using this candidate with the explicit universal tracer branch p=1.12 gives node-matched held-out mu1 RMS pulls 4.23 (fiducial), 6.36 (LC_m), and 2.52 (LC_p). The covariance-aware chi2/dof values are 215.85, 329.36, and 155.06, so the candidate does not pass the full mu1 validation. It remains useful for separating b1 amplitude from PNG and loop failures, but it is not promoted to the production bias config.


