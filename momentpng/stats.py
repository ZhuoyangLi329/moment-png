"""Small statistics toolkit: sample covariances, Hartlap, chi2 summaries, GLS fits."""
from __future__ import annotations

import numpy as np

RCOND = 1e-10  # pseudo-inverse cut used throughout (legacy convention)


def hartlap(n_samples: int, n_data: int) -> float | None:
    """Hartlap et al. (2007) debiasing factor for an inverse sample covariance."""
    return (n_samples - n_data - 2) / (n_samples - 1) if n_samples > n_data + 2 else None


def mean_cov(samples: np.ndarray):
    """Mean over axis 0 and the covariance *of the mean* (sample covariance / n)."""
    x = np.asarray(samples, dtype=float)
    return x.mean(0), np.cov(x, rowvar=False, ddof=1) / len(x)


def compare(observed: np.ndarray, model: np.ndarray, cov_samples: np.ndarray | None = None) -> dict:
    """Compare the mean of realizations ``observed`` [n, d] with a fixed ``model`` [d].

    The covariance of the mean is estimated from ``observed`` itself, or, if given, from an
    independent set ``cov_samples`` [m, d] (scaled to n); Hartlap then uses m.
    """
    from scipy.stats import chi2 as chi2_dist
    obs = np.asarray(observed, dtype=float)
    mean = obs.mean(0)
    ref = obs if cov_samples is None else np.asarray(cov_samples, dtype=float)
    cov = np.cov(ref, rowvar=False, ddof=1) / len(obs)
    r = mean - np.asarray(model, dtype=float)
    se = np.sqrt(np.diag(cov))
    pull = r / np.maximum(se, 1e-300)
    chi2 = float(r @ np.linalg.pinv(cov, rcond=RCOND) @ r)
    dof = len(r)
    h = hartlap(len(ref), dof)
    return {"n": len(obs), "n_cov": len(ref), "mean": mean, "se": se, "model": np.asarray(model),
            "pull": pull, "rms_pull": float(np.sqrt(np.mean(pull**2))),
            "frac_abs_pull_le_2": float(np.mean(np.abs(pull) <= 2)),
            "chi2": chi2, "dof": dof, "chi2_dof": chi2 / dof,
            "hartlap": h, "hartlap_chi2_dof": chi2 * h / dof if h else None,
            "p_value": float(chi2_dist.sf(chi2 * h, dof)) if h else None}


def gls_amplitude(template: np.ndarray, samples: np.ndarray) -> dict:
    """Best-fit amplitude A of mean(samples) = A * template with the sample covariance of the mean."""
    t = np.asarray(template, dtype=float)
    x = np.asarray(samples, dtype=float)
    n = len(x)
    mean, cov = mean_cov(x)
    prec = np.linalg.pinv(cov, rcond=RCOND)
    sv = np.linalg.svd(cov, compute_uv=False)
    rank = int(np.sum(sv > sv[0] * RCOND))
    denom = float(t @ prec @ t)
    amp = float(t @ prec @ mean / denom)
    r = mean - amp * t
    chi2 = float(r @ prec @ r)
    dof = max(rank - 1, 1)
    h = hartlap(n, len(t))
    return {"n": n, "amplitude": amp, "sigma": float(np.sqrt(1 / denom)),
            "sigma_hartlap": float(np.sqrt(1 / (h * denom))) if h else None,
            "chi2": chi2, "dof": dof, "chi2_dof": chi2 / dof,
            "hartlap_chi2_dof": chi2 * h / dof if h else None,
            "mean": mean, "se": np.sqrt(np.diag(cov))}


def gls_linear(design: np.ndarray, y: np.ndarray, cov: np.ndarray) -> dict:
    """Generalised least squares y = X beta with covariance ``cov`` (eigen-whitened, pinv cut)."""
    X, y = np.asarray(design, float), np.asarray(y, float)
    eig, u = np.linalg.eigh(cov)
    keep = eig > max(float(eig.max()), 1e-300) * RCOND
    R = (u[:, keep] / np.sqrt(eig[keep])).T
    A, b = R @ X, R @ y
    beta, *_ = np.linalg.lstsq(A, b, rcond=None)
    cov_beta = np.linalg.pinv(A.T @ A)
    chi2 = float(np.sum((b - A @ beta) ** 2))
    dof = max(len(y) - X.shape[1], 1)
    return {"beta": beta, "cov": cov_beta, "chi2": chi2, "dof": dof, "chi2_dof": chi2 / dof}


def fisher(derivatives: dict, fiducial: np.ndarray, hartlap_correct: bool = True,
           noise_correct: bool = True) -> dict:
    """Fisher matrix from simulation-based derivatives.

    ``derivatives`` maps parameter -> [n_a, d] per-realization derivative estimates
    (e.g. paired (X_+ - X_-) / (2 dp)); the derivative is their mean. Arrays with
    equal n are assumed realization-aligned, so their cross-covariance enters the
    noise-bias correction  F_ab -= tr(C^-1 Cov[d_a, d_b]) / n.
    ``fiducial`` [n, d] realizations give the data covariance.
    """
    x = np.asarray(fiducial, dtype=float)
    n, dim = x.shape
    ci = np.linalg.inv(np.cov(x, rowvar=False, ddof=1))
    if hartlap_correct:
        h = hartlap(n, dim)
        if h is None:
            raise ValueError(f"too few fiducial realizations ({n}) for {dim} data")
        ci *= h
    names = list(derivatives)
    D = {a: np.asarray(derivatives[a], dtype=float) for a in names}
    mean = {a: D[a].mean(0) for a in names}
    F = np.empty((len(names), len(names)))
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            F[i, j] = mean[a] @ ci @ mean[b]
            if noise_correct and len(D[a]) == len(D[b]):
                cab = (D[a] - mean[a]).T @ (D[b] - mean[b]) / (len(D[a]) - 1) / len(D[a])
                F[i, j] -= float(np.trace(ci @ cab))
    Finv = np.linalg.inv(F)
    with np.errstate(invalid="ignore", divide="ignore"):  # noise-corrected F may be non-positive -> NaN
        sig = np.sqrt(np.diag(Finv))
        sig_u = 1 / np.sqrt(np.diag(F))
    return {"params": names, "F": F, "sigma": sig, "sigma_unmarginalised": sig_u,
            "n_fiducial": n, "n_data": dim}


def fisher_crossvalidated(derivatives: dict, fiducial: np.ndarray, k: int = 5, seed: int = 0) -> dict:
    """Noise-robust Fisher via K-fold score compression.

    For each fold, compression weights W = C^-1 D are estimated on the other folds; on the
    held-out fold the compressed statistics t = X W (one per parameter) get their own
    covariance and derivatives, and the small p x p Fisher is formed there. Weight noise can
    only *lose* information, so this is a conservative (never noise-inflated) estimate.
    All arrays must be realization-aligned with ``fiducial`` (paired derivative samples).
    """
    x = np.asarray(fiducial, dtype=float)
    names = list(derivatives)
    D = {a: np.asarray(derivatives[a], dtype=float) for a in names}
    if any(len(v) != len(x) for v in D.values()):
        raise ValueError("cross-validated Fisher needs realization-aligned derivative samples")
    folds = np.array_split(np.random.default_rng(seed).permutation(len(x)), k)
    Fsum = np.zeros((len(names), len(names)))
    for f in folds:
        train = np.setdiff1d(np.arange(len(x)), f)
        W = np.linalg.solve(np.cov(x[train], rowvar=False, ddof=1),
                            np.column_stack([D[a][train].mean(0) for a in names]))
        t = x[f] @ W
        dts = [D[a][f] @ W for a in names]                              # per-realization, [n_f, p]
        dt = np.vstack([v.mean(0) for v in dts])                        # [param, compressed]
        cti = np.linalg.inv(np.atleast_2d(np.cov(t, rowvar=False, ddof=1)))
        Ff = dt @ cti @ dt.T
        for i in range(len(names)):                                     # derivative-noise bias
            for j in range(len(names)):
                cij = (dts[i] - dts[i].mean(0)).T @ (dts[j] - dts[j].mean(0)) / (len(f) - 1) / len(f)
                Ff[i, j] -= float(np.trace(cti @ np.atleast_2d(cij)))
        Fsum += Ff
    F = Fsum / k
    with np.errstate(invalid="ignore", divide="ignore"):
        sig = np.sqrt(np.diag(np.linalg.inv(F)))
        sig_u = 1 / np.sqrt(np.diag(F))
    return {"params": names, "F": F, "sigma": sig, "sigma_unmarginalised": sig_u, "k": k}


def posterior_summary(grid: np.ndarray, loglike: np.ndarray) -> tuple[float, float, float]:
    """Median and 16/84 percentiles of a 1D gridded posterior with a flat prior."""
    trapz = getattr(np, "trapezoid", None) or np.trapz
    q = np.exp(loglike - loglike.max())
    q /= trapz(q, grid)
    c = np.cumsum(q)
    c /= c[-1]
    return tuple(float(np.interp(p, c, grid)) for p in (0.5, 0.16, 0.84))
