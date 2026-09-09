# Stage 6 b_phi calibration scope audit

The new `src/audit_bphi_calibration_scope.py` performs a conservative, reproducible scan of JSON artifacts under the external NERSC analysis roots `/pscratch/sd/l/lzy/marisa-b-portable/analysis` and `/pscratch/sd/l/lzy/reconstruction-png/analysis`. It recursively records numeric fields whose names contain `bphi`, the SHA256 of each source JSON, and explicit metadata flags for the frozen selection and operator convention.

The scan found 158 JSON files with numeric `bphi`-named fields and 8 JSON parse errors. Zero files met every strict requirement simultaneously: `z=1`, `M_h >= 10^13 Msun/h`, FoF selection, real-space pre-reconstruction measurement, an explicit PNG response calibration, and independent or disjoint provenance. Missing metadata is treated as a rejection. Values from z=0.5, post-reconstruction, canary, fixed-theory, or response-fit artifacts therefore remain diagnostics and are not promoted.

The machine-readable result is `results/bphi_calibration_scope_audit_v1.json`. Its decision is `BLOCKED`, with `no_numeric_value_promoted: true`. This strengthens the existing `bphi_calibration_search` and `bphi_calibration_candidates` audits: the universal `p=1.12` and `p=1.0` branches remain assumption-only, while the training-response `b_phi=3.7636466` remains explanatory only. Stage 6 stays `ASSUMPTION_ONLY` and the Stage 5 gate stays blocked until a matching independent/disjoint calibration with uncertainty and frozen provenance is supplied.

This audit is a metadata/provenance gate; it does not fit a new value and does not alter any production configuration.
