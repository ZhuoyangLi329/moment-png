# Signed loop CIC transfer audit

Using the completed fundamental-cutoff loop components, this post-processing audit applies the signed Ngrid=64 CIC power transfer before the exact shell projection. It compares no transfer, CIC transfer with no shot term, CIC transfer with a CIC-filtered Poisson shot term, and CIC transfer with a plain constant shot term against the held-out N-body `P_h(k)` and μ1.

CIC transfer reduces the fiducial μ1 RMS pull from `4.33` to `1.67` without shot and `1.56` with the filtered Poisson shot. The LC_m and LC_p μ1 pulls remain `9.11/9.97` without shot and `9.30/9.81` with shot. The held-out `P_h(k)` RMS pulls remain `215.5/272.6/153.4` without shot and increase above `1000` when the trial shot term is added, so the transfer cannot be selected for production from this test.

The result is a signed-component convention diagnostic inherited from Slurm job `58097316`; it does not refit b_phi, alter the frozen configuration, or claim loop convergence. Stage 4 remains `OPEN` because q_min sensitivity and component residuals remain material in both `P_h(k)` and μ1.

Machine-readable result: `results/mu1_loop_signed_cic_transfer_audit_v1.json`.
