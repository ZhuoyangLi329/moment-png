# Correction to the Stage 2 covariance scan

The first execution of this diagnostic used an unsorted lattice `k` array in `np.interp`, so its intermediate chi2 values were discarded.  The authoritative artifact sorts the lattice theory k values before projection.  It gives full-block chi2/dof values 1.143, 3.206, 2.084, 2.479 and 218.227 for kmax 0.03, 0.05, 0.08, 0.10 and 0.15.  The low-k region is therefore a diagnostic candidate, while the high-k failure and b1/Pshot calibration covariance remain open.
