"""Estimator identities: shell window, Fourier projection, Wick baseline, Poisson contact."""
import numpy as np
import pytest

from momentpng.mesh import binned_power, cic_paint, lattice, mode_power
from momentpng.moments import field_moments, shell_kernel
from momentpng.theory.contact import poisson_contact_iid
from momentpng.window import mu1, mu2_gaussian, shell_window

N, L, S, WIDTH = 12, 120.0, 30.0, 20.0


def shell_offsets(n, box, s, width):
    """Independent enumeration of shell cell offsets (not via shell_kernel)."""
    out = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                r = box / n * np.sqrt(sum(min(q, n - q) ** 2 for q in (i, j, k)))
                if s - width / 2 <= r < s + width / 2:
                    out.append((i, j, k))
    return out


@pytest.fixture(scope="module")
def field():
    d = np.random.default_rng(914).normal(size=(N, N, N))
    return d - d.mean()


def test_shell_kernel_matches_roll_sum(field):
    offs = shell_offsets(N, L, S, WIDTH)
    ds_roll = sum(np.roll(field, o, axis=(0, 1, 2)) for o in offs) / len(offs)
    ds_fft = np.fft.ifftn(np.fft.fftn(field) * np.fft.fftn(shell_kernel(N, L, S, WIDTH))).real
    np.testing.assert_allclose(ds_fft, ds_roll, atol=1e-13)


def test_shell_window_is_plane_wave_average():
    offs = np.asarray(shell_offsets(N, L, S, WIDTH)) * L / N
    lat = lattice(N, L)
    kvec = np.array([lat.kx[1, 0, 0], lat.ky[0, 2, 0], lat.kz[0, 0, 5]])
    direct = np.mean(np.cos(offs @ kvec))
    np.testing.assert_allclose(shell_window(N, L, S, WIDTH)[1, 2, 5], direct, atol=1e-14)


def test_projection_reproduces_field_moments(field):
    """mu1, sigma0^2, sigma_s^2 from the mode power equal the real-space estimator exactly."""
    p = mode_power(field, L)
    direct = field_moments(field, L, [S], WIDTH)
    np.testing.assert_allclose(mu1(p, [S], WIDTH, L), direct["mu1"], rtol=1e-12)
    g = mu2_gaussian(p, [S], WIDTH, L)
    np.testing.assert_allclose(g["sigma0_sq"], direct["sigma0_sq"], rtol=1e-12)
    np.testing.assert_allclose(g["sigma_s_sq"], direct["sigma_s_sq"], rtol=1e-12)
    np.testing.assert_allclose(g["mu2_gaussian"], direct["mu2_gaussian"], rtol=1e-12)


def test_sample_centered_wick_single_mode():
    """One Gaussian Fourier mode: exact ensemble mu2 by Gauss-Hermite quadrature."""
    power = np.zeros((N, N, N))
    power[1, 0, 0] = power[-1, 0, 0] = L**3 / 2
    offs = shell_offsets(N, L, S, WIDTH)
    x = 2 * np.pi * np.arange(N) / N
    cos = np.broadcast_to(np.cos(x)[:, None, None], (N, N, N))
    sin = np.broadcast_to(np.sin(x)[:, None, None], (N, N, N))
    nodes, weights = np.polynomial.hermite.hermgauss(5)
    exact = 0.0
    for wa, a in zip(weights, nodes * np.sqrt(2)):
        for wb, b in zip(weights, nodes * np.sqrt(2)):
            f = a * cos + b * sin
            eta = f * sum(np.roll(f, o, axis=(0, 1, 2)) for o in offs) / len(offs)
            exact += wa * wb / np.pi * np.mean((eta - eta.mean()) ** 2)
    pred = mu2_gaussian(power, [S], WIDTH, L, sample_centered=True)["mu2_gaussian"][0]
    np.testing.assert_allclose(pred, exact, rtol=1e-12)


def test_gaussian_random_field_mu2_matches_wick():
    """Independent Gaussian fields: measured mu2 / Wick prediction -> 1 at all scales."""
    n, box, scales = 32, 1000.0, [80.0, 120.0, 200.0]
    k = lattice(n, box).k
    amp = np.sqrt(np.exp(-(k / 0.06) ** 2))
    amp[0, 0, 0] = 0
    ratios = []
    for seed in range(8):
        d = np.fft.ifftn(np.fft.fftn(np.random.default_rng(seed).normal(size=(n, n, n))) * amp).real
        m = field_moments(d / d.std(), box, scales, 20.0)
        ratios.append(m["mu2"] / m["mu2_gaussian"])
    np.testing.assert_allclose(np.mean(ratios, axis=0), 1.0, atol=0.03)


def test_product_third_moment_algebra():
    """For jointly Gaussian X, Y: <(XY - c)^3> = 6 c sx^2 sy^2 + 2 c^3."""
    from momentpng.moments import gaussian_moments
    rng = np.random.default_rng(7)
    sx, sy, rho = 1.3, 0.7, 0.4
    c = rho * sx * sy
    x = rng.normal(size=2_000_000)
    y = sy * (rho * x + np.sqrt(1 - rho**2) * rng.normal(size=x.size))
    z = sx * x * y
    pred = gaussian_moments(c, sx**2, sy**2)
    np.testing.assert_allclose(np.mean((z - c) ** 2), pred["mu2_gaussian"], rtol=0.01)
    np.testing.assert_allclose(np.mean((z - c) ** 3), pred["mu3_gaussian"], rtol=0.03)


def test_gaussian_random_field_mu3_matches_wick():
    """Field version: mean of mu3 - mu3_G over Gaussian realizations is consistent with 0."""
    n, box, scales = 32, 1000.0, [80.0, 120.0]
    k = lattice(n, box).k
    amp = np.sqrt(np.exp(-(k / 0.06) ** 2))
    amp[0, 0, 0] = 0
    diff = []
    for seed in range(48):
        d = np.fft.ifftn(np.fft.fftn(np.random.default_rng(100 + seed).normal(size=(n, n, n))) * amp).real
        m = field_moments(d / d.std(), box, scales, 20.0)
        diff.append(m["mu3"] - m["mu3_gaussian"])
    diff = np.asarray(diff)
    pull = diff.mean(0) / (diff.std(0, ddof=1) / np.sqrt(len(diff)))
    assert np.all(np.abs(pull) < 4)


def test_cic_paint_mean_and_binning():
    pos = np.random.default_rng(1).uniform(0, L, size=(5000, 3))
    d = cic_paint(pos, N, L)
    assert abs(d.mean()) < 1e-12
    p = mode_power(d, L)
    k, pk, nm = binned_power(p, lattice(N, L).k, dk=0.05, kmax=1.0)
    assert nm.sum() == N**3 - 1  # every nonzero mode lands in exactly one bin
    np.testing.assert_allclose(np.sum(pk * nm), p.sum(), rtol=1e-12)


def test_poisson_contact_iid_monte_carlo():
    rng, n, lam = np.random.default_rng(123), 12, 20.0
    kern = np.zeros((n, n, n))
    kern[0, 0, 0], kern[1, 0, 0], kern[0, 1, 0] = 0.2, 0.3, -0.1
    fk = np.fft.fftn(kern)
    k2, k0, inv = float(np.sum(kern**2)), float(kern[0, 0, 0]), 1 / lam
    pred = inv * inv * k2 + inv * inv * k0 * k0 + poisson_contact_iid(kern, lam)
    vals = []
    for _ in range(300):
        d = (rng.poisson(lam, size=(n, n, n)) - lam) / lam
        vals.append(np.var(d * np.fft.ifftn(np.fft.fftn(d) * fk).real))
    assert abs(np.mean(vals) - pred) / (np.std(vals, ddof=1) / np.sqrt(len(vals))) < 5
