"""Create reference/render comparison sheets. Run with a Python containing Pillow."""
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[4];entries=json.load(open(ROOT/'apps/web/src/data/blender-scooters.json'));out=ROOT/'artifacts/blender/catalog/scooters'
for k in range(0,len(entries),4):
 chunk=entries[k:k+4];canvas=Image.new('RGB',(960,len(chunk)*380),'white');d=ImageDraw.Draw(canvas)
 for j,e in enumerate(chunk):
  y=j*380;d.text((15,y+5),e['name']+' | manufacturer reference / Blender reconstruction',fill='black')
  image=e.get('supplementalImage') if e['key']=='ausom-f1-max' else e['image']
  ref=Image.open(ROOT/'apps/web/public'/image.lstrip('/')).convert('RGB');render=Image.open(out/(e['key']+'.png')).convert('RGB')
  for i,im in enumerate([ref,render]):
   fit=ImageOps.contain(im,(475,350));canvas.paste(fit,(i*480+(475-fit.width)//2,y+25+(350-fit.height)//2))
 canvas.save(out/f'comparison-{k//4+1}.jpg',quality=93)
print('Created five comparison sheets')
