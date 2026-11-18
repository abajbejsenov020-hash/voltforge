"""Deterministic observed-label artwork, not AI imagery or an alternate product photo."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,random
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'apps/web/public/assets/vehicles/expansion/premium/dualtron-details';OUT.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf'
def text_fit(im,txt,box,color,font=FONT):
 d=ImageDraw.Draw(im);x,y,w,h=box;size=80
 while size>5:
  f=ImageFont.truetype(font,size);bb=d.textbbox((0,0),txt,font=f)
  if bb[2]-bb[0]<=w and bb[3]-bb[1]<=h:break
  size-=1
 d.text((x+w/2,y+h/2),txt,font=f,fill=color,anchor='mm')
cs=json.load(open(Path(__file__).with_name('configs.json')))
for name,c in cs.items():
 if not name.startswith('Dualtron'):continue
 key=name.lower().replace(' ','-');im=Image.new('RGB',(1024,512));rng=random.Random(43);im.putdata([(q,q+1,q+2) for q in (rng.randrange(25,29) for i in range(1024*512))]);d=ImageDraw.Draw(im);style=c['deckGraphic'];model=name.replace('Dualtron ','').upper()
 if style=='thunder3':
  d.ellipse((142,111,882,401),outline=(13,14,15),width=3)
  for side in [0,1]:
   for end in [0,1]:
    pts=[(155,49),(300,49),(378,85),(223,75)];pts=[(x if not end else 1024-x,y if not side else 512-y) for x,y in pts];d.line(pts+[pts[0]],fill=(12,13,14),width=3)
  text_fit(im,'minimotors',(190,211,650,80),(222,224,225));redword=Image.new('RGB',(320,40),(26,27,28));text_fit(redword,'DUALTRON',(0,0,320,36),(208,38,44));im.paste(redword.rotate(180),(360,132));text_fit(im,'THUNDER III',(330,350,370,38),(208,38,44))
 elif style=='oval':
  for inset in [0,12]:d.rounded_rectangle((105+inset,79+inset,919-inset,433-inset),radius=96,outline=(105,108,111) if not inset else (27,28,29),width=5)
  text_fit(im,'DUALTRON',(175,192,680,83),(213,215,216));text_fit(im,model,(365,316,300,40),(181,31,35))
 elif style in ['rails','spider']:
  for yy in [57,455]:d.line([(60,yy),(960,yy)],fill=(148,151,153),width=5)
  text_fit(im,'DUALTRON',(160,191,700,85),(230,231,232));text_fit(im,model,(340,311,350,35),(190,28,32))
 elif style=='popular':
  d.line([(95,69),(900,69),(835,137),(276,137),(220,185)],fill=(198,201,203),width=9);d.line([(95,443),(900,443),(835,375),(276,375),(220,327)],fill=(198,201,203),width=9);d.ellipse((407,170,655,342),outline=(210,213,215),width=7);text_fit(im,'D',(460,211,135,80),(210,213,215))
 else:
  for yy in [51,70,442,461]:d.line([(85,yy),(920,yy)],fill=(109,111,114),width=3)
  text_fit(im,'DUALTRON',(170,191,680,85),(220,222,224));text_fit(im,model,(350,312,320,38),(182,29,34))
 im.save(OUT/(key+'-grip.png'),optimize=True)
im=Image.new('RGB',(256,512),(2,6,8));d=ImageDraw.Draw(im);d.arc((28,163,232,365),30,330,fill=(0,166,226),width=5);d.arc((38,173,222,355),120,270,fill=(57,201,99),width=3);text_fit(im,'00',(50,219,170,74),(230,237,240));text_fit(im,'km/h',(87,296,85,26),(170,189,201));text_fit(im,'ECO  DUAL',(29,139,208,29),(55,172,208));text_fit(im,'MINIMOTORS',(20,30,220,26),(210,213,216));d.rectangle((30,415,226,430),outline=(12,130,188),width=2)
for j in range(9):d.rectangle((34+j*21,419,48+j*21,426),fill=(47,194,94))
for yy,txt in [(75,'SAFE  PAS'),(369,'TRIP  000.0'),(459,'EY4   BLUETOOTH')]:text_fit(im,txt,(25,yy,210,23),(53,164,215))
im.save(OUT/'ey4-screen.png',optimize=True)
