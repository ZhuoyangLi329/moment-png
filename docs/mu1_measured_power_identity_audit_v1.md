# Stage 3 measured-power μ1 identity audit

For each node, the held-out mean halo power spectrum P_h(k) from realizations 070--099 was projected through the exact Ngrid=64 shell window to predict μ1. This removes the external Pm/M and bias input layer while keeping the estimator, zero-mode, volume, and CIC mesh conventions fixed. The output is `results/mu1_from_measured_ph_validation_v1.json`.

The covariance-aware chi2/dof values are 10.45/14 (fiducial), 7.10/14 (LC_m), and 13.63/14 (LC_p), with RMS pulls 2.32, 0.92, and 4.06. This is a large improvement over the universal-bphi tree prediction, so external Pm/bias normalization is a major part of the original μ1 discrepancy; LC_p residuals and the full PNG response remain unresolved.

This is an estimator consistency diagnostic, not an independent bias calibration or production mean model.
