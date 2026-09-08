# Stage 2 scale-dependent b1 diagnostic

The Ngrid=64 fiducial training product gives a convention-sensitive scale-dependent bias estimate. In the raw mesh ratio, the mean b1 is 2.839 for kmax=0.03, 2.828 for 0.05, 2.790 for 0.08, 2.760 for 0.10, and 2.646 for 0.15 h/Mpc. Applying the isotropic CIC power-transfer correction instead gives 2.860, 2.882, 2.923, 2.967, and 3.108.

The full per-bin values and k-bin scatter are in `results/fiducial_b1_kmax_summary_v1.json`. This is a training-set convention audit, not a PNG-response fit or production bias calibration. The divergent raw and CIC trends show why b1, CIC, shot noise, and kmax must be frozen jointly.
