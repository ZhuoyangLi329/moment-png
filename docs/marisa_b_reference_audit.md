# MARISA-B local-PNG tree reference audit

## Reference

The checked reference is under /pscratch/sd/l/lzy/reconstruction-png. The relevant production runner is codes/marisa_b/scripts/production/run_pre_recon_halo_tree_fnl2_v1.py, with finite-tree output at results/marisa_b_v0p9_kmax0p20/analysis/theory_vectors/marisa_b_halo_tree_fnl2_v1_20260726/halo_pre_tree_fnl2_components_kmax0p20_nrad4_nmu80.json.

The associated z=1 table is under the same analysis tree at marisa_b_v0/marisa_b_pre_local_png_1loop_z1_diag15_kmax0p3_nmu48_eps1e3_partial446_20260616_plin_pphi_m_z1.dat. Its columns are k, P_L, P_phi, and M(k,z=1), and it documents the Hitomi dimensional P_phi convention and M=sqrt(P_L/P_phi).

## Relation to this project

The reference uses a finite-box shell projection with L=1000 Mpc/h and k_fund=2*pi/L, excludes the zero mode, and carries finite-shell denominator metadata. Its halo tree scope includes fNL^2 terms involving bphi, bphidelta, b2 and tidal-bias insertions. It is a useful physical reference for extending the current simplified halo-power model.

The reference JSON records b1=2.7465779028, bphi=5.2150606882, bphidelta=3.9405808109, and p=1.2 for that specific analysis. The current project has b1=2.7340475186 and uses a separately declared tracer universal branch p=1.12, giving bphi=5.4425682328. These values are close in scale but are not identical calibrations.

## Policy

The reference values are not silently promoted to the current production config. Before adoption, verify the exact halo finder, mass threshold, redshift, smoothing radius, P_m/P_phi/M normalization, bias convention, covariance provenance, and whether the values were fitted or fixed by assumption. Until that audit is complete, use the reference only for equations, component structure, and an explicitly labelled comparison branch.


