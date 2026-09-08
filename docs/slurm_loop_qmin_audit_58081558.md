# Batch loop qmin audit

Slurm job `58081558` reran the Ngrid=64 loop components at qmax=0.03 h/Mpc and `(nq,nmu)=(24,24)` for qmin=1e-4 and 1e-3. The paired output is `results/loop_batch_qmin_audit_58081558.json`.

The maximum total projected difference between the two qmin choices is 2.79e-3 for fNL=-100 and 3.38e-3 for fNL=+100; the PNG one-leg response differs by 3.08e-3. The fNL=0 total differs by 2.95e-4. These differences are retained as a batch reproducibility result and confirm that the IR cutoff remains a material Stage 4 systematic.
