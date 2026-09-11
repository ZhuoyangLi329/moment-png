# Corrected independent bphi gate

The immutable Slurm refit `58197556` corrected the coefficient convention.  It reports conditional `b_phi=3.74847567` with statistical sigma `0.01246916` and `c=b1*bphi=10.23983581`.  The template fit remains rejected at `chi2/dof=207.0445`; empirical log-tilt and inverse-squared stress bases still have `chi2/dof=46.97` and `46.18`, so they are diagnostics rather than accepted halo operators.

The corrected Stage 6 audit is `CALIBRATION_SOURCE_AVAILABLE_SHAPE_REJECTED` and the gate remains `NO_PRODUCTION_BPHI`.  The b1 uncertainty and b1--bphi cross-covariance are still unpropagated.
