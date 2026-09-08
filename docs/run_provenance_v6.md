# Release code and batch provenance v6

The audited code and Slurm recipes are frozen on GitHub `main` at commit `4eb1dc9` (`Add audited resolution convention and covariance diagnostics`). The NERSC data root is `/pscratch/sd/l/lzy/byd2pcf`, and the frozen estimator configuration is `configs/baseline_v1_frozen.yaml`.

Successful batch jobs associated with this release line are:

- `58080440` on `nid004125`, 21 s, audit rerun, exit 0.
- `58080924` on `nid004098`, 13:03, Ngrid 128/256 moment generation, exit 0.
- `58081558` on `nid004103`, 1:35, Ngrid 64 loop qmin scan, exit 0.
- `58081876` on `nid004075`, 34 s, NGP/CIC/deconvolution convention audit, exit 0.

Their output hashes and input hashes remain in the corresponding JSON artifacts under `results/` on NERSC. Older loop/theory products generated directly on the login host remain identified as interactive in the provenance ledger and must be regenerated in batch before publication.

The scientific gates remain open for independent `b_phi` provenance, loop convergence, and full halo connected four-point closure; this document freezes code provenance without making a production claim.
