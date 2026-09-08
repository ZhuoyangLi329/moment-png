# Primordial μ2 trispectrum component audit

The local primordial trispectrum callback was projected through the collapsed μ2 interface at fNL=100 with 5000 Monte Carlo samples per shell. The output is `results/primordial_mu2_trispectrum_component_audit_v1.json`.

The run executes and reports Monte Carlo errors, but the first-shell predicted component is about 9.4e11 while the measured N-body connected even response is about 1.4e-8. The discrepancy is many orders of magnitude and is accompanied by very large integration variance, so the current P_phi/M transfer normalization and continuum window cannot be considered validated.

This is an explicit BLOCKED primordial-trispectrum component, not a production term. Halo b2/bK2/bphi/bphidelta, repeated/clustered contact, and discrete alias corrections remain separate unresolved components.
