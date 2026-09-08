# Release gate v2

`src/release_gate.py` checks the frozen GitHub commit, batch provenance, frozen protocol, source alignment, and every stage status before any production claim. It returns `BLOCKED` when a stage is `OPEN`, `REJECTED`, `ASSUMPTION_ONLY`, or `NOT_READY`, while preserving execution-level PASS diagnostics.

On the current artifacts, the gate confirms the provenance and protocol checks but blocks release on the known μ1/μ2 model failures, loop convergence, independent PNG-bias calibration, and halo four-point closure. The machine-readable decision is `results/release_gate_v2.json`.
