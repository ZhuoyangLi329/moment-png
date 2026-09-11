# Joint b1--bphi covariance diagnostic

The four disjoint blocks are fit with a CIC-consistent b1/Pshot model and the corrected response amplitude `c=b1*bphi`.  With the physical constraint `Pshot>=0`, the block b1 values have large GLS errors and the block covariance gives `corr(b1,c)=-0.813`, `bphi_block_mean=3.96482`, and delta-method `sigma_bphi=0.31707`.  Some blocks lie near the Pshot boundary and their kmax=.03 fits have chi2/dof about 21--31.

This is a low-sample diagnostic from four realization blocks.  It shows why setting the b1--bphi cross-covariance to zero is unjustified, while also showing that the current external response shape is still rejected.  It does not promote a bphi value or replace a validated covariance model.
