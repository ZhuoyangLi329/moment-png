# Stage 7 connected μ2 gate v4

The Stage 7 gate now separates the validated Gaussian and iid-Poisson baselines from the connected halo terms. The Gaussian full-lattice identity passes with per-realization residual below (7\times10^{-17}), and the exact CIC Poisson contact control has RMS pulls 1.036, 1.151 and 0.970 for Ngrid 64, 128 and 256.

The connected halo terms remain `BLOCKED`: no independent curves are available for (b_1), (b_2), (b_{K^2}), (b_\phi), or (b_{\phi\delta}); the primordial collapsed projection fails the N-body normalization audit; and the clustered/repeated-index residual has no three-shell resolution-stable interval. The PNG response is retained as a held-out diagnostic and is not fit by an empirical polynomial.

Every component is required to carry its own theory curve, N-body comparison, uncertainty and scope before promotion. The gate remains `BLOCKED` and does not alter the frozen v1 configuration.
