#!/usr/bin/env python
"""Calibrate the linear PNG response of the halo field from paired LC_p / LC_m realizations.

    R = [X(LC_p) - X(LC_m)] / 200,   X = binned P_h (--level P), mu1(s) (--level mu1),
                                     or b(k) = P_hm / P_mm from the DM products (--level bcross)

fitted by GLS (sample covariance of the mean) to a sum of templates
    c0   : 2 P_m T_m / M        c0 = b1 * bphi  (scale-dependent bias)
    db1  : 2 b1 P_m T_m         db1 = d b1 / d fNL  (scale-independent bias, mass-function response)
    shot : T_s                  d P_shot / d fNL
mu1-level templates are the exact-window projections of the same lattice cubes; for
bcross the response is Delta b(k) = (c0/b1)/M(k) + db1 (mesh transfers cancel in the ratio).
Also reported: the per-bin effective amplitude c(x) = R / T_c0 (the "shape" diagnostic).

    python scripts/fit_response.py --level P --block disjoint --kmax 0.05 0.1 0.15
    python scripts/fit_response.py --level mu1 --block disjoint --terms c0 db1
    python scripts/fit_response.py --level mu1 --terms c0 --scan        # contiguous shell windows
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.mesh import bin_average, lattice
from momentpng.stats import gls_linear, hartlap, mean_cov
from momentpng.theory.inputs import load_table, on_lattice
from momentpng.theory.tree import response_per_c, response_per_db1, transfers
from momentpng.window import mu1


def fit(templates: dict, resp: np.ndarray) -> dict:
    mean, cov = mean_cov(resp)
    r = gls_linear(np.column_stack(list(templates.values())), mean, cov)
    err = np.sqrt(np.diag(r["cov"]))
    h = hartlap(len(resp), resp.shape[1])
    out = {name: float(v) for name, v in zip(templates, r["beta"])}
    out.update({f"{name}_sigma": float(e) for name, e in zip(templates, err)})
    out.update(chi2=r["chi2"], dof=r["dof"], chi2_dof=r["chi2_dof"],
               hartlap_chi2_dof=r["chi2_dof"] * h if h else None, n_data=resp.shape[1])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--level", choices=["P", "mu1", "bcross"], default="P")
    ap.add_argument("--block", default="disjoint", help="e.g. train, disjoint, train+disjoint")
    ap.add_argument("--terms", nargs="+", default=["c0", "db1"], choices=["c0", "db1", "shot"])
    ap.add_argument("--b1", type=float, default=2.756, help="b1 for the db1 template and c0 -> bphi")
    ap.add_argument("--convention", default="cic_both")
    ap.add_argument("--kmax", type=float, nargs="+", default=[0.05, 0.10, 0.15], help="P level")
    ap.add_argument("--smin", type=float, default=0.0, help="mu1 level")
    ap.add_argument("--smax", type=float, default=np.inf, help="mu1 level")
    ap.add_argument("--scan", action="store_true", help="mu1 level: all contiguous windows of >= 4 shells")
    ap.add_argument("--config", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.config)
    idx = proto.indices(a.block)
    if set(idx) & set(proto.block("holdout")):
        raise SystemExit("refusing to calibrate on held-out realizations")
    prefix = "matter_" if a.level == "bcross" else ""
    minus = products.load(proto.results, proto.nmesh, prefix + "LC_m", idx)
    plus = products.load(proto.results, proto.nmesh, prefix + "LC_p", idx)
    df = proto.nodes["LC_p"] - proto.nodes["LC_m"]

    lat = lattice(proto.nmesh, proto.boxsize)
    pm, M = on_lattice(load_table(proto.path("theory_table")), lat)
    tm, ts = transfers(lat, a.convention)
    cubes = {"c0": response_per_c(pm, M, tm), "db1": response_per_db1(pm, a.b1, tm),
             "shot": np.array(ts * np.ones_like(lat.k))}
    dc = proto.bias["delta_c"]

    if a.level == "bcross":
        edges = proto.power_edges
        x = np.asarray(plus["k"])
        inv_m = np.where(lat.zero, 0.0, 1.0 / np.where(lat.zero, 1.0, M))
        T = {"c0": bin_average(inv_m / a.b1, lat.k, edges),
             "db1": np.ones(len(x)), "shot": np.zeros(len(x))}
        T = {t: T[t] for t in a.terms}
        T0 = bin_average(inv_m / a.b1, lat.k, edges)
        resp = (plus["P_cross"] / plus["P_h"] - minus["P_cross"] / minus["P_h"]) / df
        cuts = [(f"kmax={k:g}", x <= k) for k in a.kmax]
    elif a.level == "P":
        edges = proto.power_edges
        x = np.asarray(plus["k"])
        T = {t: bin_average(cubes[t], lat.k, edges) for t in a.terms}
        T0 = bin_average(cubes["c0"], lat.k, edges)
        resp = (plus["P_h"] - minus["P_h"]) / df
        cuts = [(f"kmax={k:g}", x <= k) for k in a.kmax]
    else:
        x = np.asarray(plus["s"])
        T = {t: mu1(cubes[t], x, proto.shell_width, proto.boxsize) for t in a.terms}
        T0 = mu1(cubes["c0"], x, proto.shell_width, proto.boxsize)
        resp = (plus["mu1"] - minus["mu1"]) / df
        cuts = [(f"s={a.smin:g}-{min(a.smax, x.max()):g}", (x >= a.smin) & (x <= a.smax))]
        if a.scan:
            cuts += [(f"s={x[i]:g}-{x[i + n - 1]:g}", np.isin(np.arange(len(x)), range(i, i + n)))
                     for n in range(4, len(x)) for i in range(len(x) - n + 1)]

    fits = []
    for label, sel in cuts:
        f = fit({t: T[t][sel] for t in a.terms}, resp[:, sel])
        if "c0" in f:
            f["bphi"] = f["c0"] / a.b1
            f["p_equivalent"] = a.b1 - f["bphi"] / (2 * dc)
        fits.append({"cut": label, **f})
    for f in fits[:len(cuts) if not a.scan else 1]:
        print(f"{f['cut']:16s} " + "  ".join(f"{t}={f[t]:+.4g}±{f[t + '_sigma']:.2g}" for t in a.terms)
              + f"  chi2/dof={f['chi2_dof']:.2f}" + (f"  bphi={f['bphi']:.3f} (p={f['p_equivalent']:.2f})" if "c0" in f else ""))
    if a.scan:
        for f in sorted(fits[1:], key=lambda f: f["hartlap_chi2_dof"])[:5]:
            print(f"  window {f['cut']:12s} Hartlap chi2/dof={f['hartlap_chi2_dof']:.2f}  c0={f.get('c0', np.nan):.3f}")

    m, c = mean_cov(resp)
    diag = {"x": x, "c_eff": m / T0, "c_eff_sigma": np.sqrt(np.diag(c)) / np.abs(T0)}
    out = proto.results / f"response_{a.level}_{a.block}_{'+'.join(a.terms)}.json"
    write_json(out, {"level": a.level, "block": a.block, "n_pairs": len(idx), "b1": a.b1,
                     "convention": a.convention, "terms": a.terms, "fits": fits, "diagnostic": diag}, a)
    print(out)


if __name__ == "__main__":
    main()
