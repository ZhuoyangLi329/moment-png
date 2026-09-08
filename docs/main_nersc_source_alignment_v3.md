# Main/NERSC source alignment v3

After the release-gate source update, the full alignment audit was rerun against the current GitHub `main` head `2148071e1126914033427e8e6c25dd2980df7007`. All 53 tracked Python files match the NERSC runtime tree byte-for-byte, with zero mismatches. This includes the cleaned analysis, theory, test, review-helper, and loader files.

The machine-readable result is `results/main_nersc_source_alignment_v3.json`; it supersedes v2 as the current alignment evidence while preserving v2 for history.
