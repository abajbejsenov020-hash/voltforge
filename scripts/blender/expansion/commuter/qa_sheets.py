from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[4];O=R/'artifacts/blender/expansion/commuter';selected=json.load(open(O/'selected.json'))
def thumb(im,size):
 im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);return ImageOps.contain(bg.convert('RGB'),size)
for start in range(0,len(selected),8):
 subset=selected[start:start+8];page=Image.new('RGB',(1200,((len(subset)+1)//2)*300),'#eeeeee');draw=ImageDraw.Draw(page)
 for i,e in enumerate(subset):
  x=i%2*600;y=i//2*300
  ref=thumb(Image.open(R/'apps/web/public'/e['image'].lstrip('/')),(290,265));page.paste(ref,(x+(300-ref.width)//2,y))
  p=O/(e['key']+'.png')
  if p.exists():
   im=thumb(Image.open(p),(290,265));page.paste(im,(x+300+(300-im.width)//2,y))
  draw.text((x+5,y+270),e['name']+' | reference / Blender',fill='black')
 page.save(O/f'comparison-{start//8+1}.jpg',quality=91)
rows=[]
for e in selected:
 rows.append('<section><h2>'+html.escape(e['name'])+'</h2><div><img src="../../../../apps/web/public'+e['image']+'"><img src="'+e['key']+'.png"></div><a href="'+html.escape(e['source'])+'">Primary source</a><p>'+html.escape(e['variantNote'])+'</p></section>')
(O/'qa-gallery.html').write_text('<!doctype html><meta charset="utf-8"><title>Commuter photo / Blender QA</title><style>body{font:16px system-ui;background:#eee;margin:24px}section{background:white;margin:20px 0;padding:18px}h2{font-size:20px}section div{display:flex}img{width:48%;height:420px;object-fit:contain}p{max-width:80ch}</style><h1>Exact product reference / Blender reconstruction</h1>'+''.join(rows))
print('Comparison sheets', (len(selected)+7)//8)
