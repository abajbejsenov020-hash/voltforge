import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';keys=set(json.load(open(A/'alpha-reference-updates.json')))
for e in json.load(open(A/'references.json')):
 if e['key'] not in keys:continue
 path=ROOT/'assets/blender/expansion/premium'/(e['key']+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);ref=bpy.data.objects.get('REFERENCE exact product photograph');assert ref
 old=ref.data;ref.data=None;bpy.data.images.remove(old);im=bpy.data.images.load(str(ROOT/'apps/web/public'/e['image'].lstrip('/')));im.pack();ref.data=im;assert im.packed_file.size==e['bytes'];bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);print('REPACK_ALPHA_OK',e['key'],flush=True)
