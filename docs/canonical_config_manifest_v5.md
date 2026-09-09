# Canonical v1 configuration and manifest v5

`configs/baseline_v1_canonical.yaml` is the single release configuration for new comparisons. It explicitly freezes z=1, L=1000 Mpc/h, FoF M_h >= 1e13 Msun/h, real-space CIC count overdensity, periodic 20 Mpc/h shells, s=40--300 Mpc/h, Ngrid 64/128/256 roles, zero-mode subtraction, and the 70/30 realization split.

`results/validation_manifest_v5.json` is an immutable successor to manifest v4. It records the canonical configuration SHA256, parent-manifest SHA256, all three node IDs and fNL labels, observable schema, and grid policy. Manifest v4 remains available as historical provenance but is not the protocol for new runs.

The canonical configuration SHA256 is `be18d402ea4d0d7fbf6fbb4988dbe0bb227b77f20c3af4d85632bf13aacc0eb5`; the manifest v5 SHA256 is `e14ddf939933a62714838a24b7dae8bec6f942752afa3eaa9d584d4e89ab91be`.
