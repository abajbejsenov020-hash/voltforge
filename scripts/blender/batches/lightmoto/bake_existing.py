"""Bake joined mesh transforms in an existing batch without changing visible geometry.
Build source already does this; use to normalize early files from iterative builds.
Blender -b -t 2 --python .../bake_existing.py
"""
import bpy,os,json
from mathutils import Vector
base=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../..'))
exec(compile(open(os.path.join(os.path.dirname(__file__),'primitives.py')).read(),'primitives.py','exec'))
manifest=os.path.join(base,'apps/web/src/data/blender-lightmoto.json');rows=json.load(open(manifest))
for r in rows:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(base,r['nativeSource']))
 root=bpy.data.objects[r['name']]
 meshes=[o for o in root.children_recursive if o.type=='MESH']
 for o in meshes:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.context.view_layer.update()
 recolored=False
 if r['family'] in {'ultra','storm','hyper'}:
  colors={'Model accent': ((.85,.70,.001) if r['family']!='hyper' else (.80,.001,.19),0,.40),'Bronze fork tubes':((.075,.035,.022),.65,.30)}
  for name,(color,metal,rough) in colors.items():
   material=bpy.data.materials.get(name)
   if material:
    material.diffuse_color=(*color,1);pbr=material.node_tree.nodes.get('Principled BSDF');pbr.inputs['Base Color'].default_value=(*color,1);pbr.inputs['Metallic'].default_value=metal;pbr.inputs['Roughness'].default_value=rough
  bpy.context.scene.view_settings.view_transform='Standard';bpy.context.scene.view_settings.look='None';bpy.context.scene.view_settings.exposure=-1.5
  recolored=True
 modified=project_body_livery(root,r['family'], {'ultra':.145,'storm':.158,'hyper':.095,'sigma':.120,'delta':.119,'omega':.130,'eride4':.125}.get(r['family'],.1), {'ultra':.91,'storm':.94,'hyper':.66,'sigma':.85,'delta':.82,'omega':.89,'eride4':.89}.get(r['family'],.85))
 if modified or recolored:bpy.ops.render.render(write_still=True)
 coords=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
 floor=min(p.z for p in coords)
 assert abs(floor)<.001,(r['key'],floor)
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 out=os.path.join(base,'apps/web/public'+r['url'])
 bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True)
 r['bytes']=os.path.getsize(out)
 r['triangles']=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes);r['meshes']=len(meshes)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=os.path.join(base,r['nativeSource']),compress=True)
 proofpath=os.path.join(base,'artifacts/blender/catalog/lightmoto/'+r['key']+'.json')
 proof=json.load(open(proofpath));proof['bytes']=r['bytes'];proof['triangles']=r['triangles'];proof['meshes']=r['meshes'];proof['joinedTransformsBaked']=True
 proof['dimensions_m']=[round(max(p[i] for p in coords)-min(p[i] for p in coords),4) for i in range(3)]
 json.dump(proof,open(proofpath,'w'),indent=2)
 print('TRANSFORMS_BAKED',r['key'],r['bytes'],flush=True)
json.dump(rows,open(manifest,'w'),indent=2)
