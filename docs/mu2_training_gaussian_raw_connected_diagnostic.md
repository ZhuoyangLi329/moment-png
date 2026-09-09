# Dedicated mu2 diagnostic figure

`mu2_training_gaussian_raw_connected_diagnostic.pdf` shows three rows for each of fiducial, LC_m, and LC_p: the training-only Gaussian `mu2_G` curve versus 30 held-out means, the raw `mu2` held-out moment with the Gaussian baseline overlaid, and the connected residual with a zero reference.

Curves use the 70 training realizations and exact Ngrid=64 periodic shell window; points and error bars use the 30 held-out realizations and realization-level scatter. The y axes are symlog, with the connected row using a lower linear threshold to show sign changes.

The figure is a diagnostic visualization. Raw and connected μ2 are not production fits because the halo four-point/contact decomposition remains open.
