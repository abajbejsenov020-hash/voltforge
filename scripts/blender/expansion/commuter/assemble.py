from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];O=R/'artifacts/blender/expansion/commuter';selected=json.load(open(O/'selected.json'));entries=[];pending=[]
for e in selected:
 f=O/(e['key']+'.json')
 if not f.exists():pending.append(e['name']);continue
 n=json.load(open(f));m={k:n[k] for k in ['key','url','nativeSource','triangles','meshes','bytes','family']}
 if not (R/'apps/web/public'/m['url'].lstrip('/')).exists() or not (R/m['nativeSource']).exists() or not (O/(e['key']+'.png')).exists():pending.append(e['name']);continue
 ent={k:v for k,v in e.items() if k not in ['key','productTitle']};ent['model']=m;entries.append(ent)
res={'entries':entries,'unresolved':json.load(open(O/'unresolved-audit.json'))};target=R/'apps/web/src/data/vehicle-expansion-commuter.json';temp=target.with_suffix('.tmp');temp.write_text(json.dumps(res,indent=2));temp.replace(target);print('Ready',len(entries),'audited',len(res['unresolved']),'export pending',pending)
