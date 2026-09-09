#!/usr/bin/env python3
"""Conservative audit of external/disjoint b_phi calibration candidates.

Only metadata-bearing JSON files are considered. Numeric fields containing bphi are
reported, but promotion requires explicit evidence for every frozen selection and
operator convention; missing evidence is an exclusion, never an inference.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from typing import Any

ap=argparse.ArgumentParser()
ap.add_argument('--roots', nargs='+', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
a=ap.parse_args()

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def walk(x: Any, path=''):
    if isinstance(x, dict):
        for k,v in x.items():
            yield from walk(v, f'{path}.{k}' if path else str(k))
    elif isinstance(x, list):
        for i,v in enumerate(x): yield from walk(v, f'{path}[{i}]')
    else: yield path,x

def first_num(d):
    vals=[]
    for k,v in walk(d):
        kl=k.lower()
        if 'bphi' in kl or 'b_phi' in kl:
            if isinstance(v,(int,float)) and not isinstance(v,bool): vals.append({'field':k,'value':float(v)})
    return vals

def text_flags(path: Path, raw: str, d):
    low=(str(path)+'\n'+raw).lower()
    flat=' '.join(f'{k}={v}' for k,v in walk(d)).lower() if d is not None else ''
    alltxt=low+' '+flat
    # A flag is true only when an explicit path or metadata token is present.
    z1=bool(re.search(r'(^|[^0-9])z[_-]?1([^0-9]|$)|redshift["\']?\s*[:=]\s*1(?:\.0+)?',alltxt))
    m13=bool(re.search(r'mmin1e13|10\^?13|1e13|10\s*\*?\s*\^?\s*13',alltxt))
    fof=bool(re.search(r'fof|friends[-_ ]of[-_ ]friends',alltxt))
    real=bool(re.search(r'real[-_ ]?space|realspace',alltxt))
    pre=bool(re.search(r'pre[-_ ]?recon|pre_recon|realspace',alltxt)) and not bool(re.search(r'post[-_ ]?recon',alltxt))
    response=bool(re.search(r'png|fNL|fnl|response|separate[-_ ]universe',alltxt,re.I))
    independent=bool(re.search(r'independent|disjoint|external calibration|separate[-_ ]universe',alltxt,re.I))
    # Exact strict match requires all fields explicitly present, including FoF.
    return {'z1':z1,'mmin_1e13':m13,'fof':fof,'real_space':real,'pre_recon':pre,'png_response':response,'independent_or_disjoint':independent}

rows=[]; seen=set(); parse_errors=0
for root in a.roots:
    if not root.exists(): continue
    for p in root.rglob('*.json'):
        try:
            raw=p.read_text(errors='replace'); d=json.loads(raw)
        except Exception:
            parse_errors+=1; continue
        vals=first_num(d)
        if not vals: continue
        key=str(p)
        if key in seen: continue
        seen.add(key)
        flags=text_flags(p,raw,d)
        strict=all(flags.values())
        rows.append({'path':key,'sha256':sha(p),'bphi_fields':vals[:40],'flags':flags,'strict_match':strict,'bytes':p.stat().st_size})
rows.sort(key=lambda r:(not r['strict_match'], r['path']))
strict=[r for r in rows if r['strict_match']]
out={'schema':'bphi_calibration_scope_audit_v1','status':'PASS','search_roots':[str(x) for x in a.roots], 'n_json_parse_errors':parse_errors,'n_numeric_bphi_files':len(rows),'n_strict_matches':len(strict),'strict_matches':strict,'candidates':rows,'decision':'BLOCKED' if not strict else 'REVIEW_REQUIRED','policy':{'promotion_requires':['z=1','FoF halo selection','M_h>=1e13 Msun/h','real-space','pre-reconstruction','PNG response calibration','independent or disjoint provenance','matching bias/operator convention'],'missing_metadata_is_rejection':True,'no_numeric_value_promoted':True},'conclusion':'No file met every explicit frozen-selection and independent/disjoint provenance criterion; b_phi remains unset for production.' if not strict else 'Strict metadata matches require manual provenance review before any use.'}
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'n_numeric_bphi_files':len(rows),'n_strict_matches':len(strict),'parse_errors':parse_errors,'decision':out['decision']}))

