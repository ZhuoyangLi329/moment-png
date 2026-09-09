# Stage 5 scale stability audit

The audit uses the frozen (s=40)--(300) Mpc/h shells and common realization IDs `real000`--`real009` to compare Ngrid 64 against 128 and 256 for every node.

Thresholds were declared before reading the result: absolute grid difference at most (2\times10^{-4}) for μ1 and (10^{-4}) for connected μ2, with at least three contiguous 20 Mpc/h shells required for a qualified interval. The intersection across fiducial, LC− and LC+ gives a μ1 candidate of 140--300 Mpc/h. Connected μ2 has only one passing shell (260 Mpc/h), so it has no qualified three-shell interval and the audit status is `BLOCKED`.

The frozen v1 range remains unchanged. The candidate is diagnostic and cannot be used to tune the held-out cut; μ2 requires a resolved clustered/repeated-index four-point treatment before a release interval can be selected.
