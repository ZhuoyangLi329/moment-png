# Slurm provenance v5

Three successful batch records are now available: audit job `58080440`, resolution generation job `58080924`, and loop component job `58081558`. The latter ran both qmin values at fixed qmax=0.03 and `(nq,nmu)=(24,24)` on `nid004103`; its output checksums are recorded in `results/slurm_loop_provenance_58081558.json`.

The consolidated ledger is `results/run_provenance_v5.json`. It remains `PARTIAL` because some older products were generated interactively and the scientific gates for loop convergence, independent PNG bias, and complete μ2 closure remain open.
