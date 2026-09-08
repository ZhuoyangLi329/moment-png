# Stage 5: held-out mu1 shot-noise convention audit

The frozen Ngrid=64 exact-window tree projection was rerun with three declared constant power terms: `P_shot=0`, Poisson `1/nbar=5114.24 (Mpc/h)^3`, and the fiducial training-fit value `P_shot=3603`. Each prediction uses the same 14 shells from 40--300 Mpc/h, the same universal-bphi p=1.12 branch, and the same held-out realizations 070--099. The machine-readable result is `results/power_real_n100_n64/mu1_shot_noise_variant_audit_v1.json`.

| P_shot convention | fiducial Hartlap chi2/dof | LC_m | LC_p |
|---|---:|---:|---:|
| 0 | 104.21/14 | 159.00/14 | 74.86/14 |
| 1/nbar = 5114.24 | 104.11/14 | 158.76/14 | 74.78/14 |
| training fit = 3603 | 104.14/14 | 158.83/14 | 74.80/14 |

The constant shot term changes the held-out mu1 statistic by less than 0.2%, so it cannot explain the large tree-model discrepancy. This is a useful Stage 5 result: the mu1 failure is dominated by the mean-model/window or bias convention rather than a constant Poisson term. The audit remains diagnostic; it does not treat `1/nbar` as the complete mu2 contact correction, and it does not freeze a production shot-noise value.
