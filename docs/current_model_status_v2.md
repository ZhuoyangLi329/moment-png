# Analytic model status v2: CIC convention improvement

A training-only convention scan now tests the frozen exact Ngrid=64 window against held-out μ1 without using the held-out response to fit parameters. The fiducial training mean `P_h(k)` is fit at `k<=0.08 h/Mpc` with `b1` and `P_shot`, and the same convention is applied to fiducial, LC_m, and LC_p held-out predictions.

For a CIC-assigned count field, the mesh assignment is Cloud-in-Cell: the field amplitude is filtered by `prod_i sinc^2(k_i Delta x/2)`, so the power contribution is filtered by the corresponding `prod_i sinc^4` transfer. The `CIC both` variant applies this transfer to the clustering and Poisson shot terms. It fits `b1=2.7413` and `P_shot=5467.8` from training data, close to the inverse number density scale.

The held-out RMS pulls for `CIC both` are 1.65, 2.86, and 1.97, with covariance-aware χ²/dof 4.07, 16.63, and 8.98. Applying the finite-sample Hartlap factor for 30 realizations and 14 shells gives 1.96, 8.03, and 4.34. This is a substantial improvement over the fixed-constant-b1 universal tree baseline, but LC_m and LC_p remain outside a production acceptance threshold.

The other tested conventions remain diagnostic comparisons: CIC clustering with an unfiltered shot term gives Hartlap χ²/dof 3.44, 3.87, and 13.03, while no CIC gives 4.58, 3.69, and 16.05. The `CIC both` choice is retained as the leading convention candidate because it follows the measured mesh assignment, but it is not promoted to a final analytic mean until independent bias provenance, loop convergence, and PNG response closure are supplied.

The machine-readable evidence is `results/mu1_training_theory_convention_scan_v1.json`; the visual comparison is `results/mu1_training_convention_scan_vs_nbody.pdf`.
