# Current analytic-model status against N-body

The current frozen v1 protocol is `z=1`, `L=1000` Mpc/h, FoF `Mh>=1e13 Msun/h`, real-space CIC count overdensity, periodic shells, and `s=40--300` Mpc/h in 20 Mpc/h steps. All comparisons below use the real070--real099 held-out split and Ngrid=64 unless stated otherwise.

## μ1

The tree exact-discrete model with the universal-mass-function `p=1.12` branch fails the held-out mean comparison. Covariance-aware χ²/dof after the finite-sample Hartlap correction is 122.19 (fiducial), 177.28 (LC_m), and 89.66 (LC_p); the uncorrected values are 253.10, 367.22, and 185.72. Shot-noise variants `P_shot=0`, `1/nbar`, and 3603 change these values only slightly, so shot noise is not the leading discrepancy.

Replacing the external matter input with each node's measured held-out `P_h(k)` is a diagnostic normalization test, not a model calibration. It improves μ1 χ²/dof to 10.45, 7.10, and 13.63 for fiducial, LC_m, and LC_p, which isolates external `P_m/M`, CIC, or bias normalization as a major source of the tree mismatch. This diagnostic is prohibited from production because it uses held-out data.

The exact lattice mode-power projection identity is independently closed: the direct μ1 estimator and the same-realization `P_h(k)` projection differ by at most `2.6e-16` over 30 held-out realizations per node. The remaining theory discrepancy therefore is not an estimator or shell-window mismatch.

Adding P22/P13 and the PNG one-leg loop response does not currently repair the comparison. For the batch loop output, total μ1 χ²/dof is 157.10, 364.11, and 49.96, while changing the IR cutoff from `1e-4` to `1e-3` remains materially visible. Individual loop pieces are much worse, so no loop component is promoted.

## μ2

The finite-mesh discrete Gaussian μ2 baseline remains inconsistent with N-body Gaussian μ2: χ²/dof is 342.71, 249.57, and 509.50, with zero shell-mean coverage within two standard errors. Using each realization's own measured `P_h(k)` still leaves χ²/dof 24.00, 15.11, and 27.78, showing that averaging the power spectrum is not the only issue.

The paired PNG response audit gives RMS pulls of 49.50 for μ1, 44.94 for raw μ2, 50.22 for μ₂,G, 8.07 for connected μ2, and 8.36 for `R_mu2`. The Poisson contact control passes at roughly unit RMS pull, but the halo contact excess remains grid-dependent. Clustered/repeated-index contacts, halo bias operators, primordial trispectrum normalization, and a complete four-point theory are still open.

## Release decision

The execution and packaging checks pass, including the unified N-body loader, full GitHub-main/NERSC source alignment, immutable manifest, and successful batch provenance. The scientific release gate remains `BLOCKED`: the analytic mean model, independent `b_phi`/`b_{phi delta}` calibration, loop convergence, and halo four-point closure are not yet validated. No empirical response polynomial or measured-​`P_h` diagnostic is used as a production mean.
