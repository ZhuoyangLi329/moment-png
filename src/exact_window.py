"""Estimator-matched periodic shell windows. Input P is power per FULL FFT mode.

CIC applies to P, not to the shell transfer. For a continuum input the optional
fundamental-image approximation uses |A_CIC|^2 P; alias sums are NOT included.
"""
import numpy as np
from moments import shell_kernel


def cic_window(kvecs, cell):
    """CIC FIELD transfer A; the power transfer is A**2."""
    return np.prod(np.sinc(np.asarray(kvecs) * cell / (2*np.pi))**2, axis=-1)


def mesh_wavevectors(nmesh, boxsize):
    k = 2*np.pi*np.fft.fftfreq(nmesh, d=boxsize/nmesh)
    return np.stack(np.meshgrid(k, k, k, indexing='ij'), axis=-1).reshape(-1, 3)


def _geometry(kvecs, boxsize, cell, nmesh):
    if nmesh is None:
        if cell is None:
            raise ValueError('exact mesh projection requires nmesh or cell=boxsize/nmesh')
        nmesh = int(round(boxsize/cell))
    if int(nmesh) != nmesh or nmesh < 2 or boxsize <= 0:
        raise ValueError('invalid mesh geometry')
    nmesh = int(nmesh)
    if cell is not None and not np.isclose(cell*nmesh, boxsize):
        raise ValueError('cell and nmesh disagree')
    k = np.asarray(kvecs, dtype=float)
    if k.ndim != 2 or k.shape[1] != 3 or not np.isfinite(k).all():
        raise ValueError('kvecs must be finite (N,3)')
    modes = k*boxsize/(2*np.pi)
    ints = np.rint(modes).astype(int)
    if not np.allclose(modes, ints, rtol=0, atol=1e-8):
        raise ValueError('wavevectors are not periodic-box lattice modes')
    signed = np.rint(np.fft.fftfreq(nmesh)*nmesh).astype(int)
    if not np.isin(ints, signed).all():
        raise ValueError('modes outside full-FFT signed mesh convention')
    ix = ints % nmesh
    if len(np.unique(ix, axis=0)) != len(ix):
        raise ValueError('duplicate Fourier modes')
    return k, ix, nmesh


def shell_window(kvecs, s, width=20., nrad=None, cell=None,
                 boxsize=1000., nmesh=None):
    """FFT of EXACT same discrete periodic top-hat shell as moments.measure."""
    _, ix, n = _geometry(kvecs, boxsize, cell, nmesh)
    if width <= 0 or s < width/2:
        raise ValueError('require positive width and nonnegative inner radius')
    w = np.fft.fftn(shell_kernel(n, boxsize, s, width))
    if np.max(np.abs(w.imag)) > 1e-12:
        raise ValueError('shell is not inversion symmetric')
    return w.real[tuple(ix.T)]


def _power(kvecs, pk, boxsize, cell, nmesh, power_convention):
    k, ix, n = _geometry(kvecs, boxsize, cell, nmesh)
    p = np.asarray(pk, dtype=float).copy()
    if p.shape != (len(k),) or not np.isfinite(p).all() or np.any(p < 0):
        raise ValueError('power must be finite nonnegative and match mode list')
    zero = np.all(ix == 0, axis=1)
    if len(k) != n**3 and not (len(k) == n**3-1 and not zero.any()):
        raise ValueError('full FFT mode set required (zero mode may be omitted)')
    if power_convention == 'continuum_cic_no_alias':
        p *= cic_window(k, boxsize/n)**2
    elif power_convention != 'mesh':
        raise ValueError('power_convention must be mesh or continuum_cic_no_alias')
    p[zero] = 0.  # measurement subtracts catalog mean
    cube = np.zeros((n,n,n)); cube[tuple(ix.T)] = p
    neg = (-np.arange(n)) % n
    if not np.allclose(cube, cube[np.ix_(neg,neg,neg)], rtol=1e-10, atol=1e-14):
        raise ValueError('real-field power must be parity even')
    return k, p, n


def mu1_discrete(kvecs, pk, s, width=20., boxsize=1000., cell=None,
                 nmesh=None, power_convention='mesh'):
    k,p,n = _power(kvecs,pk,boxsize,cell,nmesh,power_convention)
    w = shell_window(k,s,width,boxsize=boxsize,nmesh=n)
    return float(np.sum(p*w)/boxsize**3)


def mu2_gaussian_discrete(kvecs, pk, s, width=20., boxsize=1000., cell=None,
                         nmesh=None, power_convention='mesh', sample_centered=False):
    k,p,n = _power(kvecs,pk,boxsize,cell,nmesh,power_convention)
    w = shell_window(k,s,width,boxsize=boxsize,nmesh=n)
    v = boxsize**3
    sig0 = float(p.sum()/v); sigs = float(np.sum(p*w*w)/v)
    xi = float(np.sum(p*w)/v)
    wick = sig0*sigs+xi*xi
    # E[mean(eta**2)-mean(eta)**2] subtracts Var(mean(eta)).
    correction = float(2*np.sum((p*w)**2)/v**2)
    return wick-(correction if sample_centered else 0.), {
        'sigma0_sq':sig0,'sigma_s_sq':sigs,'xi_s':xi,
        'ensemble_centered_wick':wick,'sample_mean_variance':correction,
        'sample_centered':sample_centered,'power_convention':power_convention}

