# Stage 7 Poisson contact resolution audit

The completed Slurm control job `58082476` generated iid-Poisson catalog controls at Ngrid=128 and 256, matching the existing Ngrid=64 control in halo count, shell definition, and ten random seeds. `results/poisson_contact_resolution_audit_v1.json` compares the measured connected residual with the discrete independent-cell formula

`mu2_contact = K0^2 / lambda_cell^3`.

The RMS pulls are 1.036 (Ngrid=64), 1.151 (128), and 0.970 (256), with all three grids retaining the full per-shell arrays and coverage counts. This validates the Poisson contact baseline across resolution. It does not validate the halo connected residual: clustered and repeated-index terms are absent from the iid control and remain required for the Stage 7 production decomposition.
