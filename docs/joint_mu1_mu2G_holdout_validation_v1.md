# Stage 8 joint held-out diagnostic

A 28-dimensional joint vector `[mu1(s), mu2_G(s)]` was evaluated on the frozen held-out realizations real070--real099 for all three nodes. The μ1 prediction uses the exact discrete mesh tree model with the declared training Pshot candidate; the μ2 prediction is the corrected finite-Nyquist CIC Gaussian baseline. The output is `results/joint_mu1_mu2G_holdout_validation_v1.json`.

Because there are 30 held-out realizations and 28 observables, the Hartlap factor is undefined (`n <= d+2`) and is recorded as such. The report instead scans diagonal shrinkage λ=0, 0.1, 0.5, 0.9. The minimum reported χ²/dof over this scan is 165.51 (fiducial), 92.33 (LC_m), and 231.88 (LC_p), so shrinkage does not rescue the joint comparison.

This is a held-out diagnostic only. It does not qualify as the final joint μ1+raw-μ2 test because the μ2 model contains only the Gaussian component; Poisson contact, repeated-index, clustered contact, PNG bias, and primordial trispectrum terms remain open.
