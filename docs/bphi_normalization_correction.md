# Disjoint response coefficient correction

The linear PNG response is `dP_h/dfNL = (b1*bphi) * 2*Pm*CIC_power/M`.
The previous disjoint v2 fitter included `b1` inside its template, fitted its
amplitude, labeled that amplitude `b1*bphi`, and then divided it by `b1` again.
Thus the reported conditional `bphi=1.37219679` was wrong by one factor of
`b1=2.73173330`.  This error did not change the fitted response or its shape
chi-squared.  Historical artifacts are retained; their parameter labels are
superseded by the corrected run, not silently reused as calibration inputs.

The corrected per-`c=b1*bphi` template contains no b1 factor.  A synthetic
known-bphi regression test and a template-reparameterization test verify that
conversion to bphi occurs once, including its conditional statistical error.
Raw and Hartlap-adjusted chi-squared/error fields are both reported.  b1 input
uncertainty and cross-covariance remain outside this conditional fit, and the
shape rejection still prevents production promotion.

The independent measured-Ph diagnostic already fits bphi directly with template
`2*(Ph-Pshot*CIC_power)/(b1*M)` and does not have this extra division error.
Its amplitude cannot establish a normalization improvement relative to the
erroneous old bphi number; that comparison must use the corrected run.

Run `sbatch slurm/slurm_bphi_normalization_refit.sbatch FULL_MAIN_COMMIT` from
the NERSC repository.  The job extracts an immutable source snapshot for that
commit and records input/output/source checksums and Slurm resource fields.
