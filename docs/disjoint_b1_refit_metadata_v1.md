# Corrected metadata for full disjoint b1 fit

The original full-block fit contained the correct numerical values but mislabeled its realization block as `real100-real199`.  The refit preserves the same input power and theory, records the SHA256 of the input power, and derives the exact block from `realization_ids`: `real100-real499`, `nreal=400`.  The kmax=0.03 b1 remains 2.64631, so the scientific diagnostic is unchanged while provenance is corrected.
