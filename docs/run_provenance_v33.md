# Run provenance v33

This ledger records the completed NERSC batch jobs through the full-lattice mode-power identity audit, the frozen GitHub `main` commit, the immutable validation manifest, and the held-out split. Job `58087691` measured full lattice CIC mode powers for 30 held-out realizations in each of `fiducial`, `LC_m`, and `LC_p`; the v2 identity validator reports floating-point residuals below `2.6e-16` per realization.

The ledger remains `PARTIAL`: the mode-power identity closes estimator consistency, while the analytic mean model, independent `b_phi`/`b_{phi delta}` calibration, loop cutoff convergence, clustered/repeated-index contact terms, and complete halo four-point closure remain open. No production claim is made.
