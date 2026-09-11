#!/usr/bin/env python3
"""Inventory reconstructed disjoint LC-/LC+ catalogs for Stage 6."""
import argparse, datetime, hashlib, json
from pathlib import Path

def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def inventory_node(root,node):
 ids=sorted(p.name for p in (root/node).iterdir() if p.is_dir()) if (root/node).exists() else []
 rows=[]
 for rid in ids:
  d=root/node/rid; pos=d/'positions_mpc_h.npy'; mass=d/'masses_msun_h.npy'; meta=d/'metadata.json'; md={}
  if meta.exists():
   try: md=json.loads(meta.read_text())
   except Exception: md={}
  dtype_ok=False
  try: dtype_ok=(np.load(pos,mmap_mode='r').dtype==np.float32 and np.load(mass,mmap_mode='r').dtype==np.float32)
  except Exception: dtype_ok=False
  rows.append({'realization':rid,'positions':pos.exists(),'masses':mass.exists(),'metadata':meta.exists(),'metadata_sha256':sha(meta) if meta.exists() else None,'selection_certified':bool(pos.exists() and mass.exists() and meta.exists() and dtype_ok and md.get('mass_threshold_msun_h')==1e13 and md.get('snapnum')==2 and md.get('redshift')==1.0 and md.get('boxsize_mpc_h')==1000.0)})
 return {'node':node,'n_realization_dirs':len(ids),'first_ids':ids[:3],'last_ids':ids[-3:],'positions_files':sum(x['positions'] for x in rows),'masses_files':sum(x['masses'] for x in rows),'metadata_files':sum(x['metadata'] for x in rows),'certified_files':sum(x['selection_certified'] for x in rows),'selection_certified':bool(rows and all(x['selection_certified'] for x in rows)),'rows':rows}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--catalog-root',type=Path,default=Path('/pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions'));a=ap.parse_args(); nodes=[inventory_node(a.catalog_root,n) for n in ('fiducial','LC_m','LC_p')]; counts={x['node']:x['n_realization_dirs'] for x in nodes}; cert={x['node']:x['selection_certified'] for x in nodes}; pair=all(counts.get(n,0)>=500 and cert.get(n,False) for n in ('LC_m','LC_p')); out={'schema':'bphi_disjoint_catalog_inventory_v2','status':'PASS','catalog_root':str(a.catalog_root),'target':{'redshift':1.0,'halo_finder':'FoF','mass_cut_msun_h':1e13,'boxsize_mpc_h':1000.0,'position_dtype':'float32','snapnum':2},'nodes':nodes,'standard_node_counts':counts,'disjoint_png_pair_available':pair,'decision':'AVAILABLE_FOR_CALIBRATION' if pair else 'BLOCKED','rejection_reasons':[] if pair else ['both LC_m and LC_p require at least 500 certified realizations','metadata must certify frozen FoF selection and z=1 snapshot'],'policy':{'frozen_training_ids':'real000-real069','frozen_heldout_ids':'real070-real099','calibration_ids':'real100-real499','no_heldout_response_fit':True,'production_bphi_requires_disjoint_or_external_match':True},'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'pair':pair,'counts':counts,'decision':out['decision']}))
if __name__=='__main__':main()
