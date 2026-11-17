"""Open each completed .blend and check packed exact photos, geometry, axes and transforms."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';rs=json.load(open(A/'references.json'));reportPath=A/'native-audit.json';old=json.load(open(reportPath)) if reportPath.exists() else {};cached={x['key']:x for x in old.get('checks',[])};checks=[];pending=[];fail=[]
for e in rs:
 key=e['key'];mp=A/(key+'.json');fp=ROOT/'assets/blender/expansion/premium'/(key+'.blend')
 if not mp.exists() or json.load(open(mp)).get('revision')!=2:pending.append(key);continue
 st=fp.stat();previous=cached.get(key)
 if previous and previous['mtimeNs']==st.st_mtime_ns and previous['bytes']==st.st_size:checks.append(previous);continue
 try:
  bpy.ops.wm.open_mainfile(filepath=str(fp),load_ui=False);root=bpy.data.objects.get(e['name']);assert root and root.get('reconstructionRevision')==2
  assert root.get('source')==e['source'],(key,'source mismatch');assert root.get('reference')==e['image']
  refName=Path(e['image']).name;packed=[im for im in bpy.data.images if im.packed_file and im.name==refName];assert len(packed)==1,(key,refName);assert packed[0].packed_file.size==e['bytes']
  obs=[]
  for name in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
   group=bpy.data.objects.get(name);assert group and any(o.type=='MESH' and len(o.data.vertices)>0 for o in group.children_recursive),(key,name)
  for o in root.children_recursive:
   if o.type!='MESH':continue
   obs.append(o);assert all(abs(x-1)<1e-6 for x in o.scale);assert all(abs(x)<1e-6 for x in o.rotation_euler)
   assert all(math.isfinite(v) for vert in o.data.vertices for v in vert.co)
  bounds=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box];lo=[min(v[i] for v in bounds) for i in range(3)];hi=[max(v[i] for v in bounds) for i in range(3)];assert lo[2]>=-.003
  f=bpy.data.objects['FrontWheel'];rear=bpy.data.objects['RearWheel']
  fx=[(o.matrix_world@v.co).x for o in f.children_recursive if o.type=='MESH' for v in o.data.vertices];rx=[(o.matrix_world@v.co).x for o in rear.children_recursive if o.type=='MESH' for v in o.data.vertices];assert sum(fx)/len(fx)>0 and sum(rx)/len(rx)<0
  assert bpy.context.scene.unit_settings.system=='METRIC';assert bpy.context.scene.render.resolution_x==640 and bpy.context.scene.render.resolution_y==640
  checks.append(dict(key=key,bytes=st.st_size,mtimeNs=st.st_mtime_ns,packedPhotoBytes=packed[0].packed_file.size,meshes=len(obs),bounds=[lo,hi],passed=True));print('NATIVE_OK',key,flush=True)
 except Exception as err:fail.append(dict(key=key,error=str(err)))
report=dict(checked=len(checks),total=len(rs),pending=pending,failures=fail,checks=checks);json.dump(report,open(reportPath,'w'),indent=2);print('NATIVE_AUDIT_RESULT',len(checks),len(pending),fail,flush=True)
