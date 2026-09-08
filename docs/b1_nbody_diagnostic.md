# Fiducial N-body b1 diagnostic

`results/fiducial_b1_nbody_diagnostic_v1.json` derives a training-set diagnostic b1(k) from the 100 fiducial N-body mesh spectra and the external z=1 linear P_m table. It reports both raw sqrt(P_h/P_m) and a CIC-transfer-corrected version.

For k <= 0.03 h/Mpc, the simple mean is b1=2.8385 (raw) and 2.8599 (CIC-corrected), with across-bin scatter 0.0380 and 0.0410. The frozen MARISA-B bias input is b1=2.7340, about 4--5 percent lower.

This is a convention and selection diagnostic, not a license to replace the frozen independent b1 using the same validation products. The discrepancy must be investigated through halo selection, smoothing radius, P_m redshift/growth, mesh/CIC convention, and bias-definition matching. A future b1 calibration may use a predeclared fiducial training subset, but the held-out PNG nodes must remain untouched.


