# Run provenance v38

The current figure run was intentionally performed in the NERSC interactive Python environment because plotting does not require a compute allocation. Its scheduler is recorded as `interactive_login` with `slurm_job_id: null`; the scientific batch provenance remains job `58089819`.

The figure uses 70 training realizations to form the `P_h(k)` curves and 30 held-out realizations for measured means. The held-out vectors provide `sigma_real` for errorbars and `C_realization`; `C_mean=C_realization/30` is used only for covariance-aware mean comparisons. The PDF, both v2 validation JSONs, frozen config, and manifest have SHA256 records in this ledger.
