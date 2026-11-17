"""Read-only native proofs, including exact packed-image byte identity."""
import bpy,pathlib,json,re,hashlib,math
BASE=pathlib.Path(__file__).resolve().parents[4];OUT=BASE/'artifacts/blender/expansion/bikes';refs=json.load(open(OUT/'ready-references.json'));result=[]
for r in refs:
 k=re.sub('[^a-z0-9]+','-',r['name'].lower().replace('+','-plus')).strip('-');p=BASE/'assets/blender/expansion/bikes'/(k+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p));packed=[im for im in bpy.data.images if im.packed_file];assert len(packed)==1,(r['name'],'packed count',len(packed));want=(BASE/('apps/web/public'+r['image'])).read_bytes();got=packed[0].packed_file.data;assert hashlib.sha256(want).digest()==hashlib.sha256(got).digest(),(r['name'],'packed reference mismatch')
 root=bpy.data.objects.get(r['name']);assert root is not None,(r['name'],'root missing');meshes=[o for o in root.children_recursive if o.type=='MESH'];assert meshes
 for group in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  node=next((o for o in root.children_recursive if o.name==group),None);assert node is not None and any(c.type=='MESH' for c in node.children_recursive),(r['name'],group)
 for mesh in meshes:
  assert all(abs(x)<1e-5 for x in mesh.location) and all(abs(x)<1e-5 for x in mesh.rotation_euler) and all(abs(x-1)<1e-5 for x in mesh.scale),(r['name'],'unbaked transform',mesh.name)
  assert all(math.isfinite(x) for v in mesh.data.vertices for x in v.co)
 result.append({'name':r['name'],'packedReference':packed[0].name,'sha256':hashlib.sha256(got).hexdigest(),'packedImageCount':1,'bakedMeshTransforms':True,'nativeBytes':p.stat().st_size})
json.dump(result,open(OUT/'native-proof.json','w'),indent=2);print('NATIVE_PROOF_PASS',len(result),flush=True)
