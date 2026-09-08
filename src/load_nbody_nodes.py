#!/usr/bin/env python3
"""Load canonical fiducial/LC_m/LC_p N-body products into one theory-ready array."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

NODES = ("fiducial", "LC_m", "LC_p")
REQUIRED = ("realization_ids", "s", "k", "P_h", "nmodes", "mu1", "mu2", "mu2_gaussian", "mu2_connected", "R_mu2", "fNL")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def load_node(path):
    with np.load(path, allow_pickle=False) as d:
        missing = [k for k in REQUIRED if k not in d]
        if missing:
            raise ValueError(f"{path}: missing required arrays {missing}")
        return {k: np.asarray(d[k]) for k in REQUIRED}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True, help="directory containing nbody_<node>_n<N>.npz")
    ap.add_argument("--nmesh", type=int, default=64)
    ap.add_argument("--catalog-manifest", type=Path, default=None, help="optional quijote_manifest.json for halo metadata checks")
    ap.add_argument("--output", type=Path, required=True, help="unified .npz output path")
    args = ap.parse_args()
    arrays, source = [], {}
    for node in NODES:
        path = args.input / f"nbody_{node}_n{args.nmesh}.npz"
        if not path.exists():
            raise FileNotFoundError(path)
        source[node] = {"path": str(path), "sha256": sha256(path)}
        arrays.append(load_node(path))
    ref = arrays[0]
    ids = np.asarray(ref["realization_ids"]).astype("U")
    s = np.asarray(ref["s"], dtype=float)
    k = np.asarray(ref["k"], dtype=float)
    for node, d in zip(NODES, arrays):
        got_ids = np.asarray(d["realization_ids"]).astype("U")
        if not np.array_equal(got_ids, ids):
            raise ValueError(f"{node}: realization IDs differ from fiducial")
        if not np.array_equal(np.asarray(d["s"], dtype=float), s) or not np.array_equal(np.asarray(d["k"], dtype=float), k):
            raise ValueError(f"{node}: shell or k grid differs from fiducial")
        n = len(ids)
        for key in ("P_h", "mu1", "mu2", "mu2_gaussian", "mu2_connected", "R_mu2"):
            if d[key].shape[0] != n:
                raise ValueError(f"{node}: {key} realization axis has shape {d[key].shape}, expected {n}")
    catalog = None
    if args.catalog_manifest is not None:
        catalog = json.loads(args.catalog_manifest.read_text())
        metadata = {}
        for node in NODES:
            entries = {str(x["realization"]): x for x in catalog["nodes"][node]["realizations"]}
            missing = [x for x in ids if x not in entries]
            if missing:
                raise ValueError(f"{node}: IDs absent from catalog manifest: {missing}")
            selected = [entries[x] for x in ids]
            bad = [x["realization"] for x in selected if x.get("dtype") != "float32" or x.get("shape", [None, None])[1] != 3 or float(x.get("boxsize_mpc_h")) != 1000.0 or float(x.get("redshift")) != 1.0]
            if bad:
                raise ValueError(f"{node}: catalog metadata failed dtype/shape/box/redshift check: {bad}")
            meta_bad = []
            for x in selected:
                md = json.loads(Path(x["metadata"]).read_text())
                if (float(md.get("mass_threshold_msun_h", 0.0)) != 1.0e13 or int(md.get("snapnum", -1)) != 2 or md.get("cosmology") != node or int(md.get("n_halo_selected", -1)) != int(x["n_halo"])):
                    meta_bad.append(x["realization"])
            if meta_bad:
                raise ValueError(f"{node}: metadata failed mass-cut/snapshot/cosmology/count check: {meta_bad}")
            metadata[node] = {"n_halo": [int(x["n_halo"]) for x in selected], "dtype": sorted(set(x["dtype"] for x in selected)), "boxsize_mpc_h": sorted(set(float(x["boxsize_mpc_h"]) for x in selected)), "redshift": sorted(set(float(x["redshift"]) for x in selected)), "mass_threshold_msun_h": 1.0e13, "snapnum": 2}
    def stack(key):
        return np.stack([np.asarray(d[key]) for d in arrays], axis=0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, node_names=np.asarray(NODES), fNL=np.asarray([float(d["fNL"]) for d in arrays]), realization_ids=ids, s=s, k=k, P_h=stack("P_h"), nmodes=stack("nmodes"), mu1=stack("mu1"), mu2=stack("mu2"), mu2_gaussian=stack("mu2_gaussian"), mu2_connected=stack("mu2_connected"), R_mu2=stack("R_mu2"))
    summary = {"schema":"nbody_unified_v2", "status":"PASS", "nmesh":args.nmesh, "nodes":list(NODES), "nreal":int(len(ids)), "n_s":int(len(s)), "n_k":int(len(k)), "fNL":[float(d["fNL"]) for d in arrays], "dtypes":{key:[str(np.asarray(d[key]).dtype) for d in arrays] for key in ("P_h","mu1","mu2","mu2_gaussian","mu2_connected","R_mu2")}, "source":source, "catalog_manifest":str(args.catalog_manifest) if args.catalog_manifest else None, "catalog_metadata":metadata, "output":str(args.output), "scope":"one-command unified theory-ready N-body arrays; no PNG response fit"}
    meta = args.output.with_suffix(args.output.suffix + ".json")
    meta.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"status":"PASS", "output":str(args.output), "nodes":list(NODES), "nreal":len(ids), "n_s":len(s), "n_k":len(k), "catalog_metadata_checked":args.catalog_manifest is not None}))

if __name__ == "__main__":
    main()
