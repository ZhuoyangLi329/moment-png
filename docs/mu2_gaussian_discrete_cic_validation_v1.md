# Stage 7 exact discrete Gaussian μ2 convention audit

The exact lattice projector `mu2_gaussian_discrete` was evaluated with the frozen Ngrid=64 modes and compared with the N-body Gaussian component. A mesh-power input (`P_h=b1^2 P_m+P_shot`) predicts the first shell at 0.2185, while applying the continuum-to-CIC power transfer gives 0.06846 against the N-body fiducial mean 0.08545. The latter is the relevant convention test because the measured field uses CIC assignment.

The covariance-aware validation for the CIC-transfer branch gives chi2/dof 342.71/14 (fiducial), 249.57/14 (LC_m), and 509.50/14 (LC_p), with RMS pulls 36.55, 22.62, and 41.39 and zero shells inside |pull|<=2. The output is `results/mu2_gaussian_discrete_cic_validation_v1.json`.

This is a sharper failure localization than the earlier continuous integral: the unbounded high-k shot-noise bug is removed and the discrete shell window is exact, but the supplied external Pm/M normalization, alias treatment, and halo Gaussian convention still do not close μ2. Contact and connected four-point terms remain separate production blockers.
