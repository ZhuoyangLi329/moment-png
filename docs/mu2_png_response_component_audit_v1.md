# Stage 7 paired PNG-response component audit

Using the shared realization IDs real000--real099, the response per unit fNL was computed as `(LC_p - LC_m)/200` for μ1, raw μ2, the Gaussian μ2 component, connected μ2, and R_mu2. The machine-readable result is `results/mu2_png_response_component_audit_v1.json`.

The RMS response-to-error pulls against zero are 49.50 for μ1, 44.94 for raw μ2, 50.22 for μ2_G, 8.07 for connected μ2, and 8.36 for R_mu2. The iid-Poisson contact control is assigned a zero PNG response by construction.

This separates a highly significant measured PNG response from the unresolved analytic closure: the connected response is not explained by the Poisson contact baseline, and no validated halo b1/b2/bK2/bphi/bphidelta or primordial-trispectrum curves are yet supplied.
