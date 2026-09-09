# μ1 best-fit diagnostic figure

`mu1_training_bestfit_vs_measured.pdf` compares the leakage-free training-calibrated curve with the held-out N-body mean for all three nodes. The curve uses the mean `P_h(k)` from `real000`--`real069` projected with the exact Ngrid=64 periodic shell window; points are the `real070`--`real099` μ1 mean with standard-error bars.

The figure is a diagnostic visualization, not a production analytic model: the training spectrum contains empirical tracer information, and the held-out points are never used to form the curve. The plotted held-out χ²/dof values are 15.57, 16.83, and 19.00 for fiducial, LC_m, and LC_p.
