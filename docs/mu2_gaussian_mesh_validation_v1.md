# Stage 7 Gaussian μ2 analytic baseline

The analytic Gaussian μ2 script now applies an explicit Ngrid=64 Nyquist cutoff (`kmax=pi/(1000/64)=0.20106 h/Mpc`) and an isotropic CIC power transfer when requested. This prevents the previous unbounded integration of a constant shot term to k=80 h/Mpc, which produced a spurious sigma0 squared of order 3e7.

With the corrected mesh convention, b1=2.7813407736, P_shot=3603, and the frozen shells, the N-body comparison still rejects the continuous analytic baseline: covariance-aware chi2/dof is 654.65/14 (fiducial), 696.87/14 (LC_m), and 797.59/14 (LC_p), with zero shells inside |pull|<=2. The result is retained as `results/mu2_gaussian_analytic_mesh_validation_v1.json`.

This isolates a real remaining issue after removing the k-cutoff bug: the continuous-shell Gaussian expression does not match the discrete CIC shell estimator at the required precision. Finite-mesh contact, repeated-index, and clustered-contact contributions must be modeled separately before Stage 7 can pass; this artifact is not used as a production mean.
