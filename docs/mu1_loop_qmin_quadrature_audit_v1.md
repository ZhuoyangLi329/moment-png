# Stage 4 IR-cutoff audit at matched quadrature

At Ngrid=64, qmax=0.03 h/Mpc, and `(nq,nmu)=(24,24)`, the loop projection was repeated with qmin=1e-4 and qmin=1e-3. The exact shell window, 60 lattice-k bins, bias inputs, and all three fNL nodes were held fixed. The output is `results/mu1_loop_qmin_quadrature_audit_v1.json`.

The qmin change remains material. For the PNG one-leg response, the maximum projected difference is 1.375e-2 with RMS 4.814e-3; the total differs by 1.165e-2 for fNL=-100 and 1.585e-2 for fNL=+100. The matched runs took 45.45 s and 48.00 s.

This confirms that the IR cutoff is not stable even after increasing quadrature resolution. Both the quadrature and qmin evidence are retained as Stage 4 failures, so no loop composite is promoted to the production mean model.
