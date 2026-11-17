import json,re,subprocess,time
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path('/Users/abay/Desktop/voltforge');O=R/'artifacts/blender/expansion/commuter';A=R/'apps/web/public/assets/vehicles/expansion/commuter';rows=json.load(open(O/'assigned.json'));pool={}
for f in O.glob('*.json'):
 d=json.load(open(f))
 if isinstance(d,dict) and 'products' in d:
  dom=f.name.replace('-more.json','').removesuffix('.json')
  for p in d['products']:pool[(dom,p['handle'])]=p
M={
'KuKirin G2 VMP':('kugoo.eu','kukirin-g2-vmp-electric-scooter'),
'KuKirin G2 Ultra':('kukirin-escooter.com','kukirin-g2-ultra-electric-scooter'),
'KuKirin G3':('kukirin-escooter.com','kukirin-g3-electric-scooter'),
'KuKirin G4 Max':('kukirin-escooter.com','kukirin-g4-max-electric-scooter'),
'KuKirin M4':('kukirin-escooter.com','kukirin-m4-electric-scooter'),
'KuKirin M4 Pro':('kukirin-escooter.com','kukirin-m4-pro-electric-scooter'),
'KuKirin S1 Max':('kugoo.eu','kukirin-s1-max-electric-scooter'),
'KuKirin S3 Pro':('kukirin-escooter.com','kukirin-s3-pro-electric-scooter'),
'Kugoo G-Booster':('kugoo.eu','kugoo-g-booster-off-road-fast-electric-scooter'),
'Ausom L1':('ausomstore.com','ausom-l1-electric-scooter'),
'Ausom L2':('www.ausom.com','ausom-l2-electric-scooter'),
'Ausom L2 Max':('ausomstore.com','ausom-l2-max-electric-scooter-1'),
'Ausom Gosoul 2 Pro':('ausomstore.com','ausom-gosoul-2-pro-dual-motor-e-scooter'),
'Ausom K20 Pro':('ausomstore.com','ausom-k20-pro-dual-motor-e-scooter'),
'Ausom SR1':('ausomstore.com','ausom-sr1-electric-scooter'),
'NIU KQi1 Pro':('shop.niu.com','niu-kqi1-pro-electric-kick-scooter'),
'NIU KQi2 Pro':('shop.niu.com','niu-electric-kick-scooter-kqi2-pro'),
'NIU KQi3 Sport':('shop.niu.com','niu-electric-kick-scooter-for-adults-kqi3-sport'),
'NIU KQi3 Pro':('shop.niu.com','niu-electric-kick-scooter-for-adults-kqi3-pro'),
'NIU KQi3 Max':('shop.niu.com','niu-kqi3-max-electric-kick-scooter-for-adults'),
'NIU KQi Air':('shop.niu.com','niu-kqi-air-lightest-electric-scooter'),
'NIU KQi 300P':('shop.niu.com','niu-kqi-300p-electric-scooter'),
'NIU KQi 300X':('shop.niu.com','niu-kqi-300x-electric-scooter'),
'Joyor S8':('joyorscooter.com','joyor-s8-electric-scooter-600w-power-90km-range'),
'iScooter i9':('www.iscooterglobal.com','i9-foldable-electric-scooter'),
'iScooter i10':('www.iscooterglobal.com','iscooter-i10-commuter-electric-scooter'),
'iScooter iX3':('www.iscooterglobal.com','ix3-off-road-electric-scooter'),
'iScooter iX4':('www.iscooterglobal.com','iscooter-ix4-off-road-electric-scooter'),
'iENYRID M4 Pro S+':('ienyrid.com','ienyrid-m4-pro-s-new-version-electric-scooter'),
'iENYRID M4 Pro S+ Max':('ienyrid.com','ienyrid-m4-pro-s-plus-max-folding-electric-scooters'),
'iENYRID ES1':('ienyrid.com','ienyrid-es1-dual-motor-electric-scooter'),
'Bogist C1 Pro':('bogistshop.com','bogist-c1-pro-electric-scooter-500w-48v-13ah-40km-shockproof-and-stab-proof-with-seat-give-away-bag-lock-and-smartphone-holder-1'),
}
selected=[]
for row in rows:
 if row['name'] not in M:continue
 domain,handle=M[row['name']];p=pool.get((domain,handle))
 if not p:print('MISSING',row['name'],flush=True);continue
 img=p['images'][0]['src'];key=row['id'].split(':')[1];src='https://'+domain+'/products/'+handle
 # public preview is resized only; retains exact photographed product and source credit.
 url=img+('&' if '?' in img else '?')+'width=900';target=A/(key+'.webp')
 r=subprocess.run(['curl','-L','-s','--fail','--max-time','35','-A','Mozilla/5.0',url],capture_output=True)
 try:
  from io import BytesIO
  im=Image.open(BytesIO(r.stdout)); im.thumbnail((900,900));im.save(target,'WEBP',quality=88)
 except Exception as e:print('IMGERR',row['name'],e,flush=True);continue
 e={'name':row['name'],'type':row['type'],'subtype':'scooter','key':key,'image':'/assets/vehicles/expansion/commuter/'+target.name,'source':src,'imageSource':img,'credit':row['brand'],'variantNote':'Exact model product-page reference. Photo-guided visual reconstruction; approximate proportions, hidden internals inferred; not measured CAD. Regional equipment may differ.','license':'Reference image; no open license asserted','dimensions':list(im.size),'bytes':target.stat().st_size,'referenceKind':'manufacturer-product-reference','productTitle':p['title']}
 if row['name'] in ['Ausom Gosoul 2 Pro','Ausom K20 Pro']:e['variantNote']='Official product title explicitly identifies Dual Motor variant; this preview depicts that version. '+e['variantNote']
 selected.append(e);print('PHOTO',row['name'],p['title'],flush=True)
json.dump(selected,open(O/'selected.json','w'),indent=2)
for start in range(0,len(selected),12):
 page=Image.new('RGB',(1200,((min(12,len(selected)-start)+3)//4)*330),'#eeeeee');d=ImageDraw.Draw(page)
 for i,e in enumerate(selected[start:start+12]):
  im=Image.open(R/'apps/web/public'/e['image'].lstrip('/')).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);bg=ImageOps.contain(bg.convert('RGB'),(290,292));x=(i%4)*300;y=(i//4)*330;page.paste(bg,(x+(300-bg.width)//2,y));d.text((x+4,y+299),e['name'],fill='black')
 page.save(O/f'references-{start//12+1}.jpg')
