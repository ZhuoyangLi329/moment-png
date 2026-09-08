# N-body mu2 decomposition baseline

results/mu2_nbody_decomposition_v1.json packages the 100-realization Ngrid=64 connected products for fiducial, LC_m, and LC_p. For each shell it reports means and standard errors for raw mu2, Gaussian Wick mu2_G, Gaussian-subtracted connected residual, and R_mu2=mu2/mu2_G.

At s=40 the means are: fiducial mu2=0.09177, mu2_G=0.08545, connected=0.00632, R_mu2=1.07365; LC_m mu2=0.08334, mu2_G=0.07875, connected=0.00459, R_mu2=1.05807; LC_p mu2=0.10109, mu2_G=0.09277, connected=0.00832, R_mu2=1.08923. At larger shells the connected residual is much smaller.

This is a measurement decomposition, not a complete analytic trispectrum validation. The next step is to compare analytic Gaussian, primordial, halo-bias, and contact contributions to these arrays with identical windows and normalization.
