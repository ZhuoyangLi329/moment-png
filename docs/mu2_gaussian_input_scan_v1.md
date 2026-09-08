# Gaussian μ2 input convention scan

At fixed exact discrete Ngrid=64/CIC projection, three predeclared input choices were compared with the N-body Gaussian component: `(b1,Pshot)=(2.73405,0)`, `(2.73405,3603)`, and `(2.78134,0)`. The machine-readable result is `results/mu2_gaussian_input_scan_v1.json`.

The training-fit shot term improves the absolute mismatch but the best of these choices still has chi2/dof 515.75/14 (fiducial), 384.90/14 (LC_m), and 700.06/14 (LC_p), with zero shells inside |pull|<=2. No choice is promoted or fitted on held-out PNG responses.

This scan documents that b1 and constant shot noise alone cannot close the Gaussian μ2 convention. The remaining discrepancy must be resolved through Pm/alias normalization and the explicit discrete estimator/contact treatment.
