"""Artifact-level GLB validation, uses only Python standard library."""
import json,struct,math,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def matrix(n):
 if 'matrix' in n:return [[n['matrix'][j*4+i] for j in range(4)] for i in range(4)]
 x,y,z,w=n.get('rotation',[0,0,0,1]);s=n.get('scale',[1,1,1]);t=n.get('translation',[0,0,0]);m=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),t[0]],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),t[1]],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),t[2]],[0,0,0,1]]
 for i in range(3):
  for j in range(3):m[i][j]*=s[j]
 return m
reports=[];manifest=json.load(open(ROOT/'apps/web/src/data/blender-scooters.json'))
for e in manifest:
 p=ROOT/'apps/web/public'/e['url'].lstrip('/');raw=p.read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and length==len(raw)
 n,tag=struct.unpack_from('<II',raw,12);d=json.loads(raw[20:20+n]);assert tag==0x4e4f534a
 names={n.get('name') for n in d['nodes']};assert {'FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount'}<=names,(e['key'],names)
 tri=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives']);assert tri==e['triangles'],(e['key'],tri,e['triangles'])
 assert len(d['meshes'])==e['meshes'] and len(d['meshes'])<70 and tri<160000
 assert len(raw)==e['bytes'] and len(raw)<6000000
 assert (ROOT/e['nativeSource']).stat().st_size<12000000
 assert (ROOT/'artifacts/blender/catalog/scooters'/(e['key']+'.png')).is_file()
 mins=[float('inf')]*3;maxs=[-float('inf')]*3
 def visit(i,parent):
  node=d['nodes'][i];m=mm(parent,matrix(node))
  if 'mesh' in node:
   for primitive in d['meshes'][node['mesh']]['primitives']:
    a=d['accessors'][primitive['attributes']['POSITION']]
    for v in itertools.product(*zip(a['min'],a['max'])):
     pos=[sum(m[j][k]*(*v,1)[k] for k in range(4)) for j in range(3)]
     for j in range(3):mins[j]=min(mins[j],pos[j]);maxs[j]=max(maxs[j],pos[j])
  for c in node.get('children',[]):visit(c,m)
 ident=[[int(i==j) for j in range(4)] for i in range(4)]
 for n in d['scenes'][d.get('scene',0)]['nodes']:visit(n,ident)
 assert mins[1]>=-.001,(e['key'],'below floor',mins[1]);assert mins[1]<.01,(e['key'],'floating',mins[1])
 assert .9<maxs[0]-mins[0]<1.7 and 1.1<maxs[1]-mins[1]<1.6,(e['key'],mins,maxs)
 reports.append(dict(key=e['key'],triangles=tri,meshes=len(d['meshes']),bytes=len(raw),boundsMin=mins,boundsMax=maxs))
 print('PASS',e['key'],tri,len(d['meshes']),len(raw),'floor',round(mins[1],6))
json.dump(dict(models=len(reports),checks='GLB header, actual accessor counts, named assemblies, recorded sizes, native/render existence, transformed glTF bounding boxes and floor contact',reports=reports),open(ROOT/'artifacts/blender/catalog/scooters/verification.json','w'),indent=2)
