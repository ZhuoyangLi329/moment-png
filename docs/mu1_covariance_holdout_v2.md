# Covariance-aware held-out mu1 validation v2

The frozen tree-level discrete-mesh prediction was compared with realizations 070--099 for all three nodes using the same 14-shell vector (s=40--300 Mpc/h). The validation uses the sample covariance of the 30 held-out realizations divided by 30 for the covariance of the mean. The inverse is a Moore--Penrose pseudoinverse with `rcond=1e-10`; the covariance condition number is recorded.

The diagnostic produced `results/power_real_n100_n64/heldout_mu1_universal_p112_covariance_v2.json` and records diagonal pulls, RMS pull, raw chi2/dof, the Hartlap factor and corrected chi2/dof, a chi-square tail probability, and the fraction of shells with |pull| <= 2.

| node | raw chi2/dof | Hartlap chi2/dof | Hartlap p-value | fraction | covariance condition |
|---|---:|---:|---:|---:|---:|
| fiducial | 253.10/14 | 122.19/14 | 0 | 0.50 | 4.12e3 |
| LC_m | 367.22/14 | 177.28/14 | 0 | 0.43 | 3.51e3 |
| LC_p | 185.72/14 | 89.66/14 | 2.35e-259 | 0.57 | 6.15e3 |

The run status is `PASS` for execution only. It is a rejected scientific diagnostic: the tree model with universal bphi (p=1.12) fails the held-out mean comparison by a very large covariance-aware chi-square. Hartlap correction changes the scale of the statistic but does not change that conclusion. Parameter-input uncertainty is not propagated because independent bphi provenance is still unavailable; the result therefore cannot promote Stage 8 or a production configuration.
