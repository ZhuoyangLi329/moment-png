# Unified N-body loader smoke test

`load_nbody_nodes.py` was executed on NERSC with the canonical baseline manifest and produced `results/nbody_unified_v4.npz` in one command. The smoke test passes for `fiducial`, `LC_m` and `LC_p`, with 100 common realization IDs, 14 frozen shells and 59 Fourier bins.

The unified product contains realization-level `P_h`, `nmodes`, `mu1`, `mu2`, `mu2_gaussian`, `mu2_connected` and `R_mu2` arrays, plus node labels and (f_{NL}). The loader checked float32 halo catalog metadata, (z=1), (L=1000\,h^{-1}\mathrm{Mpc}), snapshot 2, FoF mass threshold (10^{13}\,h^{-1}M_\odot), and halo counts against `quijote_manifest.json`.

The output and metadata checksums are recorded in `nbody_unified_loader_smoke_v1.json`; this is a packaging/consistency PASS and does not promote any theory model.
