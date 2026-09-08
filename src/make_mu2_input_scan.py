import json
from pathlib import Path
variants={'baseline_b1_2p734_pshot0':'results/mu2_gaussian_discrete_base_validation.json','baseline_b1_2p734_pshot3603':'results/mu2_gaussian_discrete_base_shot_validation.json','fit_b1_2p781_pshot0':'results/mu2_gaussian_discrete_fit_noshot_validation.json'}
out={'schema':'mu2_gaussian_input_scan_v1','variants':{},'scope':'predeclared mesh Gaussian mu2 convention scan; no parameter fitting','policy':{'heldout_response_fit':False,'production_promotion':False}}
for k,p in variants.items():
 d=json.load(open(p)); out['variants'][k]={'prediction':p,'nodes':{n:{'rms_pull':v['rms_pull'],'chi2_dof':v['chi2_dof'],'coverage':v['coverage_fraction_abs_pull_le_2']} for n,v in d['nodes'].items()}}
Path('results/mu2_gaussian_input_scan_v1.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
