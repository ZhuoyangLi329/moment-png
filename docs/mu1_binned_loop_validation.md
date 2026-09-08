
## Stage 4 result

The Ngrid=64 low-quadrature component validation produced total RMS pulls of 23.50 (fiducial), 261.87 (LC_m), and 218.57 (LC_p), compared with tree-only 5.18, 7.17, and 3.14. This is a controlled failure diagnostic, not a production model.




## Corrected component schema and scale dependence

The JSON schema now stores 60 radial-bin power-component values matching the k array. Signed P22/P13 components use a signed exact-window sum, while only the total spectrum is subject to the nonnegative-power convention.

The corrected total composite model improves the k<=0.03 RMS pull relative to tree-only: 1.42, 3.71, and 2.35 for fiducial, LC_m, and LC_p versus 5.18, 7.17, and 3.14. At k<=0.05 the RMS pulls are 20.86, 205.48, and 229.40. The low-k improvement is promising but is not production validation; high-k cutoff/quadrature and PNG-loop normalization remain open.


## IR cutoff evidence

At fixed qmax=0.03, changing qmin from 1e-4 to 1e-3 materially changes the first-shell projection and the PNG-node pulls. The qmin scan is stored in results/mu1_loop_qmin_validation_v1.json. The loop layer is therefore not converged in either the UV cutoff or the IR routing, and no production cutoff has been selected.
