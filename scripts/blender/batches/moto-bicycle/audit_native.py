"""Open all native files, ensure metric display and verify packed references/editability."""
import bpy,json,os
BASE=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../..'))
rows=json.load(open(os.path.join(BASE,'apps/web/src/data/blender-moto-bicycle.json')));proof=[]
for row in rows:
 p=os.path.join(BASE,row['nativeSource']);bpy.ops.wm.open_mainfile(filepath=p)
 root=bpy.data.objects.get(row['key']);assert root and root.get('units')=='metres'
 obs=[o for o in root.children_recursive if o.type=='MESH'];assert len(obs)==row['meshes']
 for n in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:assert bpy.data.objects.get(n)
 ref=bpy.data.images.get(os.path.basename(row['image']));changed=not ref or not ref.packed_file or not ref.use_fake_user
 if not ref:ref=bpy.data.images.load(os.path.join(BASE,'apps/web/public'+row['image']),check_existing=True)
 ref.use_fake_user=True
 if not ref.packed_file:ref.pack()
 scene=bpy.context.scene;assert scene.render.resolution_x==640 and scene.render.resolution_y==640 and scene.cycles.samples==32
 if changed or scene.unit_settings.system!='METRIC' or scene.unit_settings.scale_length!=1:
  scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=p)
 bpy.ops.wm.open_mainfile(filepath=p)
 ref=bpy.data.images.get(os.path.basename(row['image']));assert ref and ref.packed_file and ref.use_fake_user
 proof.append(dict(key=row['key'],editableMeshes=len(obs),packedReference=ref.name,metric=True,render640=True,samples=32))
json.dump(dict(count=len(proof),results=proof),open(os.path.join(BASE,'artifacts/blender/catalog/moto-bicycle/native-coverage.json'),'w'),indent=2)
print('NATIVE_AUDIT_PASSED',len(proof))
