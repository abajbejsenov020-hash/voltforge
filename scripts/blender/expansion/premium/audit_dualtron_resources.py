"""Decode every embedded Dualtron image and compare its exact pixels to authored graphics."""
import json,struct,io,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';P=ROOT/'apps/web/public';T=P/'assets/vehicles/expansion/premium/dualtron-details';rs=[e for e in json.load(open(A/'references.json')) if e['name'].startswith('Dualtron')];checks=[];fail=[]
for e in rs:
 try:
  raw=(P/'models/expansion/premium'/(e['key']+'.glb')).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[20+n+8:];ims=[]
  for im in g['images']:
   v=g['bufferViews'][im['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];expected=(T/(im['name']+'.png')).read_bytes();decoded=Image.open(io.BytesIO(data)).convert('RGBA');source=Image.open(io.BytesIO(expected)).convert('RGBA');assert decoded.size==source.size and max(decoded.size)<=1024;assert decoded.tobytes()==source.tobytes();ims.append(dict(name=im['name'],dimensions=list(decoded.size),bytes=len(data),encodedBytesEqual=data==expected,pixelsEqual=True,sha256=hashlib.sha256(data).hexdigest()))
  checks.append(dict(name=e['name'],images=ims,passed=True))
 except Exception as err:fail.append(dict(name=e['name'],error=str(err)))
report=dict(checked=len(checks),embeddedImages=sum(len(e['images']) for e in checks),failures=fail,checks=checks);(A/'dualtron-resource-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('DUALTRON_RESOURCES',len(checks),report['embeddedImages'],fail);assert len(checks)==23 and not fail
