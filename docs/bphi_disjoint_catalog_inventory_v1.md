# Disjoint PNG catalog inventory

The certified root `FoF_z1_mmin1e13_positions` contains 500 fiducial realization directories and 100 each for `LC_m` and `LC_p`; every listed directory has both `positions_mpc_h.npy` and `metadata.json`.

The older `FoF_z1` root contains 500 directory names for fiducial and LC±, but none of those directories has the converted positions or metadata required to prove the frozen FoF (M_h\ge10^{13}\), z=1, real-space selection. The smoke root has only one realization per node.

The inventory therefore records `disjoint_png_pair_available=false` and keeps the (b_\phi) decision `BLOCKED`. Extra fiducial realizations can support Gaussian (b_1) checks, but they cannot calibrate a PNG response without a matched and certified LC± pair.
