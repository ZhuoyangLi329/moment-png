"""Pure analytic tree-level halo P_h and exact-window mu1 forward model."""
from pathlib import Path
import argparse,json,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from exact_window import mu1_discrete
from load_bias_inputs import load_bias_inputs
from marisa_b_power_loop import response_loop_basis
from halo_kernels import halo_P22

def predict(kvecs,pm,M,b1,bphi,fnl,pshot=0.,box=1000.,s=40.,width=20.,cell=None,delta_c=1.686):
 k=np.linalg.norm(kvecs,axis=1); db=bphi/np.maximum(np.abs(M),1e-30); bh=b1+fnl*db; ph=bh*bh*pm+pshot
 return mu1_discrete(kvecs,ph,s,width,box,cell),ph


def predict_with_loop(kvecs,pm,M,b1,bphi,fnl,pshot=0.,box=1000.,s=40.,width=20.,cell=None,delta_c=1.686,qmin=1e-4,qmax=30.,nq=160,nmu=96):
    """Truncated analytic one-loop correction using fixed-cutoff P22+P13.

    The loop basis is isotropic and EdS; full MARISA-B composite bias kernels
    are not silently assumed. This function is therefore a declared intermediate
    scheme for convergence studies, not a fitted response template.
    """
    k=np.linalg.norm(kvecs,axis=1); tree=(b1+fnl*bphi/np.maximum(np.abs(M),1e-30))**2*pm+pshot
    # tabulate loop terms mode-by-mode; inputs are callable wrappers for the loop integrator.
    Pm=lambda x: np.interp(np.asarray(x),k,pm,left=pm[0],right=pm[-1]); Mm=lambda x: np.interp(np.asarray(x),k,M,left=M[0],right=M[-1])
    loop=np.zeros_like(k); resp=np.zeros_like(k)
    for i,ki in enumerate(k):
        z=response_loop_basis(float(ki),Pm,Mm,b1,bphi,delta_c,qmin,qmax,nq,nmu); loop[i]=b1*b1*z['P1loop_gaussian']; resp[i]=z['dP1loop_dfNL']
    ph=tree+loop+fnl*resp
    return mu1_discrete(kvecs,ph,s,width,box,cell), {'tree':tree,'loop':loop,'response_loop':resp,'cutoff':(qmin,qmax)}

def predict_with_halo_p22(kvecs, pm, M, b1, b2, bK2, bphi, fnl, pshot=0., box=1000., s=40., width=20., cell=None, qmin=1e-4, qmax=30., nq=160, nmu=96):
    """Intermediate two-point model with explicit halo K2 P22."""
    k=np.linalg.norm(kvecs,axis=1)
    db=bphi/np.maximum(np.abs(M),1e-30)
    tree=(b1+fnl*db)**2*pm+pshot
    Pm=lambda x: np.interp(np.asarray(x), k, pm, left=pm[0], right=pm[-1])
    loop=np.array([halo_P22(float(ki), Pm, b1, b2, bK2, qmin, qmax, nq, nmu) for ki in k])
    ph=tree+loop
    return mu1_discrete(kvecs, ph, s, width, box, cell), {"tree":tree, "halo_P22":loop, "cutoff":(qmin,qmax), "kernel":"b1F2+b2/2+bK2S2"}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('input',type=Path); ap.add_argument('--bias',default='configs/bias_inputs_v1.yaml'); ap.add_argument('--b1',type=float); ap.add_argument('--bphi',type=float); ap.add_argument('--bphi-universal',action='store_true',help='derive bphi=2 delta_c (b1-p) from universal mass function'); ap.add_argument('--universality-p',type=float,default=None,help='universality parameter p; defaults to bias config universality_p_tracer'); ap.add_argument('--fNL',type=float,default=0.); ap.add_argument('--pshot',type=float,default=0.); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--shells',default='40,60,80,100'); ap.add_argument('--width',type=float,default=20.); ap.add_argument('--cell',type=float); ap.add_argument('--output',required=True); a=ap.parse_args(); d=np.load(a.input); kv=np.asarray(d['kvecs']); pm=np.asarray(d['Pm']); M=np.asarray(d['M']); b=load_bias_inputs(a.bias,False); b1=b['parameters']['b1'] if a.b1 is None else a.b1; bp=b['parameters']['bphi'] if a.bphi is None else a.bphi
 if b1 is None: raise ValueError('supply --b1 or freeze it in bias config')
 p_univ = a.universality_p if a.universality_p is not None else float(b.get('parameters',{}).get('universality_p_tracer',1.12))
 if bp is None and a.bphi_universal: bp=2*1.686*(float(b1)-p_univ)
 if bp is None: raise ValueError('supply --bphi, freeze it in bias config, or explicitly select --bphi-universal')
 vals=[{'s':s,'mu1':predict(kv,pm,M,float(b1),float(bp),a.fNL,a.pshot,a.box,s=s,width=a.width,cell=a.cell)[0]} for s in map(float,a.shells.split(','))]
 out={'model':'MARISA-B-inspired pure analytic tree-level halo P_h exact-window projection','fNL':a.fNL,'b1':float(b1),'bphi':float(bp),'bphi_source':('universal_mass_function' if a.bphi_universal and a.bphi is None else 'config_or_cli'),'universality_p':p_univ,'P_shot':a.pshot,'predictions':vals,'equation':'P_h=[b1+fNL*bphi/M(k)]^2 P_m+P_shot; universal bphi=2*delta_c*(b1-p)','scope':'tree level; b2,bK2 and fixed-cutoff one-loop contractions are not yet included'}; Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','nshell':len(vals),'scope':out['scope']}))
if __name__=='__main__': main()



