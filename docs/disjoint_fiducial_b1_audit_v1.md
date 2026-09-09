# Disjoint fiducial (b_1) audit

Slurm job `58104847` measured full-lattice CIC halo powers for fiducial `real100`--`real199`, disjoint from the frozen `real000`--`real099` validation pool. The job completed on `nid004110` with exit code 0 and recorded output checksums.

Using the same (V/N_{\rm mesh}^6|\mathrm{FFT}(\delta_{\rm CIC})|^2) convention, zero-mode removal, isotropic CIC (\mathrm{sinc}^4) transfer and the external z=1 linear spectrum, the joint (b_1,P_{\rm shot}) fit gives (b_1=2.73173), (P_{\rm shot}=6719.5) at (k_{\max}=0.03\), with (\chi^2/\mathrm{dof}=0.37). The corresponding fits at (k_{\max}=0.05,0.08,0.10,0.15) give (b_1=2.80290,2.77528,2.79077,2.90240); the last fit has (\chi^2/\mathrm{dof}=65.35), showing the nonlinear cutoff dependence.

The disjoint large-scale (b_1) agrees with the frozen training fit (b_1=2.73405) at (k_{\max}=0.03). This is an independent Gaussian (b_1/P_h) audit only; it does not calibrate (b_\phi), fit a PNG response, or alter the held-out split.
