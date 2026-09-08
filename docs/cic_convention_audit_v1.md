# Stage 5 CIC convention audit

Slurm job `58081876` measured the same ten realizations (real000--009) at Ngrid=64 with three field conventions: NGP/no-deconvolution, CIC mesh power, and CIC Fourier deconvolution. The raw output is `results/cic_convention_audit_batch_58081876.json`; the summary is `results/cic_convention_summary_58081876.json`.

Relative to CIC, the NGP convention changes μ1 by RMS 6.5--7.0e-4 and μ2 by RMS 0.039--0.046. CIC deconvolution changes μ1 by RMS 7.5--7.8e-4 and μ2 by RMS 0.0061--0.0062. Fractional metrics are reported too, but become unstable when a shell mean crosses zero.

The result establishes that μ1 is moderately convention-sensitive while μ2 is strongly convention-sensitive. The CIC mesh-power convention remains the frozen diagnostic baseline, but no μ2 production cut is promoted because contact and clustered corrections are still unresolved.
