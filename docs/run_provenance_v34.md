# Run provenance v34

The v34 ledger freezes the current GitHub `main` source (`b086586`), baseline configuration and validation manifest checksums, the v1 measurement protocol, the training/held-out split, and the completed NERSC jobs. Slurm job `58087691` ran on `nid004074` for 22 seconds with 8 CPUs and 15,240 MiB, and completed with exit code 0. Its mode-power inputs and v2 identity result have recorded SHA256 values.

The exact-lattice mode-power projection reproduces the direct μ1 estimator for all 30 held-out realizations in each node to floating-point precision. The overall ledger remains `PARTIAL` and the release gate remains blocked by the independent PNG-bias, loop-convergence, contact/four-point, and analytic mean-model gates.
