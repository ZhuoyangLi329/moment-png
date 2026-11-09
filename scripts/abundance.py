#!/usr/bin/env python
"""Halo abundance response to fNL and the scale-independent PNG bias it predicts (plan A1).

1. Measure y(M) = d ln n(M) / d fNL in particle-number mass bins from paired LC_p / LC_m
   catalogs (LC_m50 vs fiducial is reported as a linearity check).
2. Analytic route: Edgeworth (LoVerde+08) mass-function ratio from the tree-level PNG
   skewness sigma*S3(M); compared with the measured y(M), optionally with delta_c -> sqrt(q) delta_c.
3. Peak-background split: Delta b(M) = -(1/sigma) d ln R_NG / d nu |_M, either from the
   analytic R_NG or from a cubic fit to the measured y(nu) (empirical route).
4. Sample prediction  d b1/d fNL = <Delta b> + <(b - b1) y>  with b(M) the Sheth-Tormen
   shape rescaled to the measured sample b1.

    python scripts/abundance.py --b1 2.756
"""
import argparse

import numpy as np

from momentpng.catalogs import positions_path
from momentpng.config import load_protocol, write_json
from momentpng.theory.inputs import load_table
from momentpng.theory.massfunction import (edgeworth, lagrangian_radius, sheth_tormen_bias, sigma_R,
                                           skewness_per_fnl)

PARTICLE_EDGES = [20, 22, 25, 28, 32, 40, 50, 64, 80, 100, 128, 160, 200, 256, 400, 640, 10**6]


def counts(proto, node, idx, mp):
    rows = []
    for i in idx:
        m = np.load(positions_path(proto.path("catalogs"), node, i).with_name("masses_msun_h.npy"))
        rows.append(np.histogram(np.round(m / mp), bins=PARTICLE_EDGES)[0])
    return np.asarray(rows, dtype=float)


def sample_db1(n0, b, y, db):
    """d b1 / d fNL of the abundance-weighted sample."""
    w = n0 / n0.sum()
    b1 = np.sum(w * b)
    return float(np.sum(w * db) + np.sum(w * (b - b1) * y))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blocks", default="train+disjoint")
    ap.add_argument("--b1", type=float, default=2.756, help="measured sample b1 to normalise b(M)")
    ap.add_argument("--q", type=float, nargs="+", default=[1.0, 0.75], help="delta_c -> sqrt(q) delta_c")
    ap.add_argument("--config", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.config)
    cosmo = proto.raw["cosmology"]
    mp = cosmo["particle_mass"]
    dc = proto.bias["delta_c"]
    idx = proto.indices(a.blocks)
    N = {n: counts(proto, n, idx, mp) for n in ("fiducial", "LC_p", "LC_m", "LC_m50")}

    # per-bin mass (abundance-weighted mean particle number) from the fiducial catalogs
    edges = np.asarray(PARTICLE_EDGES, dtype=float)
    n0 = N["fiducial"].mean(0)
    mid = np.sqrt(edges[:-1] * np.minimum(edges[1:], 4 * edges[:-1]))
    mass = mid * mp
    pair = (N["LC_p"] - N["LC_m"]) / (proto.nodes["LC_p"] - proto.nodes["LC_m"]) / n0
    y, y_err = pair.mean(0), pair.std(0, ddof=1) / np.sqrt(len(pair))
    y50 = ((N["fiducial"] - N["LC_m50"]) / 50.0 / n0).mean(0)
    tot = {n: v.sum(1) for n, v in N.items()}
    dlnN = float(np.mean((tot["LC_p"] - tot["LC_m"]) / 200.0) / tot["fiducial"].mean())

    table = load_table(proto.path("theory_table"))
    R = lagrangian_radius(mass, cosmo["Omega_m"])
    sig = sigma_R(R, table)
    s3s = skewness_per_fnl(R, table) / sig**2
    lnnu_grid = np.log(dc / sig)
    ds3s = np.gradient(s3s, lnnu_grid)

    # Gaussian bias shape, rescaled so that the abundance-weighted mean equals the measured b1
    bst = sheth_tormen_bias(dc / sig, dc)
    w = n0 / n0.sum()
    b = 1 + (bst - 1) * (a.b1 - 1) / (np.sum(w * bst) - 1)

    print(f"realizations: {len(idx)}   d ln N / d fNL (whole sample) = {dlnN:.3e}")
    print(" particles      nu     n/real      y(meas)±err     y(LC_m50)   y(Edgeworth,q=1)")
    analytic = {}
    for q in a.q:
        nu = np.sqrt(q) * dc / sig
        ln_r, dln_r = edgeworth(nu, s3s, ds3s)
        db = -dln_r / (sig / np.sqrt(q))   # -(1/sigma_eff) d ln R / d nu, sigma_eff = sigma / sqrt(q)
        analytic[q] = {"nu": nu, "y_pred": ln_r, "delta_b": db,
                       "db1_sample": sample_db1(n0, b, ln_r, db),
                       "db1_sample_measured_y": sample_db1(n0, b, y, db)}
    nu1 = dc / sig
    for i in range(len(n0)):
        print(f" {PARTICLE_EDGES[i]:4d}-{PARTICLE_EDGES[i + 1]:<7d} {nu1[i]:5.2f} {n0[i]:9.0f}   "
              f"{y[i]:+.3e}±{y_err[i]:.1e}   {y50[i]:+.3e}   {analytic[a.q[0]]['y_pred'][i]:+.3e}")

    # empirical route: smooth y(nu) with a weighted cubic, differentiate at fixed mass
    ok = n0 > 50
    coef = np.polyfit(nu1[ok], y[ok], 3, w=1 / y_err[ok])
    db_emp = -np.polyval(np.polyder(coef), nu1) / sig
    emp = sample_db1(n0, b, np.polyval(coef, nu1), db_emp)

    print("\npredicted d b1 / d fNL for the M >= 1e13 sample   (P(k) fit: -4.26e-4 at kmax 0.05)")
    for q, r in analytic.items():
        print(f"  Edgeworth q={q:<5g}: {r['db1_sample']:+.3e}   (with measured y weights: {r['db1_sample_measured_y']:+.3e})")
    print(f"  empirical PBS (cubic fit of measured y(nu)): {emp:+.3e}")

    path = write_json(proto.results / "abundance.json", {
        "blocks": a.blocks, "n_realizations": len(idx), "particle_edges": PARTICLE_EDGES,
        "particle_mass": mp, "mass": mass, "nu": nu1, "sigma": sig, "sigma_S3_per_fNL": s3s,
        "n_per_realization": n0, "y_measured": y, "y_err": y_err, "y_LC_m50": y50,
        "dlnN_dfNL": dlnN, "b_gaussian": b, "b1_sample": a.b1,
        "analytic": {str(q): r for q, r in analytic.items()},
        "empirical": {"cubic_coef": coef, "delta_b": db_emp, "db1_sample": emp}}, a)
    print(path)


if __name__ == "__main__":
    main()
