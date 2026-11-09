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


def compare(observed: np.ndarray, model: np.ndarray) -> dict:
    """Compare the mean of realizations ``observed`` [n, d] with a fixed ``model`` [d]."""
    obs = np.asarray(observed, dtype=float)
    mean, cov = mean_cov(obs)
    r = mean - np.asarray(model, dtype=float)
    se = np.sqrt(np.diag(cov))
    pull = r / np.maximum(se, 1e-300)
    chi2 = float(r @ np.linalg.pinv(cov, rcond=RCOND) @ r)
    dof = len(r)
    h = hartlap(len(obs), dof)
    return {"n": len(obs), "mean": mean, "se": se, "model": np.asarray(model), "pull": pull,
            "rms_pull": float(np.sqrt(np.mean(pull**2))),
            "frac_abs_pull_le_2": float(np.mean(np.abs(pull) <= 2)),
            "chi2": chi2, "dof": dof, "chi2_dof": chi2 / dof,
            "hartlap": h, "hartlap_chi2_dof": chi2 * h / dof if h else None}


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


def posterior_summary(grid: np.ndarray, loglike: np.ndarray) -> tuple[float, float, float]:
    """Median and 16/84 percentiles of a 1D gridded posterior with a flat prior."""
    trapz = getattr(np, "trapezoid", None) or np.trapz
    q = np.exp(loglike - loglike.max())
    q /= trapz(q, grid)
    c = np.cumsum(q)
    c /= c[-1]
    return tuple(float(np.interp(p, c, grid)) for p in (0.5, 0.16, 0.84))
