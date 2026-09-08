# Stage 7 halo contact excess audit

The real-halo connected residual was decomposed as

`mu2_connected = iid_Poisson_contact + halo_excess`.

The iid term is `K0^2/lambda_cell^3` from the matched Poisson controls, and the excess is retained as a candidate clustered/repeated-index contribution. RMS pulls of the excess against the connected-residual standard error are:

| node | Ngrid=64 | Ngrid=128 | Ngrid=256 |
|---|---:|---:|---:|
| fiducial | 6.64 | 2.30 | 2.18 |
| LC_m | 5.87 | 1.94 | 1.83 |
| LC_p | 7.00 | 2.64 | 2.51 |

The result is `results/halo_contact_excess_audit_v1.json`. The Poisson term is therefore a useful independent baseline, but it does not explain the halo connected residual on the primary grid; the remaining excess is grid-dependent and has no validated analytic halo four-point model yet.
