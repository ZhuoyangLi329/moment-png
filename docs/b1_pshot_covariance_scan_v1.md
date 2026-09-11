# Covariance-aware Stage 2 b1/Pshot scan

The scan fits `P_h(k)=b1^2 P_m(k) T_CIC(k)+Pshot` using the full realization covariance, physical bounds `b1>=0`, `Pshot>=0`, and sorted lattice-theory k interpolation.  For the full disjoint block, kmax=0.03 gives b1=2.6099, Pshot=11160, b1/Pshot correlation=-0.999, and covariance-aware chi2/dof=99.12.  The fit deteriorates rapidly at kmax=.05,.08,.10,.15, with chi2/dof about 1906, 4891, 12086 and 23144.

This rejects the diagonal-fit low chi2 as an acceptance result and separates cutoff/model failure from a simple shot-noise choice.  The artifact is diagnostic and does not promote b1 or Pshot to production.
