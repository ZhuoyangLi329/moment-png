#!/usr/bin/env python
"""Simulation-based Fisher information on fNL for combinations of observables.

    sigma(fNL) from  F = d^T C^-1 d,   d = paired (X_LC_p - X_LC_m)/200,   C = fiducial covariance,
with the Hartlap correction and the derivative-noise bias removed (momentpng.stats.fisher).
Nuisance directions are other measurement *variants* of the fiducial node (e.g. a raised
mass cut '_m1.6e+13' ~ bias/amplitude, a dilution '_d2' ~ shot noise); their derivatives are
paired differences X_variant - X_base and they are marginalised over.

    python scripts/information.py --sets P mu1 mu2 mu1+mu2 P+mu1+mu2
    python scripts/information.py --config configs/explore_z1.yaml --nmesh 128 --smin 10 \\
        --nuisance _m1.6e+13 _d2
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.stats import fisher, fisher_crossvalidated

DEFAULT_SETS = ["P", "mu1", "mu2", "mu2G", "mu2c", "R", "mu3", "mu3c",
                "mu1+mu2", "mu1+mu2+mu3", "P+mu1", "P+mu2", "P+mu2c", "P+mu3c", "P+mu1+mu2+mu3"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--nmesh", type=int, default=None)
    ap.add_argument("--variant", default="", help="base measurement variant (e.g. _d2)")
    ap.add_argument("--blocks", default="train+disjoint", help="realizations used (holdout is never used)")
    ap.add_argument("--sets", nargs="+", default=DEFAULT_SETS, help="'+'-joined observables")
    ap.add_argument("--smin", type=float, default=0.0)
    ap.add_argument("--smax", type=float, default=np.inf)
    ap.add_argument("--kmax", type=float, default=None, help="P(k) cut; default 0.95 k_Nyquist (<= 0.3)")
    ap.add_argument("--nuisance", nargs="*", default=[], help="fiducial variants to marginalise over")
    ap.add_argument("--cv", type=int, default=0, metavar="K",
                    help="also report the K-fold cross-validated (compression) sigma, robust to noise fitting")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    proto = load_protocol(a.config)
    nmesh = a.nmesh or proto.nmesh
    if "holdout" in a.blocks:
        raise SystemExit("the held-out block is reserved for validation")
    idx = proto.indices(a.blocks)
    kmax = a.kmax or min(0.3, 0.95 * np.pi * nmesh / proto.boxsize)
    load = lambda node, var: products.load(proto.results, nmesh, node, idx, var)
    data = {n: load(n, a.variant) for n in ("fiducial", "LC_m", "LC_p")}
    nuis = {v: load("fiducial", v) for v in a.nuisance}
    df = proto.nodes["LC_p"] - proto.nodes["LC_m"]

    rows = []
    for spec in a.sets:
        names = spec.split("+")
        X = {n: products.features(d, names, a.smin, a.smax, kmax) for n, d in data.items()}
        derivs = {"fNL": (X["LC_p"] - X["LC_m"]) / df}
        for v, d in nuis.items():
            derivs[v] = products.features(d, names, a.smin, a.smax, kmax) - X["fiducial"]
        r = fisher(derivs, X["fiducial"])
        row = {"set": spec, "n_data": r["n_data"], "sigma_fNL": float(r["sigma"][0]),
               "sigma_fNL_unmarginalised": float(r["sigma_unmarginalised"][0])}
        msg = (f"{spec:18s} dim={r['n_data']:4d}  sigma(fNL)={row['sigma_fNL_unmarginalised']:7.2f}"
               + (f"   marginalised={row['sigma_fNL']:7.2f}" if a.nuisance else ""))
        if a.cv:
            cv = fisher_crossvalidated(derivs, X["fiducial"], k=a.cv)
            row.update(cv_sigma_fNL=float(cv["sigma"][0]), cv_sigma_fNL_unmarginalised=float(cv["sigma_unmarginalised"][0]))
            msg += (f"   | CV: {row['cv_sigma_fNL_unmarginalised']:7.2f}"
                    + (f" / marg {row['cv_sigma_fNL']:7.2f}" if a.nuisance else ""))
        rows.append(row)
        print(msg)

    tag = f"n{nmesh}{a.variant}_smin{a.smin:g}" + (f"_{a.tag}" if a.tag else "")
    path = write_json(proto.results / f"information_{tag}.json",
                      {"nmesh": nmesh, "variant": a.variant, "n_realizations": len(idx), "kmax": kmax,
                       "smin": a.smin, "smax": a.smax, "nuisance": a.nuisance, "results": rows}, a)
    print(path)


if __name__ == "__main__":
    main()
