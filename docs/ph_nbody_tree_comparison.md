# N-body P_h(k) tree comparison

The first unified comparison is `results/ph_nbody_tree_comparison_v1.json`. It compares the Ngrid=64 canonical N-body mesh halo spectra for fiducial, LC_m, and LC_p with the tree halo model using b1=2.7340475186, the explicit universal tracer branch p=1.12, bphi=5.4425682328, the external z=1 P_L/P_phi/M table, and an isotropic-bin average of the CIC power transfer.

The comparison uses the same 100-realization products and reports per-bin means, standard errors, model/data ratios, pulls, and kmax scans. The broad all-k RMS pull is dominated by high-k bins where the standard error is small and the simple tree model omits nonlinear halo corrections. Restricting to k<=0.03 still gives RMS pulls of 6.78 (fiducial), 11.00 (LC_m), and 3.66 (LC_p), so the low-k comparison is not yet accepted as a model validation.

At the first k bin (0.0075 h/Mpc), model/data ratios are about 0.90 (fiducial), 0.61 (LC_m), and 1.05 (LC_p). This demonstrates a scale-dependent PNG mismatch in addition to the general nonlinear amplitude mismatch. The result is a diagnostic failure, not a reason to fit bphi on the validation nodes.

Next actions are to verify the P_L/P_phi/M units and growth convention, compare no-CIC and CIC-transfer variants, include explicit shot-noise choices, and then test the MARISA-B finite halo-tree PNG components. Only after those checks should a kmax or production cut be considered.




## Formal mu1 N-body validation

src/validate_mu1_nbody_model.py creates results/mu1_nbody_tree_validation_v1.json using the frozen 70/30 split and node-matched p=1.12 exact-discrete predictions. The covariance-aware chi2/dof values are 253.10 (fiducial), 367.22 (LC_m), and 185.72 (LC_p), so the tree model is decisively rejected as a full N-body mean model under the current conventions.
