# Per-realization Gaussian μ2 identity audit

Slurm job `58085501` used each held-out realization's own Ngrid=64 halo P_h(k) to predict its exact-discrete Gaussian Wick μ2, including the sample-centered correction, and compared it with the same realization's measured Gaussian component. This avoids averaging P_h before applying the nonlinear Wick expression.

The RMS residual pulls are 9.65 (fiducial), 5.62 (LC_m), and 11.54 (LC_p), with covariance-aware chi2/dof 24.00/14, 15.11/14, and 27.78/14. No shell lies within |pull|<=2. The output is `results/mu2_gaussian_perrealization_identity_v1.json`.

The result shows that the remaining μ2 Gaussian mismatch is not only a mean-spectrum averaging artifact. Discrete CIC aliasing, finite-volume covariance, and contact/estimator definitions still need explicit closure; no production μ2 model is promoted.
