# μ1/μ₂ training best-fit overlay figure (statistics v2)

The one-page PDF `mu1_mu2_training_bestfit_vs_measured_symlog.pdf` overlays all three node curves on common axes. The upper panel is μ1; the lower panel is the Gaussian μ₂ component. Curves use the mean `P_h(k)` from 70 training realizations (`real000`--`real069`) projected through the exact Ngrid=64 periodic shell window. Colored points are the means of 30 held-out realizations (`real070`--`real099`).

Each errorbar is the realization-level standard deviation `sigma_real` across those 30 held-out vectors, not the standard error of the mean. For the covariance-aware mean comparison, the validator separately forms `C_mean = C_realization / 30`; the plotted scatter and the covariance used for chi-square therefore represent different statistical quantities. The lower μ₂,G panel uses a sign-preserving symlog axis with display minimum `1e-3`.

This is a leakage-free diagnostic, not a production analytic mean: μ₂ contact, clustered halo, and primordial four-point terms are omitted.
