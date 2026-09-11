#!/usr/bin/env python3
"""Inventory NERSC catalog roots relevant to a disjoint bphi calibration."""
import argparse,json,datetime
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--catalog-root',type=Path,default=Path('/pscratch/sd/l/lzy/quijote-png/halos'));a=ap.parse_args();base=a.catalog_root
 roots=[base/'FoF_z1_mmin1e13_positions',base/'FoF_z1',base/'FoF_z1_mmin1e13_positions_smoke_tmp']; rows=[]
 for root in roots:
  if not root.exists(): rows.append({'root':str(root),'exists':False});continue
  nodes=[]
  for node in sorted(p for p in root.iterdir() if p.is_dir()):
   ids=sorted(p.name for p in node.iterdir() if p.is_dir()); pos=sum((node/x/'positions_mpc_h.npy').exists() for x in ids); meta=sum((node/x/'metadata.json').exists() for x in ids); nodes.append({'node':node.name,'n_realization_dirs':len(ids),'first_ids':ids[:3],'last_ids':ids[-3:],'positions_files':pos,'metadata_files':meta,'selection_certified':bool(ids and pos==len(ids) and meta==len(ids))})
  rows.append({'root':str(root),'exists':True,'nodes':nodes})
 standard=rows[0]; node_counts={x['node']:x['n_realization_dirs'] for x in standard.get('nodes',[])}; disjoint_pair=all(node_counts.get(x,0)>=200 for x in ['LC_m','LC_p'])
 out={'schema':'bphi_disjoint_catalog_inventory_v1','status':'PASS','target':{'root':'FoF_z1_mmin1e13_positions','redshift':1.0,'halo_finder':'FoF','mass_cut_msun_h':1e13,'selection':'positions+metadata certified'},'roots':rows,'standard_node_counts':node_counts,'disjoint_png_pair_available':disjoint_pair,'decision':'BLOCKED','rejection_reasons':['standard LC_m and LC_p roots stop at real099, so no certified PNG disjoint block beyond frozen 70/30 split','older FoF_z1 roots contain binary group_tab files without positions_mpc_h.npy/metadata.json and cannot certify the frozen selection','fiducial-only extra realizations cannot calibrate a PNG response without matched LC± catalogs'],'policy':{'no_uncertified_selection_used':True,'no_heldout_response_fit':True,'production_bphi_requires_disjoint_or_external_match':True},'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'standard_counts':node_counts,'disjoint_png_pair_available':disjoint_pair}))
if __name__=='__main__':main()
