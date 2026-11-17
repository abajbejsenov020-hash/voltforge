from source import *
from PIL import ImageOps,ImageDraw
paths=sorted((BASE/'apps/web/public/assets/vehicles/expansion/bikes').glob('*.webp'))
for start in range(0,len(paths),20):
 sheet=Image.new('RGB',(1500,1250),'#e8e8e8');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(paths[start:start+20]):
  x=(i%4)*375;y=(i//4)*250;im=Image.open(p).convert('RGBA');white=Image.new('RGBA',im.size,'white');white.alpha_composite(im);im=white.convert('RGB');im.thumbnail((365,220));sheet.paste(im,(x+(375-im.width)//2,y+(220-im.height)//2));d.text((x+8,y+225),p.stem[:46],fill='black')
 sheet.save(OUT/('references-'+str(start//20)+'.jpg'))
print(len(paths))
