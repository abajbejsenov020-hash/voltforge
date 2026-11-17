"""Validate native/export/proof presence and publish only verified structural exports."""
import json,struct,math,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';PUBLIC=ROOT/'apps/web/public';M=ROOT/'apps/web/src/data/vehicle-expansion-premium.json'
rs=json.load(open(A/'references.json'));assigned=json.load(open(A/'assigned.json'));names=[e['name'] for e in rs];assert len(names)==len(set(names));assert set(names)<=set(e['name'] for e in assigned)
ready=[];pending=[];fail=[]
for e in rs:
 key=e['key'];note=A/(key+'.json');glb=PUBLIC/'models/expansion/premium'/(key+'.glb');native=ROOT/'assets/blender/expansion/premium'/(key+'.blend');proof=A/(key+'.png')
 if not all(p.exists() for p in [note,glb,native,proof]):pending.append(e['name']);continue
 try:
  meta=json.load(open(note));
  if meta.get('revision')!=2:pending.append(e['name']);continue
  raw=glb.read_bytes();magic,version,total=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and total==len(raw)
  size,typ=struct.unpack_from('<II',raw,12);assert typ==0x4e4f534a;g=json.loads(raw[20:20+size]);assert not g.get('cameras');assert 'KHR_lights_punctual' not in g.get('extensionsUsed',[])
  nodes=g['nodes'];groups={n['name']:n for n in nodes if 'name' in n}
  def contains_mesh(n):return 'mesh' in n or any(contains_mesh(nodes[i]) for i in n.get('children',[]))
  for n in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:assert n in groups and contains_mesh(groups[n]),(key,n)
  tris=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tris<90000;assert len(g['meshes'])<55;assert len(raw)<5000000
  assert tris==meta['model']['triangles'],(key,tris,meta['model']['triangles'])
  for accessor in g['accessors']:
   for v in accessor.get('min',[])+accessor.get('max',[]):assert math.isfinite(v)
  for n in nodes:
   assert n.get('scale',[1,1,1])==[1,1,1],(key,n.get('name'),'scale')
  assert native.stat().st_size>100000;assert Image.open(proof).size==(640,640)
  image=PUBLIC/e['image'].lstrip('/');im=Image.open(image);assert list(im.size)==e['dimensions'];assert image.stat().st_size==e['bytes']
  lo,hi=meta['bounds'];assert lo[2]>=-.003 and all(math.isfinite(v) for v in lo+hi)
  out={k:e[k] for k in ['name','type','subtype','image','source','imageSource','credit','variantNote','license','dimensions','bytes','referenceKind']};out['model']=meta['model'];out['variantNote']=(out['variantNote']+' '+meta['observed']+' Photo-guided exterior reconstruction; hidden/internal geometry inferred, not measured CAD.').strip();ready.append(out)
 except Exception as err:fail.append([e['name'],str(err)])
unresolved=[]
for e in assigned:
 if e['name'] in names:continue
 unresolved.append(dict(name=e['name'],type=e['type'],reason='Manufacturer sources identify base and Pro as different motor configurations, but only Pro-specific or combined-family whole-vehicle photos were found. Exact base-model preview/appearance is withheld rather than borrowing Pro body/motor details.',sources=['https://www.hiley-mobility.com/tiger-9-electric-scooters/62829289.html','https://www.hileyrider.com/products/hiley-tiger-t8-pro-dual-motor-electric-scooter' if '8' in e['name'] else 'https://www.hileyrider.com/products/hiley-tiger-t9-pro-dual-motor-electric-scooter','https://bsg-i.nbxc.com/upload/1512/131/pdf/24d0b779964bb7d9628ee792e4.pdf']))
# Do not publish incomplete exports; pending remains in audit status rather than posing as an identity failure.
report=dict(assigned=len(assigned),references=len(rs),ready=len(ready),pending=pending,failures=fail,unresolved=unresolved,maxTriangles=max([e['model']['triangles'] for e in ready],default=0),maxMeshes=max([e['model']['meshes'] for e in ready],default=0),maxGLBBytes=max([e['model']['bytes'] for e in ready],default=0));json.dump(report,open(A/'audit.json','w'),indent=2)
if '--publish' in sys.argv:
 assert not pending and not fail,report;assert len(ready)+len(unresolved)==len(assigned)
 nativeAudit=json.load(open(A/'native-audit.json'));assert nativeAudit['checked']==len(rs) and not nativeAudit['pending'] and not nativeAudit['failures'];nativeChecks={e['key']:e for e in nativeAudit['checks']}
 for e in rs:
  check=nativeChecks[e['key']];assert check['mtimeNs']==(ROOT/'assets/blender/expansion/premium'/(e['key']+'.blend')).stat().st_mtime_ns;assert check['packedPhotoBytes']==e['bytes']
 json.dump(dict(entries=ready,unresolved=unresolved),open(M,'w'),indent=2)
# Compact side-by-side photo/render comparison sheets for visual audit.
for page in range((len(ready)+11)//12):
 sheet=Image.new('RGB',(1440,1080),'#edf0f2');d=ImageDraw.Draw(sheet)
 for i,e in enumerate(ready[page*12:(page+1)*12]):
  x=(i%3)*480;y=(i//3)*270
  for j,path in enumerate([PUBLIC/e['image'].lstrip('/'),A/(e['model']['key']+'.png')]):
   im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);im=bg.convert('RGB');im.thumbnail((235,232));sheet.paste(im,(x+j*240+(235-im.width)//2,y+(232-im.height)//2))
  d.text((x+4,y+239),e['name'],fill='black')
 sheet.save(A/f'comparison-{page+1:02}.jpg',quality=92)
print(json.dumps({k:v for k,v in report.items() if k not in ['pending','unresolved']},indent=2));print('PENDING',pending)
