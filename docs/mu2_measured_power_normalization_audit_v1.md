# Stage 2/7 measured-power normalization audit

The external lattice Pm input was compared with the N-body mean halo power using the same 0.005 h/Mpc bins. The first measured-to-external ratio is 8.08, close to the baseline b1 squared, so the power normalization is broadly consistent at the largest modes but still carries scale dependence and shot/nonlinear contributions.

To isolate that uncertainty, the exact discrete Gaussian μ2 Wick projection was recomputed using the measured mean P_h(k) instead of external Pm. The resulting covariance-aware chi2/dof is 19.17/14 (fiducial), 13.90/14 (LC_m), and 21.70/14 (LC_p), with RMS pulls 9.07, 4.43, and 11.03. This is a substantial improvement over the external-Pm branch but still fails the held-out Gaussian-component comparison.

Outputs are `results/ph_pm_normalization_audit_v1.json` and `results/mu2_gaussian_from_measured_ph_validation_v1.json`. The remaining discrepancy is therefore not solely an overall external Pm amplitude error; finite-mesh aliasing, realization covariance, and contact/estimator terms remain relevant.
