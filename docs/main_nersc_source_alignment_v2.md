# Full GitHub main / NERSC source alignment v2

The alignment audit compares every tracked Python source in the clean GitHub `main` clone with the corresponding NERSC runtime tree. It checks SHA256 byte equality rather than only import success and includes the review helper package as well as `src/`.

At main commit `54bec64`, all 53 tracked Python files matched the NERSC tree with zero mismatches. The accidental login-banner contamination was removed before this check; `python -m compileall -q src` also passes. The machine-readable result is `results/main_nersc_source_alignment_v2.json`.
