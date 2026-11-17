"""Blender native-file validation. Run after build.py with Blender background."""
import bpy,json,os
from mathutils import Vector
base=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../..'))
rows=json.load(open(os.path.join(base,'apps/web/src/data/blender-lightmoto.json')))
proof=[]
for r in rows:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(base,r['nativeSource']))
 root=bpy.data.objects.get(r['name']);assert root is not None
 nodes={o.name for o in root.children}
 assert {'FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount'}<=nodes
 for required in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  descendant=[o for o in bpy.data.objects[required].children_recursive if o.type=='MESH']
  assert descendant and sum(len(o.data.vertices) for o in descendant)>0,(r['name'],required,'empty mount')
 refs=[im for im in bpy.data.images if im.packed_file]
 assert len(refs)==1,(r['name'],'packed photos',len(refs))
 assert refs[0].name==os.path.basename(r['image'])
 assert not any(m.users==0 for m in bpy.data.meshes),(r['name'],'unused meshes')
 assert tuple(root.location)==(0,0,0)
 coords=[o.matrix_world @ Vector(c) for o in root.children_recursive if o.type=='MESH' for c in o.bound_box]
 floor=min(v.z for v in coords);assert abs(floor)<.00001,(r['name'],floor)
 assert bpy.data.objects['FrontWheel'].location.x>bpy.data.objects['RearWheel'].location.x
 scene=bpy.context.scene;assert scene.render.resolution_x==640 and scene.render.resolution_y==640 and scene.cycles.samples==32
 proof.append(dict(key=r['key'],packed_reference=refs[0].name,floor_m=round(floor,7),unused_meshes=0,native_bytes=os.path.getsize(os.path.join(base,r['nativeSource']))))
json.dump(proof,open(os.path.join(base,'artifacts/blender/catalog/lightmoto/native-validation.json'),'w'),indent=2)
print('NATIVE_VALIDATED',len(proof))
