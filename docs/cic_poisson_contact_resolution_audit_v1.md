# CIC Poisson contact resolution audit

This audit evaluates the independent Poisson `kappa_22` contact term for the exact CIC assignment used by `src/moments.py`, rather than treating `1/nbar` as a complete four-point correction.

For a point in one mesh cell, the CIC weights to the eight receiving cells are `w_e`; for shell kernel `K_e`, the contact term is

`I_CIC / lambda_cell^3`, with `I_CIC = integral_[0,1]^3 w_0^2 (sum_e K_e w_e)^2 du`.

The frozen shells start at 40 Mpc/h. For Ngrid 64, 128 and 256, their real-space shell support does not overlap the eight CIC receiving cells of the observed cell, so the exact CIC contact is zero at these radii. The measured iid-Poisson connected residual is nevertheless consistent with that prediction: RMS pulls are 1.036 (64), 1.151 (128), and 0.970 (256), with mean absolute pull below 2 for 64/128/256 equal to 1.0, 0.929 and 0.929.

This closes the independent Poisson CIC contact baseline only. The large Ngrid dependence of the halo connected residual therefore remains a clustered/repeated-index/four-point effect and requires explicit halo terms; no production promotion is made.
