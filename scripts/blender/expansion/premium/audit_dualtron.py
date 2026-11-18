"""Independent native reopens and exported-resource checks for the 23 refined Dualtrons."""
import bpy,json,struct,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';PUBLIC=ROOT/'apps/web/public';rs=[e for e in json.load(open(A/'references.json')) if e['name'].startswith('Dualtron')];checks=[];fail=[]
if '--gate' in sys.argv:rs=[e for e in rs if e['name'] in ['Dualtron Thunder 3','Dualtron Spider','Dualtron Mini','Dualtron X2']]
for e in rs:
 try:
  key=e['key'];native=ROOT/'assets/blender/expansion/premium'/(key+'.blend');glb=PUBLIC/'models/expansion/premium'/(key+'.glb');photo=PUBLIC/e['image'].lstrip('/');meta=json.load(open(A/(key+'.json')))
  bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False);root=bpy.data.objects[e['name']];assert root['dualtronRefinement']==1;assert root['source']==e['source'] and root['reference']==e['image']
  packed=next(i for i in bpy.data.images if i.name==photo.name and i.packed_file);assert bytes(packed.packed_file.data)==photo.read_bytes()
  if e['name']=='Dualtron Thunder 3':
   detailed=next(i for i in bpy.data.images if i.name=='dualtron-thunder-3-deck-reference.jpg' and i.packed_file);assert bytes(detailed.packed_file.data)==(A/'dualtron-thunder-3-deck-reference.jpg').read_bytes()
  images=[i for i in bpy.data.images if i.name.endswith('-grip.png') or i.name.startswith('ey4-screen.png')];assert images and all(i.packed_file for i in images)
  for im in images:
   filename=im.name.split('.png')[0]+'.png';assert bytes(im.packed_file.data)==(PUBLIC/'assets/vehicles/expansion/premium/dualtron-details'/filename).read_bytes()
  for n in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:assert any(o.type=='MESH' and len(o.data.vertices) for o in bpy.data.objects[n].children_recursive)
  model=[o for o in root.children_recursive if o.type=='MESH'];bounds=[o.matrix_world@Vector(v) for o in model for v in o.bound_box];lo=[min(v[i] for v in bounds) for i in range(3)];hi=[max(v[i] for v in bounds) for i in range(3)];assert lo[2]>=-.003 and all(math.isfinite(x) for x in lo+hi)
  for o in model:assert all(abs(v-1)<1e-6 for v in o.scale) and all(abs(v)<1e-6 for v in o.rotation_euler)
  raw=glb.read_bytes();magic,ver,total=struct.unpack_from('<III',raw);assert (magic,ver,total)==(0x46546c67,2,len(raw));jsize=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jsize]);assert not g.get('cameras') and 'KHR_lights_punctual' not in g.get('extensionsUsed',[]);assert all('uri' not in b for b in g['buffers']);assert all('bufferView' in i and 'uri' not in i for i in g.get('images',[]));assert not any('STUDIO' in n.get('name','') or 'REFERENCE' in n.get('name','') for n in g['nodes'])
  tris=sum(g['accessors'][pr['indices']]['count']//3 for m in g['meshes'] for pr in m['primitives']);assert tris==meta['model']['triangles'] and tris<90000;assert len(g['meshes'])<55 and len(raw)<5000000;assert len(g.get('images',[])) in [1,2]
  textureMats=[m for m in g['materials'] if m.get('pbrMetallicRoughness',{}).get('baseColorTexture')];assert any('printed rubber' in m.get('name','') for m in textureMats)
  # Re-import the published binary into a clean scene to catch exporter-only defects.
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));rr=bpy.data.objects[e['name']];assert rr['dualtronRefinement']==1;assert any(o.type=='MESH' for o in rr.children_recursive)
  imported=[o for o in rr.children_recursive if o.type=='MESH'];bb=[o.matrix_world@Vector(v) for o in imported for v in o.bound_box];ilo=[min(v[i] for v in bb) for i in range(3)];ihi=[max(v[i] for v in bb) for i in range(3)];assert max(abs(a-b) for a,b in zip(lo+hi,ilo+ihi))<.0001,(key,lo,ilo,hi,ihi)
  checks.append(dict(name=e['name'],key=key,triangles=tris,meshes=len(g['meshes']),materials=len(g['materials']),embeddedTextures=len(g['images']),bytes=len(raw),nativePackedSourceSHA256=hashlib.sha256(photo.read_bytes()).hexdigest(),glbSHA256=hashlib.sha256(raw).hexdigest(),bounds=[lo,hi],reopenedNative=True,reimportedGLB=True,passed=True));print('DUALTRON_AUDIT_OK',key,flush=True)
 except Exception as err:fail.append(dict(name=e['name'],error=str(err)));print('DUALTRON_AUDIT_FAIL',e['name'],str(err),flush=True)
untouched=json.load(open(A/'dualtron-untouched-baseline.json'));changes=[p for p,h in untouched.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h];report=dict(assigned=len(rs),checked=len(checks),failures=fail,unrelatedChanged=changes,checks=checks);(A/('dualtron-gate-audit.json' if '--gate' in sys.argv else 'dualtron-refinement-audit.json')).write_text(json.dumps(report,indent=2)+'\n');print('DUALTRON_AUDIT_RESULT',len(checks),fail,'UNRELATED_CHANGED',changes,flush=True)
