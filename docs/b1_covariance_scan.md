# Fiducial b1 covariance scan

`results/fiducial_b1_covariance_scan_v1.json` fits a constant b1 and nonnegative constant P_shot to the 100-realization fiducial N-body P_h(k), using the full realization covariance and scanning kmax. This is a diagnostic fit on the fiducial training product, not a PNG-response calibration.

The inferred b1 is strongly convention and kmax dependent. With CIC transfer, b1 is 2.626 (kmax=.03), 2.776 (.05), 2.783 (.08), and 2.784 (.10), with fitted P_shot about 11237, 4129, 3619, and 3645. Without CIC, b1 is 2.727 (.03), 2.820 (.05), 2.764 (.08), and 2.737 (.10), while the nonnegative shot fit reaches zero for kmax >= .05.

The nominal linearized b1 errors are not reliable as final uncertainties because the covariance is highly correlated and the model is misspecified. The scan demonstrates why a single very-low-k average cannot constrain b1 well, and why b1, CIC convention, P_shot, and kmax must be audited jointly before freezing a production input.


