# Stage 2 block variance diagnostic

The full 400-realization disjoint b1 shift is heterogeneous by 100-realization block.  The fitted b1 values at kmax=0.03 are 2.731733 (real100--199), 2.545109 (real200--299), 2.738168 (real300--399), and 2.559147 (real400--499); the combined value is 2.646311.  This explains why the earlier 100-realization check agreed with training while the combined scan did not.  The result remains diagnostic because the block variance and Pshot/cutoff coupling have not been incorporated into a frozen production covariance.
