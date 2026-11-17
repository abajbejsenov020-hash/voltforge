from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[4];O=R/'artifacts/blender/expansion/commuter';selected=json.load(open(O/'selected.json'))
for start in range(0,len(selected),12):
 count=min(12,len(selected)-start);page=Image.new('RGB',(1200,((count+3)//4)*330),'#eee');d=ImageDraw.Draw(page)
 for i,e in enumerate(selected[start:start+12]):
  im=Image.open(R/'apps/web/public'/e['image'].lstrip('/')).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);bg=ImageOps.contain(bg.convert('RGB'),(290,292));x=(i%4)*300;y=(i//4)*330;page.paste(bg,(x+(300-bg.width)//2,y));d.text((x+4,y+299),e['name'],fill='black')
 page.save(O/f'references-{start//12+1}.jpg')
