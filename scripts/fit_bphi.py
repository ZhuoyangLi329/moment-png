#!/usr/bin/env python
"""Calibrate the PNG bias from the paired mu1 response of a realization block.

    R(s) = [mu1_LC_p(s) - mu1_LC_m(s)] / 200   (paired by realization)
    model: R(s) = c * T(s),  T = exact-window projection of 2 P_m T_m / M,  c = b1 * bphi

c is the quantity the data constrain; bphi = c / b1 is reported for each --b1.
``--scan`` also fits every contiguous sub-window of >= 4 shells (diagnostic).

    python scripts/fit_bphi.py --block disjoint --b1 2.7317 2.7413
"""
import argparse

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.mesh import lattice
from momentpng.stats import gls_amplitude
from momentpng.theory.inputs import load_table, on_lattice
from momentpng.theory.tree import response_per_c, transfers, universal_bphi
from momentpng.window import mu1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--block", default="disjoint", help="train | disjoint")
    ap.add_argument("--b1", type=float, nargs="+", required=True, help="b1 value(s) to convert c -> bphi")
    ap.add_argument("--convention", default="cic_both", help="mesh transfer on the clustering term")
    ap.add_argument("--scan", action="store_true", help="fit all contiguous shell windows (>= 4 shells)")
    ap.add_argument("--output", default=None)
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    if a.block == "holdout":
        raise SystemExit("refusing to calibrate on the held-out block")
    idx = list(proto.block(a.block))
    minus = products.load(proto.results, proto.nmesh, "LC_m", idx)
    plus = products.load(proto.results, proto.nmesh, "LC_p", idx)
    df = proto.nodes["LC_p"] - proto.nodes["LC_m"]
    resp = (plus["mu1"] - minus["mu1"]) / df

    lat = lattice(proto.nmesh, proto.boxsize)
    pm, M = on_lattice(load_table(proto.path("theory_table")), lat)
    tm, _ = transfers(lat, a.convention)
    s = proto.scales
    template = mu1(response_per_c(pm, M, tm), s, proto.shell_width, proto.boxsize)

    full = gls_amplitude(template, resp)
    c, sc = full["amplitude"], full["sigma"]
    half = len(idx) // 2
    halves = [gls_amplitude(template, resp[sl])["amplitude"] for sl in (slice(0, half), slice(half, None))]
    p_tr = proto.bias["p_universal"]["tracer"]
    conversions = [{"b1": b1, "bphi": c / b1, "bphi_sigma_stat": sc / b1,
                    "bphi_universal_p_tracer": universal_bphi(b1, p_tr, proto.bias["delta_c"])[0]}
                   for b1 in a.b1]
    print(f"c = b1*bphi = {c:.4f} ± {sc:.4f}   chi2/dof = {full['chi2_dof']:.2f} "
          f"(Hartlap {full['hartlap_chi2_dof']:.2f})   halves: {halves[0]:.3f}, {halves[1]:.3f}")
    for r in conversions:
        print(f"  b1={r['b1']:.4f}: bphi = {r['bphi']:.4f} ± {r['bphi_sigma_stat']:.4f}  "
              f"(universal p={p_tr}: {r['bphi_universal_p_tracer']:.3f})")

    windows = []
    if a.scan:
        for length in range(4, len(s) + 1):
            for i in range(len(s) - length + 1):
                f = gls_amplitude(template[i:i + length], resp[:, i:i + length])
                windows.append({"s_min": s[i], "s_max": s[i + length - 1], "c": f["amplitude"],
                                "c_sigma": f["sigma"], "chi2_dof": f["chi2_dof"],
                                "hartlap_chi2_dof": f["hartlap_chi2_dof"]})
        best = sorted(windows, key=lambda w: w["hartlap_chi2_dof"])[:5]
        for w in best:
            print(f"  window {w['s_min']:.0f}-{w['s_max']:.0f}: c={w['c']:.3f}  "
                  f"Hartlap chi2/dof={w['hartlap_chi2_dof']:.2f}")

    out = a.output or proto.results / f"bphi_{a.block}_{a.convention}.json"
    write_json(out, {"block": a.block, "realizations": [idx[0], idx[-1]], "n_pairs": len(idx),
                     "convention": a.convention, "s": s, "template_per_c": template,
                     "response_mean": full["mean"], "response_se": full["se"],
                     "c": c, "c_sigma": sc, "c_sigma_hartlap": full["sigma_hartlap"],
                     "chi2": full["chi2"], "dof": full["dof"], "chi2_dof": full["chi2_dof"],
                     "hartlap_chi2_dof": full["hartlap_chi2_dof"], "c_halves": halves,
                     "bphi": conversions, "windows": windows}, a)
    print(out)


if __name__ == "__main__":
    main()
