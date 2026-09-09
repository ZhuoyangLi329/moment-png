# Stage 4 fundamental IR cutoff audit

The Ngrid=64 loop calculation was rerun with the box fundamental cutoff `q_min = 2*pi/L = 0.0062831853`, keeping `q_max=0.03`, `n_q=n_mu=24`, the frozen bias inputs, and the exact periodic shell projection unchanged. Slurm job `58097316` completed on `nid004107` in 62 seconds.

The three runs have `q_min` values `0.0001`, `0.001`, and `0.0062831853`. Relative to `q_min=0.0001`, the fundamental cutoff changes the μ1 total by RMS `8.07e-5`, `8.23e-4`, and `9.84e-4` for fNL `0`, `-100`, and `+100`; the corresponding qmin=0.001 changes are `1.27e-4`, `1.18e-3`, and `1.43e-3`. The fundamental cutoff reduces the IR shift but does not make the loop prediction stable.

Against held-out N-body, the fundamental-cutoff total has μ1 χ²/dof `162.34`, `374.55`, and `69.18` for fiducial, LC_m, and LC_p, with power-spectrum RMS pulls `213.72`, `270.47`, and `152.34`. Individual P22/P13/PNG-loop components remain discrepant as well.

This is a completed convergence diagnostic, not a production loop selection. Stage 4 remains `OPEN`; no composite model is promoted until cutoff and quadrature convergence is demonstrated in both `P_h(k)` and μ1.

Machine-readable audit: `results/loop_ir_cutoff_fundamental_audit_v1.json`.
