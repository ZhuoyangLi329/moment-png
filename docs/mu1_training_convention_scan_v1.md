# Training-only CIC/shot convention scan for μ1

The convention scan fits (b_1) and (P_{\rm shot}) to the fiducial `real000`--`real069` halo-power mean at (k\le0.08\ h/{\rm Mpc}), then projects the fitted model through the exact Ngrid=64 lattice window for the held-out μ1 test. The three predeclared variants are CIC on clustering and shot, CIC on clustering with unfiltered shot, and no CIC.

The `cic_both` convention gives (b_1=2.7413), (P_{\rm shot}=5467.8), and universal-branch (b_\phi=5.466). Its held-out μ1 results are:

| node | RMS pull | χ²/dof | Hartlap χ²/dof | coverage |
|---|---:|---:|---:|---:|
| fiducial | 1.65 | 4.07 | 1.96 | 0.79 |
| LC_m | 2.86 | 16.63 | 8.03 | 0.64 |
| LC_p | 1.97 | 8.98 | 4.34 | 0.64 |

This is a substantial improvement over the fixed-(b_1=2.734) universal tree baseline. The fitted shot level is close to (1/\bar n\), supporting CIC filtering of the Poisson contribution as a plausible convention. The improvement is not a production closure: (b_\phi) still has no independent calibration, LC± residuals remain significant, and nonlinear halo terms and loops are not included. The scan is training-only and no held-out response was fitted.

The machine-readable output is `results/mu1_training_theory_convention_scan_v1.json`; it retains all three convention variants and their held-out diagnostics.
