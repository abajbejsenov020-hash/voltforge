"""Independent GLB structure, geometry budget, provenance and coverage audit."""
import json,struct,math,pathlib,collections
BASE=pathlib.Path(__file__).resolve().parents[4];OUT=BASE/'artifacts/blender/expansion/bikes'
refs=json.load(open(OUT/'ready-references.json'));assigned=json.load(open(OUT/'assigned.json'));issues=[];entries=[]
for ref in refs:
 import re
 key=re.sub('[^a-z0-9]+','-',ref['name'].lower().replace('+','-plus')).strip('-');ep=OUT/(key+'-entry.json');vp=OUT/(key+'-validation.json')
 if not ep.exists() or not vp.exists():issues.append((ref['name'],'missing export proof'));continue
 e=json.load(open(ep));proof=json.load(open(vp));model=e['model'];path=BASE/('apps/web/public'+model['url']);b=path.read_bytes()
 assert b[:4]==b'glTF';size,kind=struct.unpack_from('<I4s',b,12);g=json.loads(b[20:20+size]);nodes=g['nodes'];meshes=g['meshes'];tri=0
 for mesh in meshes:
  for primitive in mesh['primitives']:
   acc=g['accessors'][primitive['attributes']['POSITION']];assert all(math.isfinite(x) for x in acc['min']+acc['max'])
   tri+=g['accessors'][primitive['indices']]['count']//3
 def hasmesh(i):return 'mesh' in nodes[i] or any(hasmesh(k) for k in nodes[i].get('children',[]))
 for name in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  indexes=[i for i,n in enumerate(nodes) if n.get('name')==name]
  if not indexes or not hasmesh(indexes[0]):issues.append((ref['name'],'empty/missing semantic node '+name))
 if len(b)>=5_000_000 or tri>=100_000 or len(meshes)>=55:issues.append((ref['name'],'budget exceeded',len(b),tri,len(meshes)))
 if any(any(s in n.get('name','').lower() for s in ['studio','camera','softbox','floor']) for n in nodes):issues.append((ref['name'],'studio in GLB'))
 if any(abs(x)>1e-7 for x in [proof['floor_min_z']]):issues.append((ref['name'],'not grounded'))
 if not (BASE/model['nativeSource']).exists() or not (OUT/(key+'.png')).exists():issues.append((ref['name'],'missing native/render'))
 # Fresh reference metadata wins after a reviewed photograph replacement.
 e={**ref,'model':{**model,'triangles':tri,'meshes':len(meshes),'bytes':len(b)}}
 if ref['name'] in ['Trek Marlin','Giant Talon','Specialized Rockhopper']:e['variantNote']+=' Nonmotorized pedal reference. BatteryMount/ControllerMount/MotorMount are viewer service anchors for bottle bosses, cable junction and crank bearing; no electric components are asserted.'
 e['variantNote']+=' Photo-based approximate exterior; no manufacturer CAD or fitment claim.'
 entries.append(e)
missing=sorted(set(x['name'] for x in assigned)-set(x['name'] for x in entries));dupes=[n for n,c in collections.Counter(e['name'] for e in entries).items() if c>1]
audit={'assigned':len(assigned),'completed':len(entries),'missing':missing,'duplicateNames':dupes,'issues':issues,'maxGlbBytes':max((e['model']['bytes'] for e in entries),default=0),'maxTriangles':max((e['model']['triangles'] for e in entries),default=0),'maxMeshes':max((e['model']['meshes'] for e in entries),default=0)}
json.dump(audit,open(OUT/'audit.json','w'),indent=2);print(json.dumps(audit,indent=2))
if not missing and not issues and not dupes:
 import os
 target=BASE/'apps/web/src/data/vehicle-expansion-bikes.json';tmp=target.with_suffix('.json.tmp');json.dump({'entries':entries,'unresolved':[]},open(tmp,'w'),indent=2);os.replace(tmp,target)
