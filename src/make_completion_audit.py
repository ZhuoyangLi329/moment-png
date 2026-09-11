#!/usr/bin/env python3
"""Requirement-level completion audit; never promotes diagnostics to PASS."""
import argparse, datetime, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); r=a.root
    stage=json.loads((r/'results/stage_progress_v31.json').read_text()); gate=json.loads((r/'results/release_gate_v62.json').read_text()); manifest=json.loads((r/'results/validation_manifest_v7.json').read_text()); pipeline=json.loads((r/'results/pipeline_audit_latest.json').read_text()); align=json.loads((r/'results/main_nersc_source_alignment_v45.json').read_text()); release=json.loads((r/'results/release_audit_latest.json').read_text())
    requirements=[]
    requirements.append({'id':'stage0_protocol','status':'PASS' if manifest.get('status')=='FROZEN' and manifest.get('train_ids')[-1]=='real069' and manifest.get('holdout_ids')[0]=='real070' and manifest.get('github_release_commit') else 'OPEN','evidence':'results/validation_manifest_v7.json'})
    requirements.append({'id':'stage1_unified_loader','status':'PASS' if stage['stages']['1']['status']=='PASS' else 'OPEN','evidence':'results/nbody_unified_current.npz.json'})
    for n in ['2','3','4','5','6','7','8']:
        requirements.append({'id':'stage'+n,'status':'PASS' if stage['stages'][n]['status']=='PASS' else 'OPEN','stage_status':stage['stages'][n]['status'],'evidence':stage['stages'][n].get('evidence',[])})
    requirements += [{'id':'pipeline_artifacts','status':'PASS' if pipeline.get('status')=='PASS' and pipeline.get('present_count')==pipeline.get('required_count') else 'OPEN','evidence':'results/pipeline_audit_latest.json'}, {'id':'source_alignment','status':'PASS' if align.get('status')=='PASS' and not align.get('mismatches') else 'OPEN','evidence':'results/main_nersc_source_alignment_v45.json'}, {'id':'release_artifacts','status':'PASS' if release.get('status')=='PASS' else 'OPEN','evidence':'results/release_audit_latest.json'}]
    out={'schema':'completion_audit_v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'COMPLETE' if all(x['status']=='PASS' for x in requirements) and gate.get('status')=='PASS' else 'INCOMPLETE','requirements':requirements,'release_gate_status':gate.get('status'),'scientific_blockers':gate.get('scientific_blockers',[]),'policy':'A PASS execution audit does not override an OPEN scientific stage; no production claim is made.','scope':'requirement-level audit only; does not alter frozen configuration or fit parameters.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':out['status'],'pass_count':sum(x['status']=='PASS' for x in requirements),'total':len(requirements),'blockers':len(out['scientific_blockers'])}))
if __name__=='__main__': main()
