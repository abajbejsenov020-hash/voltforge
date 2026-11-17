from source import *
from PIL import ImageDraw
cs={x['name']:x for x in json.load(open(OUT/'candidates.json'))}
for n in ['Engwe Engine Pro','Aventon Pace 500']:
 candidates=cs[n]['candidates'];sheet=Image.new('RGB',(1200,900),'white');d=ImageDraw.Draw(sheet)
 for i,c in enumerate(candidates[:12]):
  data=fetch(c['imageSource'])
  try:
   im=Image.open(io.BytesIO(data)).convert('RGB');im.thumbnail((290,260));x=(i%4)*300;y=(i//4)*300;sheet.paste(im,(x+(300-im.width)//2,y));d.text((x+8,y+270),str(i),fill='black')
  except:pass
 sheet.save(OUT/(n.lower().replace(' ','-')+'-gallery.jpg'))
