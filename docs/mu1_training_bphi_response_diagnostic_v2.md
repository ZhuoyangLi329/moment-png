# Training-only b_phi response diagnostic v2

After selecting the CIC-both mesh convention and fitting `b1=2.7413`, `P_shot=5467.8` from fiducial training power, this diagnostic fits `b_phi` only to the paired LC_p-minus-LC_m response in the 70 training realizations. The identity

`[mu1(+100)-mu1(-100)]/200 = b_phi * 2*b1*P_m*CIC/M`

makes the response fit linear and avoids any held-out optimization. The universal reference is `b_phi=5.467`; the training response gives `b_phi=3.764`.

Applying the training-fit value to the held-out nodes gives Hartlap-corrected χ²/dof `1.96` (fiducial), `4.41` (LC_m), and `2.46` (LC_p), with 30 held-out realizations per node. This improves the PNG nodes relative to the universal response, but LC_m and LC_p still fail a strict production criterion.

This is an explanatory diagnostic only. It uses the paired PNG response from the training set and has no independent calibration provenance, so `b_phi=3.764` is not promoted to production. An external or disjoint calibration with matching z, mass cut, FoF selection, and convention remains required.
