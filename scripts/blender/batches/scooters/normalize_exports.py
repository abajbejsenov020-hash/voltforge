"""Normalize consolidated mesh transforms in existing generated assets, preserving shape.
One-time migration / reproducible regression check for loose transformed local AABBs.
"""
import bpy,json,sys,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];M=ROOT/'apps/web/src/data/blender-scooters.json';P=ROOT/'artifacts/blender/catalog/scooters'
manifest=json.load(open(M));keys=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [e['key'] for e in manifest]
for key in keys:
 entry=next(e for e in manifest if e['key']==key);blend=ROOT/entry['nativeSource'];bpy.ops.wm.open_mainfile(filepath=str(blend));bpy.context.preferences.filepaths.save_version=0
 root=bpy.data.objects[entry['name']];descendants=list(root.children_recursive);models=[o for o in descendants if o.type=='MESH']
 actualmin=min((o.matrix_world@v.co).z for o in models for v in o.data.vertices)
 for o in models:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.context.view_layer.update();boxmin=min((o.matrix_world@Vector(c)).z for o in models for c in o.bound_box)
 assert abs(actualmin-boxmin)<.00001,(key,actualmin,boxmin)
 assert boxmin>=-.001,(key,boxmin)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in descendants:o.select_set(True)
 out=ROOT/'apps/web/public'/entry['url'].lstrip('/');bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
 entry['bytes']=out.stat().st_size;note=json.load(open(P/(key+'.json')));note.update(bytes=entry['bytes'],blendBytes=blend.stat().st_size,minHeight=actualmin,boundsNormalized=True);json.dump(note,open(P/(key+'.json'),'w'),indent=2);print('NORMALIZED',key,round(actualmin,6),flush=True)
json.dump(manifest,open(M,'w'),indent=2)
