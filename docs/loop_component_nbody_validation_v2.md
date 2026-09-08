# Stage 4 batch component comparison

The Ngrid=64 batch loop output from Slurm job `58081558` was compared with the held-out N-body P_h and μ1 products using the same frozen shell and split definitions. The machine-readable result is `results/loop_component_nbody_validation_batch_58081558.json`; the loop k grid is interpolated onto the N-body k centers for the power comparison, while μ1 uses the exact 14-shell vector.

For the qmin=1e-4 run, total μ1 covariance-aware chi2/dof is 157.10/14 (fiducial), 364.11/14 (LC_m), and 49.96/14 (LC_p). Total P_h RMS pulls are 190.92, 365.99, and 47.55 respectively, while individual P22 and P13 pieces are also far from the measured P_h as expected for diagnostic components.

The report therefore supplies the requested per-component P_h and μ1 evidence but rejects the composite as a production mean. The large P_h residuals and qmin/quadrature sensitivity show that the current binned loop implementation does not close Stage 4.
