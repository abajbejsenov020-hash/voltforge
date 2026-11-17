"""Read-only GLB/manifest/native/render coverage audit; standard-library Python."""
from pathlib import Path
import json,struct,itertools,math
BASE=Path(__file__).resolve().parents[4]
rows=json.loads((BASE/'apps/web/src/data/blender-moto-bicycle.json').read_text())
I=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
def mul(a,b):return [sum(a[k*4+r]*b[c*4+k] for k in range(4)) for c in range(4) for r in range(4)]
def matrix(n):
 if 'matrix' in n:return n['matrix']
 x,y,z,w=n.get('rotation',[0,0,0,1]);sx,sy,sz=n.get('scale',[1,1,1]);t=n.get('translation',[0,0,0])
 return [(1-2*y*y-2*z*z)*sx,(2*x*y+2*z*w)*sx,(2*x*z-2*y*w)*sx,0,(2*x*y-2*z*w)*sy,(1-2*x*x-2*z*z)*sy,(2*y*z+2*x*w)*sy,0,(2*x*z+2*y*w)*sz,(2*y*z-2*x*w)*sz,(1-2*x*x-2*y*y)*sz,0,*t,1]
def transform(m,v):return [sum(m[k*4+r]*v[k] for k in range(3))+m[12+r] for r in range(3)]
proof=[]
for row in rows:
 p=BASE/'apps/web/public'/row['url'].lstrip('/');data=p.read_bytes();magic,version,total=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and total==len(data)
 size,typ=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+size]);assert typ==0x4e4f534a
 names={n.get('name') for n in d['nodes']};required=['FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount'];assert all(n in names for n in required)
 points=[];tris=0
 def walk(i,parent):
  nonlocal_dummy=None
  n=d['nodes'][i];m=mul(parent,matrix(n))
  if 'mesh' in n:
   for prim in d['meshes'][n['mesh']]['primitives']:
    a=d['accessors'][prim['attributes']['POSITION']]
    for v in itertools.product(*zip(a['min'],a['max'])):points.append(transform(m,v))
  for j in n.get('children',[]):walk(j,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,I)
 for mesh in d['meshes']:
  for prim in mesh['primitives']:tris+=d['accessors'][prim['indices']]['count']//3
 bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)];dims=[b-a for a,b in bounds]
 assert abs(bounds[1][0])<.002,(row['key'],bounds)
 assert tris==row['triangles'],(row['key'],tris,row['triangles'])
 assert len(d['meshes'])==row['meshes'];assert len(data)==row['bytes'];assert len(data)<6_000_000 and tris<180_000 and row['meshes']<80
 assert (BASE/row['nativeSource']).stat().st_size>100_000
 png=BASE/'artifacts/blender/catalog/moto-bicycle'/(row['key']+'-three-quarter.png');hdr=png.read_bytes()[:24];assert struct.unpack('>II',hdr[16:24])==(640,640)
 proof.append(dict(key=row['key'],triangles=tris,meshes=len(d['meshes']),bytes=len(data),bounds_y_up=bounds,dimensions_m=dims,semanticNodes=True,nativeBlend=True,render640=True))
print(json.dumps(dict(count=len(rows),triangles_max=max(x['triangles'] for x in proof),meshes_max=max(x['meshes'] for x in proof),bytes_max=max(x['bytes'] for x in proof),results=proof),indent=2))
