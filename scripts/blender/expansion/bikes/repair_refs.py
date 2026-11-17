from source import *
from urllib.parse import urlparse
refs={x['name']:x for x in json.load(open(OUT/'ready-references.json'))}
cs={x['name']:x for x in json.load(open(OUT/'candidates.json'))}
def update(n,src,ims,note=None):
 data=fetch(ims)
 try:im=Image.open(io.BytesIO(data));im.load()
 except:
  data=subprocess.check_output(['curl','-s','-L','--fail','--max-time','30',ims]);im=Image.open(io.BytesIO(data));im.load()
 im.thumbnail((1200,1200));r=refs[n];p=BASE/('apps/web/public'+r['image']);im.save(p,'WEBP',quality=90);r.update(source=src,imageSource=ims,dimensions=list(im.size),bytes=p.stat().st_size,credit=urlparse(src).hostname)
 if note:r['variantNote']=note
 json.dump(list(refs.values()),open(OUT/'ready-references.json','w'),indent=2);print('UPDATED',n,flush=True)
for n,i in [('Engwe Engine Pro',5),('Aventon Pace 500',1)]:
 c=cs[n]['candidates'][i];update(n,c['source'],c['imageSource'],'Engine Pro folding full-suspension reference, prior to 2.0.' if n.startswith('Engwe') else 'Pace 500 Next Gen step-over, SoCal Sand reference trim.')
r=refs['Trek Marlin'];update('Trek Marlin',r['source'],r['imageSource'],'Marlin 5 Gen 3, Miami Green/Dark Aquatic Fade, 2026 reference trim. Nonmotorized pedal mountain bike.')
update('Lectric XP 2.0','https://upway.co/products/lectric-xp-20-ubu72','https://upway.co/cdn/shop/files/UBU72-1_3984x.jpg?v=1716595355','XP 2.0 exact generation; pre-owned product photograph from Upway. Not a newer XP 3.0/4.0 substitution.')
p=next(x for x in json.load(open(OUT/'arctic-catalog.json')) if x['handle']=='e-zpro');update('Arctic Leopard E-ZPRO','https://arctic-leopard.bike/products/e-zpro',p['images'][0]['src'],'E-ZPRO youth electric dirt bike, official regional catalog reference. Distinct from full-size E-X PRO.')
refs['Arctic Leopard E-ZPRO']['referenceKind']='manufacturer-product-reference'
json.dump(list(refs.values()),open(OUT/'ready-references.json','w'),indent=2)
