# Stage 7 gate v3

The corrected full-lattice audit closes the Gaussian estimator identity: the ensemble-centered Wick prediction built from each held-out realization's complete Ngrid=64 `P_h` agrees with the stored `mu2_gaussian` to below `7e-17` per realization. The iid Poisson contact control remains a separate passing baseline.

Stage 7 is still `BLOCKED` for production because halo connected four-point terms, PNG response, clustered/repeated-index contacts, and primordial contributions have not been supplied and validated term by term. The Gaussian identity is necessary evidence, not a production closure.

Machine-readable gate: `results/stage7_gate_v3.json`.
