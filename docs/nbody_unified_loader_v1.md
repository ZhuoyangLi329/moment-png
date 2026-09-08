# Unified N-body theory-array loader

`src/load_nbody_nodes.py` provides one command for the canonical Ngrid=64 products:

```bash
python src/load_nbody_nodes.py --input results/nbody_baseline_v1 --nmesh 64 --output results/nbody_unified_v1.npz
```

It requires and validates `realization_ids`, shell and k grids, `P_h`, `nmodes`, `mu1`, raw `mu2`, `mu2_gaussian`, `mu2_connected`, `R_mu2`, and `fNL` for `fiducial`, `LC_m`, and `LC_p`. It rejects missing fields, differing realization IDs, mismatched grids, or inconsistent realization axes before writing a compressed theory-ready array.

The NERSC read test passed with 100 realizations per node, 14 frozen shells, and 59 k bins. The output arrays use node axis order `[fiducial, LC_m, LC_p]`; the sidecar JSON records source SHA256 values and dtypes. This packaging check does not alter the scientific acceptance gates or fit PNG responses.
