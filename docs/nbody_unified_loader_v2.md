# Unified N-body theory-array loader v2

`src/load_nbody_nodes.py` now provides one command for the canonical Ngrid=64 products and can validate the source halo catalog metadata:

```bash
python src/load_nbody_nodes.py --input results/nbody_baseline_v1 --nmesh 64 \
  --catalog-manifest results/quijote_manifest.json \
  --output results/nbody_unified_v2.npz
```

The loader requires `realization_ids`, shell and k grids, `P_h`, `nmodes`, `mu1`, raw `mu2`, `mu2_gaussian`, `mu2_connected`, `R_mu2`, and `fNL` for `fiducial`, `LC_m`, and `LC_p`. It rejects missing fields, differing IDs or grids, and inconsistent realization axes. With `quijote_manifest.json`, it additionally checks every selected catalog entry for float32 `(N,3)` positions, z=1, and a 1000 Mpc/h box, while preserving each realization's halo count in the sidecar metadata.

The NERSC metadata-checked read passed with 100 realizations per node, 14 frozen shells, 59 k bins, and fNL labels `[0,-100,100]`. The compressed unified arrays use node order `[fiducial, LC_m, LC_p]`; source SHA256 values and halo-count arrays are recorded in `results/nbody_unified_v2.npz.json`.
