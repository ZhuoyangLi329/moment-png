#!/usr/bin/env python
"""Reproduce the statistical pipeline of Vislosky+2025 (arXiv 2508.13381) on Quijote (plan B3).

Their recipe: node means of 125 mocks at fNL = -X, 0, +X give a quadratic emulator
m(f) = A f^2 + B f + C per data bin; the covariance comes from the fiducial mocks
(no Hartlap); each mock of an independent fNL node is fitted on an fNL grid, and the
posterior width is compared between observable sets (mu1 alone vs mu1+mu2+mu3).

We run it as published ('reference') and with the corrections ('corrected': covariance
from the 470 non-holdout fiducial realizations + Hartlap), testing on LC_m50 (fNL=-50)
mocks that either share seeds with the emulator mocks ('same seeds') or not ('independent').

    python scripts/reference_pipeline.py --sets mu1 mu1+mu2 mu1+mu2+mu3 P
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.stats import hartlap, posterior_summary


def run(X, model_ids, test_ids, cov_ids, use_hartlap, grid):
    m0, mp, mm = (X[n][model_ids].mean(0) for n in ("fiducial", "LC_p", "LC_m"))
    B = (mp - mm) / 200.0
    A = ((mp + mm) / 2 - m0) / 100.0**2
    C = np.cov(X["fiducial"][cov_ids], rowvar=False, ddof=1)
    Ci = np.linalg.inv(C) * (hartlap(len(cov_ids), C.shape[0]) if use_hartlap else 1.0)
    model = m0 + grid[:, None] * B + grid[:, None] ** 2 * A
    rows = []
    for x in X["LC_m50"][test_ids]:
        r = x - model
        rows.append(posterior_summary(grid, -0.5 * np.einsum("gi,ij,gj->g", r, Ci, r)))
    rows = np.asarray(rows)
    width = (rows[:, 2] - rows[:, 1]) / 2
    return {"posterior_halfwidth": float(width.mean()), "median_mean": float(rows[:, 0].mean()),
            "median_scatter": float(rows[:, 0].std(ddof=1)),
            "pull_std": float(np.std((rows[:, 0] + 50) / width, ddof=1))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sets", nargs="+", default=["mu1", "mu1+mu2", "mu1+mu2+mu3", "P", "P+mu1+mu2+mu3"])
    ap.add_argument("--smin", type=float, default=60.0)
    ap.add_argument("--smax", type=float, default=260.0)
    ap.add_argument("--kmax", type=float, default=0.187)
    ap.add_argument("--nmock", type=int, default=125)
    ap.add_argument("--config", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.config)
    if proto.fnl("LC_m50") != -50:
        raise SystemExit("expects LC_m50 as the test node")
    calib = proto.indices("train+disjoint")                          # holdout never used
    model_ids = np.arange(a.nmock)                                   # positions within `calib`
    test_same = model_ids
    test_indep = np.arange(a.nmock, 2 * a.nmock)
    nodes = ("fiducial", "LC_p", "LC_m", "LC_m50")
    D = {n: products.load(proto.results, proto.nmesh, n, calib) for n in nodes}
    grid = np.linspace(-300, 200, 2001)

    out = {}
    print(f"{'set':16s} {'pipeline':10s} {'test seeds':12s} <halfwidth>  median scatter  pull std")
    for spec in a.sets:
        names = spec.split("+")
        X = {n: products.features(D[n], names, a.smin, a.smax, a.kmax) for n in nodes}
        out[spec] = {}
        for label, cov_ids, hart in [("reference", model_ids, False),
                                     ("corrected", np.arange(len(calib)), True)]:
            for tlabel, tids in [("same", test_same), ("independent", test_indep)]:
                if label == "corrected" and tlabel == "same":
                    continue
                cids = cov_ids if label == "reference" else np.setdiff1d(cov_ids, tids)
                r = run(X, model_ids, tids, cids, hart, grid)
                out[spec][f"{label}_{tlabel}"] = r
                print(f"{spec:16s} {label:10s} {tlabel:12s} {r['posterior_halfwidth']:8.1f}  "
                      f"{r['median_scatter']:12.1f}  {r['pull_std']:8.2f}")
    base = out[a.sets[0]]["reference_same"]["posterior_halfwidth"]
    for spec in a.sets[1:]:
        g = 1 - out[spec]["reference_same"]["posterior_halfwidth"] / base
        print(f"apparent gain {a.sets[0]} -> {spec} (reference pipeline, same seeds): {100 * g:+.0f}%")
    path = write_json(proto.results / "reference_pipeline.json",
                      {"nmock": a.nmock, "smin": a.smin, "smax": a.smax, "kmax": a.kmax, "results": out}, a)
    print(path)


if __name__ == "__main__":
    main()
