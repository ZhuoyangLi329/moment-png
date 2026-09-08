# Stage 5 and 7 paired resolution audit v2

The resolution comparison now uses the ten shared IDs `real000`--`real009` for every grid and checks both raw μ2 and the connected residual `mu2_connected`. The connected artifacts do not carry an ID field, so their ordering is explicitly inherited from the matching moments products and recorded in the JSON. The result is `results/resolution_mu1_mu2_audit_v2.json`.

| node | grid pair | μ1 mean abs fractional difference | raw μ2 mean abs fractional difference | connected μ2 mean abs fractional difference | connected μ2 max absolute difference |
|---|---|---:|---:|---:|---:|
| fiducial | 128/64 | 5.58% | 4.11 | 4.18 | 2.05e-2 |
| fiducial | 256/64 | 6.82% | 27.66 | 32.83 | 1.15e-1 |
| LC_m | 128/64 | 7.75% | 4.24 | 6.79 | 1.40e-2 |
| LC_m | 256/64 | 9.89% | 28.73 | 48.87 | 7.74e-2 |
| LC_p | 128/64 | 104.1%* | 3.98 | 4.78 | 2.79e-2 |
| LC_p | 256/64 | 187.2%* | 26.64 | 30.29 | 1.55e-1 |

`*` LC_p μ1 fractional values are inflated by zero crossings; paired absolute arrays remain in the machine-readable output. The connected residual also changes substantially with grid, so subtracting the Gaussian field does not by itself establish resolution convergence. The μ2 contact, repeated-index, and clustered-contact terms therefore remain unresolved and no final μ2 scale cut is frozen.
