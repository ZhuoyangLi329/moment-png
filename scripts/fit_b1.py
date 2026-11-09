#!/usr/bin/env python
"""Fit b1 and P_shot to the fiducial binned halo power of a realization block.

Model per k bin (mode-averaged on the mesh lattice, so binning is exact):
    <P_h>_bin = b1^2 <P_m T_m>_bin + P_shot <T_s>_bin
which is linear in (b1^2, P_shot) and solved by GLS with the sample covariance
of the block mean. ``--fix-shot`` pins P_shot = 1/nbar (Poisson) and fits b1 only.

    python scripts/fit_b1.py --block disjoint
    python scripts/fit_b1.py --block train --convention cic_matter --fix-shot
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.mesh import bin_average, lattice
from momentpng.stats import gls_linear, mean_cov
from momentpng.theory.inputs import load_table, on_lattice
from momentpng.theory.tree import transfers


def fit(P, xm, xs, fix_shot):
    mean, cov = mean_cov(P)
    if fix_shot is None:
        r = gls_linear(np.column_stack([xm, xs]), mean, cov)
        b1sq, pshot = r["beta"]
        b1 = float(np.sqrt(max(b1sq, 0.0)))
        c = r["cov"]
        return {"b1": b1, "b1_sigma": float(np.sqrt(c[0, 0]) / (2 * b1)) if b1 > 0 else None,
                "P_shot": float(pshot), "P_shot_sigma": float(np.sqrt(c[1, 1])),
                "corr_b1sq_Pshot": float(c[0, 1] / np.sqrt(c[0, 0] * c[1, 1])),
                "chi2": r["chi2"], "dof": r["dof"], "chi2_dof": r["chi2_dof"]}
    r = gls_linear(xm[:, None], mean - fix_shot * xs, cov)
    b1 = float(np.sqrt(max(r["beta"][0], 0.0)))
    return {"b1": b1, "b1_sigma": float(np.sqrt(r["cov"][0, 0]) / (2 * b1)) if b1 > 0 else None,
            "P_shot": float(fix_shot), "P_shot_sigma": 0.0,
            "chi2": r["chi2"], "dof": r["dof"], "chi2_dof": r["chi2_dof"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--block", default="disjoint", help="train | holdout | disjoint")
    ap.add_argument("--kmax", type=float, nargs="+", default=[0.03, 0.05, 0.08, 0.10, 0.15])
    ap.add_argument("--convention", default="cic_both", help="cic_both | cic_matter | none")
    ap.add_argument("--fix-shot", action="store_true", help="fix P_shot = 1/nbar of the block")
    ap.add_argument("--subblock", type=int, default=100, help="also fit consecutive sub-blocks of this size")
    ap.add_argument("--output", default=None)
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    idx = list(proto.block(a.block))
    d = products.load(proto.results, proto.nmesh, "fiducial", idx)
    lat = lattice(proto.nmesh, proto.boxsize)
    pm, _ = on_lattice(load_table(proto.path("theory_table")), lat)
    tm, ts = transfers(lat, a.convention)
    edges = proto.power_edges
    xm_all = bin_average(pm * tm, lat.k, edges)
    xs_all = bin_average(ts * np.ones_like(lat.k), lat.k, edges)
    k = np.asarray(d["k"])
    nbar = float(np.mean(d["n_halo"])) / proto.boxsize**3
    shot = 1.0 / nbar if a.fix_shot else None

    rows = {}
    for kmax in a.kmax:
        sel = k <= kmax
        full = fit(d["P_h"][:, sel], xm_all[sel], xs_all[sel], shot)
        subs = [fit(d["P_h"][lo:lo + a.subblock, sel], xm_all[sel], xs_all[sel], shot)
                for lo in range(0, len(idx) - a.subblock + 1, a.subblock)] if len(idx) >= 2 * a.subblock else []
        rows[str(kmax)] = {"n_bins": int(sel.sum()), **full,
                           "subblocks_b1": [s["b1"] for s in subs],
                           "subblocks_P_shot": [s["P_shot"] for s in subs]}
        print(f"kmax={kmax:.3f}  b1={full['b1']:.4f}±{full['b1_sigma']:.4f}  "
              f"Pshot={full['P_shot']:.0f}  chi2/dof={full['chi2_dof']:.2f}")

    tag = f"{a.block}_{a.convention}" + ("_fixshot" if a.fix_shot else "")
    out = a.output or proto.results / f"b1_{tag}.json"
    write_json(out, {"block": a.block, "realizations": [idx[0], idx[-1]], "n": len(idx),
                     "convention": a.convention, "inverse_nbar": 1.0 / nbar, "fits": rows}, a)
    print(out)


if __name__ == "__main__":
    main()
