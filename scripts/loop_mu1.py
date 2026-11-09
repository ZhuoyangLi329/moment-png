#!/usr/bin/env python
"""Fixed-cutoff one-loop mu1 and its sensitivity to the loop cutoffs (diagnostic).

Loop terms (halo P22, halo P13, one-PNG-leg loop response) are evaluated at the
centres of the protocol k bins from the full linear table, interpolated onto the
lattice, and projected with the exact window together with the tree term.
Bias inputs b1, b2, bK2 default to the independent MARISA-B values in the protocol.

    python scripts/loop_mu1.py --bphi 3.764 --pshot 5467.8 --qmax 0.03 0.05 0.08
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.mesh import lattice
from momentpng.stats import compare
from momentpng.theory.inputs import load_table, on_lattice
from momentpng.theory.loops import loop_components
from momentpng.theory.tree import halo_power, transfers
from momentpng.window import mu1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bphi", type=float, required=True)
    ap.add_argument("--pshot", type=float, default=0.0)
    ap.add_argument("--b1", type=float, default=None)
    ap.add_argument("--b2", type=float, default=None)
    ap.add_argument("--bK2", type=float, default=None)
    ap.add_argument("--qmin", type=float, default=1e-4)
    ap.add_argument("--qmax", type=float, nargs="+", default=[0.03, 0.05, 0.08])
    ap.add_argument("--nq", type=int, default=24)
    ap.add_argument("--nmu", type=int, default=24)
    ap.add_argument("--convention", default="cic_both")
    ap.add_argument("--block", default="holdout")
    ap.add_argument("--tag", default="")
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    mb = proto.bias["marisa_b"]
    b1 = a.b1 if a.b1 is not None else mb["b1"]
    b2 = a.b2 if a.b2 is not None else mb["b2"]
    bK2 = a.bK2 if a.bK2 is not None else mb["bK2"]
    table = load_table(proto.path("theory_table"))
    P = lambda q: np.interp(q, table["k"], table["Pm"])
    Mf = lambda q: np.interp(q, table["k"], table["M"])
    lat = lattice(proto.nmesh, proto.boxsize)
    pm, M = on_lattice(table, lat)
    tm, ts = transfers(lat, a.convention)
    dk, kmax = proto.power_bins
    kb = np.arange(dk / 2, kmax, dk)
    s, w = proto.scales, proto.shell_width
    idx = list(proto.block(a.block))
    data = {node: products.load(proto.results, proto.nmesh, node, idx)["mu1"] for node in proto.nodes}

    runs = []
    for qmax in a.qmax:
        comp = loop_components(kb, P, Mf, b1, b2, bK2, a.bphi, a.qmin, qmax, a.nq, a.nmu)
        on = {name: np.interp(lat.k, kb, v, left=0.0, right=v[-1]) for name, v in comp.items()}
        nodes = {}
        for node, fnl in proto.nodes.items():
            tree = halo_power(pm, M, b1, a.bphi, fnl, a.pshot, tm, ts)
            loop = (on["P22"] + on["P13"] + fnl * on["dloop_dfNL"]) * tm
            parts = {"tree": mu1(tree, s, w, proto.boxsize), "loop": mu1(loop, s, w, proto.boxsize)}
            r = compare(data[node], parts["tree"] + parts["loop"])
            nodes[node] = {"fNL": fnl, "mu1_tree": parts["tree"], "mu1_loop": parts["loop"], **r}
            print(f"qmax={qmax:.3f} {node:8s} chi2/dof={r['chi2_dof']:10.2f}  rms pull={r['rms_pull']:8.2f}")
        runs.append({"qmin": a.qmin, "qmax": qmax, "k_bins": kb, "components": comp, "nodes": nodes})

    out = proto.results / f"loop_mu1{('_' + a.tag) if a.tag else ''}.json"
    write_json(out, {"b1": b1, "b2": b2, "bK2": bK2, "bphi": a.bphi, "P_shot": a.pshot,
                     "convention": a.convention, "nq": a.nq, "nmu": a.nmu, "s": s, "runs": runs}, a)
    print(out)


if __name__ == "__main__":
    main()
