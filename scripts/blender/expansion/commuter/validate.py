"""Load each final native file and GLB and independently check export contract."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];O=R/'artifacts/blender/expansion/commuter';rows=json.load(open(O/'selected.json'));required=['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount'];results=[]
def descendant_meshes(obj):
 out=[]
 for ch in obj.children:
  if ch.type=='MESH':out.append(ch)
  out.extend(descendant_meshes(ch))
 return out
for e in rows:
 key=e['key'];note=json.load(open(O/(key+'.json')));blend=R/note['nativeSource'];glb=R/'apps/web/public'/note['url'].lstrip('/')
 bpy.ops.wm.open_mainfile(filepath=str(blend));native=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('STUDIO')];packed=[i for i in bpy.data.images if i.packed_file]
 assert len(packed)>=1,(key,'missing packed reference');assert bpy.context.scene.unit_settings.system=='METRIC',(key,'units')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));objects=list(bpy.context.scene.objects);meshes=[o for o in objects if o.type=='MESH'];assert meshes,(key,'empty')
 assert not [o.name for o in objects if o.name.startswith('STUDIO') or o.type in ['LIGHT','CAMERA']],(key,'studio leak')
 group_counts={}
 for name in required:
  g=next((o for o in objects if o.name==name),None);assert g,(key,'missing group '+name);children=descendant_meshes(g);assert children,(key,'empty group '+name);group_counts[name]=len(children)
 bpy.context.view_layer.update();bounds=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];mins=[min(v[i] for v in bounds) for i in range(3)];maxs=[max(v[i] for v in bounds) for i in range(3)]
 # Blender importer converts glTF Y-up back into the Z-up authoring coordinate system.
 assert -.006<=mins[2]<.025,(key,'floor',mins);assert maxs[0]-mins[0]>.75 and maxs[2]-mins[2]>.9,(key,'dimensions',mins,maxs)
 tri=0
 for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 assert glb.stat().st_size==note['bytes'],(key,'stale byte count');assert tri==note['triangles'],(key,'triangle mismatch',tri,note['triangles']);assert len(meshes)==note['meshes'],(key,'mesh mismatch');assert tri<120000 and len(meshes)<65 and glb.stat().st_size<5000000,(key,'budget')
 results.append({'name':e['name'],'key':key,'triangles':tri,'meshes':len(meshes),'bytes':glb.stat().st_size,'packedReferences':len(packed),'nativeMeshCount':len(native),'boundsMin':mins,'boundsMax':maxs,'requiredGroups':group_counts,'passed':True});print('CHECKED',key,flush=True)
json.dump({'count':len(results),'allPassed':True,'checks':results},open(O/'verification.json','w'),indent=2);print('COMMUTER_VALIDATED',len(results),flush=True)
