# Stage 4 loop quadrature audit

At fixed Ngrid=64, qmin=1e-4 and qmax=0.03 h/Mpc, the loop projection was evaluated with `(nq,nmu)=(4,4)` and `(24,24)` on the same 60 radial lattice-k bins and exact shell window. Both runs recorded about 45.3 seconds, so this comparison isolates quadrature settings rather than changing the cutoff.

The machine-readable result is `results/mu1_loop_quadrature_audit_v1.json`. Increasing quadrature resolution changes the projected components by:

| fNL | component | maximum absolute difference | RMS difference |
|---:|---|---:|---:|
| 0 | P22 | 1.987e-3 | 6.067e-4 |
| 0 | P13 | 1.136e-4 | 3.270e-5 |
| -100 or +100 | PNG one-leg response | 1.375e-2 | 4.814e-3 |
| -100 | total | 1.165e-2 | 4.203e-3 |
| +100 | total | 1.585e-2 | 5.432e-3 |

The fixed-qmax loop result is therefore not quadrature-converged at the tested settings. The output retains the component-level differences and timings; it is a Stage 4 failure diagnostic and is not used as a production mean model.
