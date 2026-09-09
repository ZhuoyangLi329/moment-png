# Full-lattice Gaussian mu2 identity v2

The batch audit uses the complete Ngrid=64 Fourier lattice `P_h` for each held-out realization and projects it through the same exact periodic shell window as the stored N-body `mu2_gaussian` field. The stored N-body Gaussian component is the ensemble-centered Wick quantity

`mu2_G = sigma0^2 sigma_s^2 + xi_s^2`.

The validator therefore does not subtract the finite-sample mean correction. That correction belongs to a sample-centered estimator and was the source of the earlier false residual.

Slurm job `58096167` completed on `nid004079` in 31 seconds using 30 held-out realizations per node. The per-realization RMS differences are `8.33e-18` (fiducial), `7.13e-18` (LC_m), and `9.91e-18` (LC_p); maximum absolute differences are below `7e-17`. Mean covariance statistics are χ²/dof `0.994`, `0.794`, and `5.039`, with the latter driven by machine-precision covariance conditioning rather than a visible estimator residual.

This is an estimator identity and Gaussian baseline closure diagnostic. It does not validate the external analytic `P_m/M` input, PNG response, contact terms, or the full halo four-point model, and it does not promote any bias parameter.
