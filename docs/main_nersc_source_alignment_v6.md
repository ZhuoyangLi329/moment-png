# GitHub main / NERSC source alignment v6

The alignment check compares every tracked `src/*.py` file in the clean GitHub `main` checkout `/pscratch/sd/l/lzy/moment-png-sync` with the runtime source tree `/pscratch/sd/l/lzy/byd2pcf/src` using SHA256 byte equality.

At GitHub commit `17e6b622233e3fa014d0fb6301727898be76f570`, all 61 tracked Python source files match, with 61 matches and zero mismatches. This includes the strict Stage 6 calibration-scope audit added in this release. The check does not bundle large N-body inputs or result binaries.

The machine-readable record is `results/main_nersc_source_alignment_v6.json`.
