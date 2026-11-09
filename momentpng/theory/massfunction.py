"""Local-PNG halo abundance and the scale-independent bias it induces.

For a long-wavelength density shift the collapse threshold moves, so in the
peak-background split the Lagrangian bias of mass M is b_L = -(1/sigma) d ln n / d nu
at fixed M, with nu = delta_c / sigma(M). Local PNG changes the mass function by the
ratio R_NG(nu, M); to first order in fNL (Edgeworth, LoVerde et al. 2008)

    ln R_NG = (sigma S3 / 6)(nu^3 - 3 nu) - (1/6)(nu - 1/nu) d(sigma S3)/d ln nu,

where sigma S3 = <delta_R^3> / sigma^2 is linear in fNL. The scale-independent PNG bias
is then Delta b(M) = -(1/sigma) d ln R_NG / d nu |_M, and for a mass-threshold sample

    d b1 / d fNL = < Delta b > + < (b - b1) y >,   y = d ln n(M) / d fNL,

where <.> are abundance-weighted averages (the second term is the change of weights).
"""
from __future__ import annotations

import numpy as np

RHO_CRIT = 2.77536627e11  # h^2 Msun / Mpc^3, i.e. (Msun/h) / (Mpc/h)^3

trapz = getattr(np, "trapezoid", None) or np.trapz


def tophat(x):
    x = np.asarray(x, dtype=float)
    small = x < 1e-3
    xs = np.where(small, 1.0, x)
    return np.where(small, 1 - x**2 / 10, 3 * (np.sin(xs) - xs * np.cos(xs)) / xs**3)


def lagrangian_radius(mass, omega_m):
    return (3 * np.asarray(mass, dtype=float) / (4 * np.pi * omega_m * RHO_CRIT)) ** (1 / 3)


def sigma_R(R, table, nk=4000):
    """RMS linear density in a top-hat of radius R [Mpc/h] (table P_L at the output redshift)."""
    lnk = np.linspace(np.log(1e-5), np.log(80.0), nk)
    k = np.exp(lnk)
    pk = np.interp(k, table["k"], table["Pm"])
    R = np.atleast_1d(R)
    w = tophat(k[None, :] * R[:, None])
    return np.sqrt(trapz(k**3 * pk * w**2, lnk, axis=1) / (2 * np.pi**2))


def skewness_per_fnl(R, table, nk=320, nmu=48):
    """<delta_R^3> per unit fNL for local PNG (tree level, primordial bispectrum only).

    <delta^3> = 6 fNL int d3k1 d3k2 /(2pi)^6 W1 W2 W12 M1 M2 M12 P_phi(k1) P_phi(k2).
    """
    out = []
    for r in np.atleast_1d(R):
        lnk = np.linspace(np.log(1e-4), np.log(60.0 / r), nk)
        k = np.exp(lnk)
        M = np.interp(k, table["k"], table["M"])
        pphi = np.interp(k, table["k"], table["Pphi"])
        f = k**3 * tophat(k * r) * M * pphi              # per-leg factor (k^3 from d ln k)
        mu, wmu = np.polynomial.legendre.leggauss(nmu)
        k12 = np.sqrt(k[:, None, None] ** 2 + k[None, :, None] ** 2
                      + 2 * k[:, None, None] * k[None, :, None] * mu[None, None, :])
        g = tophat(k12 * r) * np.interp(k12, table["k"], table["M"])
        inner = np.einsum("ijm,m->ij", g, wmu)           # mu integral
        val = trapz(trapz(f[:, None] * f[None, :] * inner, lnk, axis=1), lnk)
        out.append(6.0 * 4 * np.pi * 2 * np.pi * val / (2 * np.pi) ** 6)
    return np.asarray(out)


def edgeworth(nu, s3sigma, ds3sigma_dlnnu):
    """ln R_NG and its nu-derivative at fixed mass (per unit fNL if the S3 inputs are)."""
    ln_r = s3sigma / 6 * (nu**3 - 3 * nu) - ds3sigma_dlnnu / 6 * (nu - 1 / nu)
    dln_r = s3sigma / 6 * (3 * nu**2 - 3) - ds3sigma_dlnnu / 6 * (1 + 1 / nu**2)
    return ln_r, dln_r


def sheth_tormen_bias(nu, delta_c=1.686, q=0.707, p=0.3):
    a = q * nu**2
    return 1 + (a - 1) / delta_c + 2 * p / (delta_c * (1 + a**p))
