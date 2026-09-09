# Run provenance v40

The v40 ledger records two training-only theory diagnostics under the frozen protocol. The CIC-both convention scan and the paired training-response b_phi scan were lightweight interactive analyses, so both explicitly carry `slurm_job_id: null`; the successful NERSC compute anchor remains batch job `58089819` with complete resources.

The training response gives `b_phi=3.76365` versus the universal reference `5.46702` and lowers held-out Hartlap χ²/dof to 1.96, 4.41, and 2.46. This is evidence that the universal PNG response is too strong for this selection under the current convention, but the value is fit from the training PNG response and has no independent provenance; it is blocked from production.
