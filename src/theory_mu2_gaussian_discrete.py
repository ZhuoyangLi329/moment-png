#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from exact_window import mu2_gaussian_discrete

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('input',type=Path); ap.add_argument('--b1',type=float,required=True); ap.add_argument('--pshot',type=float,required=True); ap.add_argument('--nmesh',type=int,required=True); ap.add_argument('--box',type=float,default=1000.); ap.add_argument('--width',type=float,default=20.); ap.add_argument('--power-convention',choices=['mesh','continuum_cic_no_alias'],default='mesh'); ap.add_argument('--shells',default='40,60,80,100,120,140,160,180,200,220,240,260,280,300'); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); d=np.load(a.input); kv=np.asarray(d['kvecs']); pm=np.asarray(d['Pm']); ph=a.b1*a.b1*pm+a.pshot; ss=[float(x) for x in a.shells.split(',')]; preds=[]; meta=[]
 for s in ss:
  y,m=mu2_gaussian_discrete(kv,ph,s,width=a.width,boxsize=a.box,cell=a.box/a.nmesh,nmesh=a.nmesh,power_convention=a.power_convention); preds.append(float(y)); meta.append(m)
 out={'status':'PASS','schema':'mu2_gaussian_discrete_prediction_v1','b1':a.b1,'P_shot':a.pshot,'nmesh':a.nmesh,'power_convention':a.power_convention,'boxsize':a.box,'shell_width':a.width,'s':ss,'predictions':[{'s':s,'mu2_gaussian':y} for s,y in zip(ss,preds)],'mode_metadata':meta,'scope':'exact discrete lattice Gaussian Wick projection; no connected/contact terms'}; a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'status':'PASS','n_shells':len(ss),'first':preds[0]}))
if __name__=='__main__': main()
