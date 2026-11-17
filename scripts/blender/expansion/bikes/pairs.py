from source import *
from PIL import ImageDraw
refs=json.load(open(OUT/'ready-references.json'));data=[]
for r in refs:
 k=re.sub('[^a-z0-9]+','-',r['name'].lower().replace('+','-plus')).strip('-');render=OUT/(k+'.png')
 if render.exists():data.append((r,render))
for start in range(0,len(data),8):
 sheet=Image.new('RGB',(1600,1560),'#eeeeee');d=ImageDraw.Draw(sheet)
 for i,(r,render) in enumerate(data[start:start+8]):
  x=(i%2)*800;y=(i//2)*390
  for j,p in enumerate([BASE/('apps/web/public'+r['image']),render]):
   im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);im=bg.convert('RGB');im.thumbnail((390,350));sheet.paste(im,(x+j*400+(400-im.width)//2,y+(350-im.height)//2))
  d.text((x+10,y+357),r['name'],fill='black')
 sheet.save(OUT/('pairs-'+str(start//8)+'.jpg'),quality=92)
print('pairs',len(data))
