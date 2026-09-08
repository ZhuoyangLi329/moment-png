
"""Independent roll-sum/plane-wave checks of the estimator-matched window."""
import json
import numpy as np
from exact_window import mesh_wavevectors, shell_window, mu1_discrete, mu2_gaussian_discrete, cic_window
from moments import shell_kernel


def main():
    n=12; L=120.; s=30.; width=20.
    kv=mesh_wavevectors(n,L)
    # Independent enumeration of integer offsets (not moments.shell_kernel).
    offsets=[]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                r=L/n*np.sqrt(sum(min(q,n-q)**2 for q in (i,j,k)))
                if s-width/2 <= r < s+width/2:
                    offsets.append((i,j,k))
    rng=np.random.default_rng(914)
    delta=rng.normal(size=(n,n,n)); delta-=delta.mean()
    ds=sum(np.roll(delta, off, axis=(0,1,2)) for off in offsets)/len(offsets)
    dk=np.fft.fftn(delta)
    p=L**3*np.abs(dk.ravel())**2/n**6
    expected=float(np.mean(delta*ds))
    actual=mu1_discrete(kv,p,s,width,L,nmesh=n)
    np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-14)
    _,parts=mu2_gaussian_discrete(kv,p,s,width,L,nmesh=n)
    np.testing.assert_allclose([parts['sigma0_sq'],parts['sigma_s_sq'],parts['xi_s']],
                               [np.mean(delta**2),np.mean(ds**2),expected],rtol=1e-12,atol=1e-14)
    w=shell_window(kv,s,width,boxsize=L,nmesh=n)
    direct=np.mean(np.cos((np.asarray(offsets)*L/n) @ kv[17]),axis=0)
    np.testing.assert_allclose(w[17],direct,atol=1e-14)
    A=cic_window(kv,L/n).reshape((n,n,n))
    smoothed=np.fft.ifftn(dk*A).real
    ds_sm=sum(np.roll(smoothed,o,axis=(0,1,2)) for o in offsets)/len(offsets)
    _,cp=mu2_gaussian_discrete(kv,p,s,width,L,nmesh=n,power_convention='continuum_cic_no_alias')
    np.testing.assert_allclose([cp['sigma0_sq'],cp['sigma_s_sq'],cp['xi_s']],
        [np.mean(smoothed**2),np.mean(ds_sm**2),np.mean(smoothed*ds_sm)],rtol=1e-12,atol=1e-14)
    # Exactly solvable one Fourier-mode Gaussian ensemble, evaluated by GH quadrature.
    one=np.zeros(n**3); cube=one.reshape(n,n,n)
    cube[1,0,0]=cube[-1,0,0]=L**3/2
    nodes,weights=np.polynomial.hermite.hermgauss(5)
    cos=np.cos(2*np.pi*np.arange(n)/n)[:,None,None]*np.ones((1,n,n))
    sin=np.sin(2*np.pi*np.arange(n)/n)[:,None,None]*np.ones((1,n,n))
    mc=0.
    for i,a in enumerate(nodes*np.sqrt(2)):
        for j,b in enumerate(nodes*np.sqrt(2)):
            field=a*cos+b*sin
            filtered=sum(np.roll(field,o,axis=(0,1,2)) for o in offsets)/len(offsets)
            eta=field*filtered
            mc+=weights[i]*weights[j]/np.pi*np.mean((eta-eta.mean())**2)
    pred,_=mu2_gaussian_discrete(kv,one,s,width,L,nmesh=n,sample_centered=True)
    np.testing.assert_allclose(pred,mc,rtol=1e-12,atol=1e-14)
    # Old shortcut demonstrably differs from the discrete window.
    old=np.sinc(np.outer(np.linalg.norm(kv,axis=1),np.linspace(s-width/2,s+width/2,257))/np.pi).mean(1)
    for bad in (kv[:4], kv+0.0001):
        try: mu1_discrete(bad,np.ones(len(bad)),s,width,L,nmesh=n)
        except ValueError: pass
        else: raise AssertionError('invalid mode set accepted')
    result={'status':'PASS','nmesh':n,'n_shell_cells':len(offsets),
       'mu1_abs_error':abs(actual-expected),'gaussian_centering_abs_error':abs(pred-mc),
       'old_continuum_max_window_error':float(np.max(np.abs(old-w))),
       'scope':'window and Gaussian estimator identity only; no halo PNG closure validation'}
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
