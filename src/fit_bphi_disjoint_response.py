#!/usr/bin/env python3
"""Fit a conditional b_phi response from a disjoint LC+/LC- block.

The fit estimates c=b1*b_phi from the PNG response. b_phi=c/b1 is reported
conditional on the independently measured low-k b1; b1 uncertainty is kept
explicitly outside this response-only fit until its covariance convention is
audited. This script never reads frozen training or held-out moments.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fit_response(template: np.ndarray, response: np.ndarray) -> dict:
    template = np.asarray(template, dtype=float)
    response = np.asarray(response, dtype=float)
    if response.ndim != 2 or template.shape != (response.shape[1],):
        raise ValueError("template must match the response observable axis")
    if len(response) < 3 or not np.isfinite(response).all() or not np.isfinite(template).all():
        raise ValueError("at least three finite response realizations are required")
    n = len(response)
    mean = response.mean(axis=0)
    cov = np.cov(response, rowvar=False, ddof=1) / n
    precision = np.linalg.pinv(cov, rcond=1e-10)
    singular = np.linalg.svd(cov, compute_uv=False)
    rank = int(np.sum(singular > singular[0] * 1e-10)) if singular.size else 0
    denom = float(template @ precision @ template)
    if not np.isfinite(denom) or denom <= 0:
        raise ValueError("response template has no identifiable covariance-weighted amplitude")
    c = float(template @ precision @ mean / denom)
    residual = mean - c * template
    chi2 = float(residual @ precision @ residual)
    hartlap = float((n - len(template) - 2) / (n - 1)) if n > len(template) + 2 else None
    return {
        "nreal": n,
        "c_b1_times_bphi": c,
        "sigma_c_statistical": float(np.sqrt(max(1.0 / denom, 0.0))),
        "chi2": chi2,
        "dof": max(rank - 1, 1),
        "chi2_dof": chi2 / max(rank - 1, 1),
        "hartlap_factor": hartlap,
        "hartlap_chi2": chi2 * hartlap if hartlap is not None else None,
        "hartlap_chi2_dof": chi2 * hartlap / max(rank - 1, 1) if hartlap is not None else None,
        "sigma_c_hartlap": float(np.sqrt(1.0 / (hartlap * denom))) if hartlap is not None else None,
        "covariance_rank": rank,
        "response_mean": mean.tolist(),
        "response_se": np.sqrt(np.maximum(np.diag(cov), 0.0)).tolist(),
    }


def conditional_bphi(c: float, sigma_c: float, b1: float) -> tuple[float, float]:
    """Convert an amplitude of the per-(b1*bphi) template exactly once."""
    if not np.isfinite(b1) or b1 <= 0:
        raise ValueError("b1 must be finite and positive")
    return float(c / b1), float(sigma_c / b1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--moments-root", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--b1", type=float, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    from exact_window import mu1_discrete
    conditional_bphi(0., 1., args.b1)

    inp = np.load(args.input)
    kvecs = np.asarray(inp["kvecs"], dtype=float)
    pm = np.asarray(inp["Pm"], dtype=float)
    cell = 1000.0 / 64.0
    transfer = (
        np.sinc(kvecs[:, 0] * cell / (2.0 * np.pi)) ** 4
        * np.sinc(kvecs[:, 1] * cell / (2.0 * np.pi)) ** 4
        * np.sinc(kvecs[:, 2] * cell / (2.0 * np.pi)) ** 4
    )
    M = np.asarray(inp["M"], dtype=float)
    scales = np.arange(40.0, 300.1, 20.0)
    minus = np.load(args.moments_root / "moments_LC_m_n64_disjoint.npz")
    plus = np.load(args.moments_root / "moments_LC_p_n64_disjoint.npz")
    ids_minus = np.asarray(minus["realization_ids"]).astype(str)
    ids_plus = np.asarray(plus["realization_ids"]).astype(str)
    expected = np.asarray([f"real{i:03d}" for i in range(100, 500)])
    if not np.array_equal(ids_minus, ids_plus) or not np.array_equal(ids_minus, expected):
        raise ValueError("response IDs must be exactly real100-real499 and paired")
    if not np.array_equal(np.asarray(minus["s"], dtype=float), scales):
        raise ValueError("disjoint moments do not use frozen shell scales")
    if not np.array_equal(np.asarray(plus["s"], dtype=float), scales):
        raise ValueError("plus moments do not use frozen shell scales")
    response = (np.asarray(plus["mu1"], dtype=float) - np.asarray(minus["mu1"], dtype=float)) / 200.0
    # dP_h/dfNL = (b1*bphi) * 2*Pm*CIC/M.  The fitted amplitude
    # is c=b1*bphi, so this template MUST NOT contain another factor b1.
    nonzero = np.linalg.norm(kvecs, axis=1) > 0
    if not np.isfinite(M[nonzero]).all() or np.any(M[nonzero] == 0):
        raise ValueError("nonzero lattice modes require finite nonzero M")
    per_c = np.zeros_like(pm)
    per_c[nonzero] = 2.0 * pm[nonzero] * transfer[nonzero] / M[nonzero]
    template = np.array(
        [
            mu1_discrete(
                kvecs,
                per_c,
                float(s), width=20.0, boxsize=1000.0, cell=cell,
                nmesh=64, power_convention="mesh",
            )
            for s in scales
        ]
    )
    fit = fit_response(template, response)
    c = fit["c_b1_times_bphi"]
    sigma_c = fit["sigma_c_statistical"]
    bphi, bphi_sigma = conditional_bphi(c, sigma_c, args.b1)
    halves = []
    for lo, hi in ((0, 200), (200, 400)):
        hfit = fit_response(template, response[lo:hi])
        halves.append({
            "start_id": str(ids_minus[lo]), "stop_id": str(ids_minus[hi - 1]),
            "nreal": hi - lo,
            "bphi_conditional": hfit["c_b1_times_bphi"] / args.b1,
            "sigma_conditional": hfit["sigma_c_statistical"] / abs(args.b1),
            "chi2_dof": hfit["chi2_dof"],
        })
    out = {
        "status": "PASS", "schema": "bphi_disjoint_response_calibration_v3",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "b1_conditioning_value": float(args.b1),
        "b1_uncertainty": "NOT_INCLUDED_PENDING_VALIDATED_B1_COVARIANCE",
        "bphi_conditional": float(bphi),
        "bphi_sigma_statistical_conditional": float(bphi_sigma),
        "c_b1_times_bphi": c, "sigma_c_statistical": sigma_c,
        "nreal": 400, "realization_ids": ids_minus.tolist(), "fNL_pair": [-100.0, 100.0],
        "response_definition": "(mu1_LC_p - mu1_LC_m)/200",
        "scales_mpc_h": scales.tolist(),
        "fit": {k: v for k, v in fit.items() if k not in ("response_mean", "response_se")},
        "stability_halves": halves, "template": template.tolist(),
        "template_parameter": "c=b1*bphi",
        "template_power_definition": "2*Pm*CIC_power/M with zero lattice mode removed",
        "normalization_correction": "Prior v2 included b1 in the template and then divided its amplitude by b1 again; the old bphi value was wrong by a factor b1, while its fitted response and chi2 were unchanged.",
        "response_mean": fit["response_mean"], "response_se": fit["response_se"],
        "input_theory": str(args.input), "input_theory_sha256": sha256(args.input),
        "moments": {
            "LC_m": str(args.moments_root / "moments_LC_m_n64_disjoint.npz"),
            "LC_p": str(args.moments_root / "moments_LC_p_n64_disjoint.npz"),
            "LC_m_sha256": sha256(args.moments_root / "moments_LC_m_n64_disjoint.npz"),
            "LC_p_sha256": sha256(args.moments_root / "moments_LC_p_n64_disjoint.npz"),
        },
        "scope": "disjoint LC+/LC- response diagnostic for frozen FoF z=1 Mh>=1e13 real-space CIC selection",
        "policy": {
            "frozen_training_ids_excluded": True, "frozen_heldout_ids_excluded": True,
            "matched_response_ids": True, "same_window_and_mesh": True,
            "production_promotion": False, "b1_uncertainty_and_cross_covariance_required": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"status": out["status"], "bphi_conditional": bphi,
                      "sigma": bphi_sigma, "chi2_dof": fit["chi2_dof"]}))


if __name__ == "__main__":
    main()
