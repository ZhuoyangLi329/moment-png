# GitHub main / NERSC source alignment

A byte-for-byte SHA256 comparison of 17 key audit, validation, theory, and batch orchestrator files found no mismatches between the clean GitHub `main` clone and `/pscratch/sd/l/lzy/byd2pcf/src`. The result is `results/main_nersc_source_alignment_v1.json`.

This confirms that the final diagnostic job ran the frozen source line. NERSC data and binary result products remain external inputs with their own checksums and are not bundled into the repository.
