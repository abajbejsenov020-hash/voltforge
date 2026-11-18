"""Make source/full/top/detail review sheets for every owned Dualtron."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import json
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';rs=[e for e in json.load(open(A/'references.json')) if e['name'].startswith('Dualtron')]
for page in range((len(rs)+3)//4):
 sheet=Image.new('RGB',(1440,1320),'#e8ebed');d=ImageDraw.Draw(sheet)
 for row,e in enumerate(rs[page*4:(page+1)*4]):
  paths=[ROOT/'apps/web/public'/e['image'].lstrip('/')]+[A/(e['key']+s+'.png') for s in ['', '-top','-deck']]
  for col,path in enumerate(paths):
   im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);im=ImageOps.contain(bg.convert('RGB'),(354,298));sheet.paste(im,(col*360+(354-im.width)//2,row*330+(298-im.height)//2));d.text((col*360+8,row*330+303),e['name']+' | '+['reference','full','top','deck'][col],fill='black')
 sheet.save(A/f'dualtron-review-{page+1:02}.jpg',quality=94)
print('DUALTRON_CONTACTS',len(rs),(len(rs)+3)//4)
