# Release gate v4

`src/release_gate.py` now selects the newest source-alignment artifact (v6 through v1) and checks that the strict `bphi` calibration-scope audit exists and has recorded the expected blocked decision. These are execution and provenance checks; a blocked calibration decision is retained as a scientific blocker through Stage 6.

On the current NERSC root, the gate has 15 checks: 8 execution/provenance checks pass, including the frozen manifest, 61/61 source alignment, and the strict `bphi` audit; seven scientific stage blockers remain (Stages 2–8 except Stage 1). The machine-readable decision is `results/release_gate_v12.json` with `status: BLOCKED`.

The gate does not promote a fitted response or alter the frozen configuration.
