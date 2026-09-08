# Run provenance v36

The v36 ledger binds the successful mode-power batch to GitHub `main` commit `54bec64d12e5aa643fa1593c255bf7b112bc413f`. Slurm job `58089819` completed with exit code `0:0` on `nid004078` in 34 seconds using 8 CPUs and 15,240 MiB under `desi/shared`; its source, configuration, manifest, mode-power inputs, identity output, unified N-body package, and source-alignment result all have recorded SHA256 values.

The failed predecessor `58088569` is retained with its exact SyntaxError cause. The successful job gives 30 held-out realizations per node and reproduces direct μ1 from exact lattice mode powers at floating-point precision; mean RMS pulls are 1.218, 1.025, and 1.104, while per-realization RMS residuals are below `2.6e-16`.

The ledger remains `PARTIAL`. Scientific release is still blocked by the analytic mean-model, independent PNG-bias, loop-convergence, and halo four-point gates.
