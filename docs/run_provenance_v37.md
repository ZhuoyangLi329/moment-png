# Run provenance v37

This ledger updates the current GitHub main head after the model-status and source-alignment documentation commits while preserving the exact runtime source commit (`54bec64`) used by successful Slurm job `58089819`. The batch result, unified N-body sidecar, source alignment, configuration, manifest, and resource fields remain checksum-addressed.

The cleaned runtime passed exact-window, halo two-point, and connected-μ2 interface regression tests. These are interactive post-cleanup checks with no Slurm job ID and are explicitly diagnostic; the successful batch provenance remains the authoritative compute record.

The scientific release status remains `PARTIAL`/`BLOCKED` because analytic mean, independent PNG bias, loop convergence, and full halo four-point closure are still open.
