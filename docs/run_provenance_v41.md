# Run provenance v41

`results/run_provenance_v41.json` records the frozen protocol, configuration and manifest SHA256 values, the current GitHub `main` source line, the NERSC root, completed Slurm jobs and resource fields, and the strict Stage 6 calibration-scope audit.

The Stage 6 scan examined 158 JSON files with numeric `bphi`-named fields across the external analysis roots; 8 files were unparsable and zero met every explicit requirement for the current z=1, FoF, M_h >= 10^13 Msun/h, real-space pre-reconstruction PNG calibration with independent or disjoint provenance. The release remains `PARTIAL`; no value was promoted.

The latest compute anchor is completed Slurm job `58089819` on `nid004078` (8 CPUs, 15240 MiB, 34 seconds). Lightweight calibration and convention scans are explicitly marked `interactive_login` with no Slurm ID because they are diagnostics rather than production runs.
