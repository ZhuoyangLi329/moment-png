# Stage 2 disjoint Gaussian b1 gate v1

The full independent fiducial block (real100--499, 400 realizations) was fit with the frozen CIC lattice convention.  At the predeclared low-k cutoff `kmax=0.03`, the fit is internally acceptable (`chi2/dof=0.645`), but `b1=2.64631` differs from the frozen training calibration `2.73405` by `-0.08774`, exceeding the `0.02` tolerance.  The higher-k scan drifts further (`b1=2.76204, 2.77797, 2.79114, 2.90125` for `kmax=0.05,0.08,0.10,0.15`), with the final cutoff rejected (`chi2/dof=221.75`).

The gate is `DIAGNOSTIC_OPEN`: the independent Gaussian audit is useful for locating amplitude and cutoff sensitivity, but it does not authorize PNG response fitting or production promotion.  The earlier 100-realization disjoint check remains a separate low-k diagnostic and is not silently substituted for this full-block result.
