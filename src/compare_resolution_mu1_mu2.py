#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np

def load(path, connected=None):
    d=np.load(path)
    out={'path':str(path),'ids':[str(x) for x in d['realization_ids']], 's':d['s'].tolist(), 'mu1':np.asarray(d['mu1'],float), 'mu2':np.asarray(d['mu2'],float), 'fNL':float(d['fNL'])}
    if connected is not None and connected.exists():
        c=np.load(connected)
        if not np.allclose(np.asarray(c['s'],float), np.asarray(out['s'],float)) or len(c['mu2_connected']) != len(out['ids']):
            raise ValueError(f'Connected product mismatch for {path}')
        out['mu2_connected']=np.asarray(c['mu2_connected'],float)
        out['connected_id_source']='inherited moments ordering (connected artifact has no ID field)'
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--n128-dir',type=Path); ap.add_argument('--n256-dir',type=Path); a=ap.parse_args()
    roots={64:a.root/'results/power_real_n100_n64',128:(a.n128_dir or a.root/'results/resolution_clean/moments_n128'),256:(a.n256_dir or a.root/'results/resolution_clean/moments_n256')}; nodes={}
    for node in ['fiducial','LC_m','LC_p']:
        grids={}
        for n,p in roots.items():
            f=p/f'moments_{node}_n{n}.npz'
            c=a.root/'results/resolution_clean'/f'connected_{node}_n{n}.npz'
            if f.exists(): grids[str(n)]=load(f,c)
        row={'grids':{},'comparisons':{}}
        for n,d in grids.items():
            item={'path':d['path'],'nreal':len(d['ids']),'ids':d['ids'],'fNL':d['fNL'],'s':d['s'],'mean_mu1':d['mu1'].mean(0).tolist(),'std_mu1':d['mu1'].std(0,ddof=1).tolist(),'mean_mu2':d['mu2'].mean(0).tolist(),'std_mu2':d['mu2'].std(0,ddof=1).tolist()}
            if 'mu2_connected' in d: item['mean_mu2_connected']=d['mu2_connected'].mean(0).tolist(); item['std_mu2_connected']=d['mu2_connected'].std(0,ddof=1).tolist()
            row['grids'][n]=item
        for n in ['128','256']:
            key=f'{n}_over_64'
            if '64' not in grids or n not in grids:
                row['comparisons'][key]={'status':'OPEN','reason':f'moments n{n} missing'}; continue
            x=grids['64']; y=grids[n]; common=sorted(set(x['ids'])&set(y['ids']))
            if not common: raise ValueError(f'No common realization IDs for {node} {key}')
            ix=[x['ids'].index(i) for i in common]; iy=[y['ids'].index(i) for i in common]
            if x['s']!=y['s']: raise ValueError(f'Scale mismatch for {node} {key}')
            row['comparisons'][key]={'common_ids':len(common),'realization_ids':common,'matched_samples':True}
            for obs in ['mu1','mu2'] + (['mu2_connected'] if 'mu2_connected' in x and 'mu2_connected' in y else []):
                xx=x[obs][ix]; yy=y[obs][iy]; delta=yy-xx; xm=xx.mean(0); ym=yy.mean(0)
                row['comparisons'][key][obs]={'mean_64':xm.tolist(),'mean_high':ym.tolist(),'mean_difference':delta.mean(0).tolist(),'se_paired_difference':(delta.std(0,ddof=1)/np.sqrt(len(common))).tolist(),'ratio_high_over_64':(ym/np.where(np.abs(xm)>1e-30,xm,np.nan)).tolist(),'mean_abs_fractional_difference':float(np.mean(np.abs((ym-xm)/np.maximum(np.abs(xm),1e-30)))),'max_abs_difference':float(np.max(np.abs(ym-xm)))}
        nodes[node]=row
    out={'status':'PASS' if all('256' in x['grids'] for x in nodes.values()) else 'OPEN','schema':'resolution_mu1_mu2_audit_v1','nodes':nodes,'policy':{'scales':'40--300 step20','same_catalog_ids_required':True,'observables':['mu1','mu2']},'scope':'realization-level resolution comparison; no theory fitting'}
    a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'grids':{k:list(v['grids']) for k,v in nodes.items()}}))
if __name__=='__main__': main()
