"""Validate lightmoto GLB container, triangle limits, semantic nodes and coverage.
Run with system Python; standard library only. Does not mutate assets.
"""
import json,struct,pathlib
base=pathlib.Path(__file__).resolve().parents[4]
rows=json.loads((base/'apps/web/src/data/blender-lightmoto.json').read_text())
assert len(rows)==22
assert len({r['name'] for r in rows})==22
assert len({r['key'] for r in rows})==22
proof=[]
for r in rows:
 p=base/'apps/web/public'/r['url'].lstrip('/')
 data=p.read_bytes(); magic,version,length=struct.unpack_from('<III',data)
 assert magic==0x46546c67 and version==2 and length==len(data),(r['name'],'GLB header')
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 g=json.loads(data[20:20+size]);names={n.get('name') for n in g['nodes']}
 assert {'FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount'}<=names,(r['name'],'semantic groups')
 nodes=g['nodes']
 def has_mesh(i):return 'mesh' in nodes[i] or any(has_mesh(c) for c in nodes[i].get('children',[]))
 for required in ['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  index=next(i for i,n in enumerate(nodes) if n.get('name')==required)
  assert has_mesh(index),(r['name'],required,'empty mount')
 triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
 assert triangles==r['triangles'],(r['name'],triangles,r['triangles'])
 assert triangles<180000
 assert len(g['meshes'])==r['meshes'] and r['meshes']<80
 assert r['bytes']==len(data) and 100000<=len(data)<=6000000
 assert not any('uri' in x for x in g.get('buffers',[])),'External buffers'
 assert (base/r['nativeSource']).is_file()
 assert (base/'artifacts/blender/catalog/lightmoto'/f"{r['key']}.png").is_file()
 proof.append({'key':r['key'],'triangles':triangles,'meshes':r['meshes'],'bytes':len(data)})
print(json.dumps({'models':len(proof),'triangles':[min(x['triangles'] for x in proof),max(x['triangles'] for x in proof)],'meshes':[min(x['meshes'] for x in proof),max(x['meshes'] for x in proof)],'bytes':[min(x['bytes'] for x in proof),max(x['bytes'] for x in proof)],'checks':'GLB headers, indices, no external buffers, semantic groups, unique names/keys, file coverage, manifest measurements'},indent=2))
