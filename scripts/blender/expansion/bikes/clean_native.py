"""Keep only each model's own freshly packed source photograph in its native file."""
import bpy,json,pathlib,re,sys
BASE=pathlib.Path(__file__).resolve().parents[4];OUT=BASE/'artifacts/blender/expansion/bikes';refs=json.load(open(OUT/'ready-references.json'));result=[]
chosen=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for r in refs:
 key=re.sub('[^a-z0-9]+','-',r['name'].lower().replace('+','-plus')).strip('-')
 if chosen and key not in chosen:continue
 path=BASE/'assets/blender/expansion/bikes'/(key+'.blend')
 if not path.exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(path))
 for img in list(bpy.data.images):
  if img.type not in ['RENDER_RESULT','COMPOSITING']:bpy.data.images.remove(img,do_unlink=True)
 ref=bpy.data.images.load(str(BASE/('apps/web/public'+r['image'])),check_existing=False);ref.use_fake_user=True;ref.pack()
 for datablocks in [bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights,bpy.data.worlds]:
  for d in list(datablocks):
   if d.users==0:datablocks.remove(d)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 imagecount=len([i for i in bpy.data.images if i.packed_file]);assert imagecount==1
 result.append({'name':r['name'],'packedImageCount':imagecount,'nativeBytes':path.stat().st_size});print('NATIVE_CHECKED',key,imagecount,flush=True)
previous=json.load(open(OUT/'native-audit.json')) if (OUT/'native-audit.json').exists() else [];merged={x['name']:x for x in previous};merged.update({x['name']:x for x in result});json.dump(list(merged.values()),open(OUT/'native-audit.json','w'),indent=2)
