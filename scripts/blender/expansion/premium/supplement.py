import sys,json,re,concurrent.futures,io
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent));import curate as q
from prepare_refs import dl
A=q.A;P=q.P
r={e['name']:e for e in json.load(open(A/'references.json'))}
for name,host,handle,note in [
 ('Apollo Air','www.electrickicks.com.au','apollo-air-2023-electric-scooter','Apollo Air V3 2023 photographed revision.'),
 ('Apollo City Pro','www.electrickicks.com.au','apollo-city-23-pro-v3-electric-scooter','City Pro V3 2023 steel gray dual motor configuration.'),
 ('Apollo Pro','www.electrickicks.com.au','apollo-pro-electric-scooter','Apollo Pro 2023 generation; not Phantom 2.0 successor.'),
 ]:
 q.catalog(name,host,handle,note);e,err=dl(q.refs[name]);print(name,err)
 if not err:r[name]=e
# RS5 PRO and MAX exterior equivalence is explicitly documented by manufacturer.
e=dict(r['RoadRunner RS5 Max']);e.update(name='RoadRunner RS5 Pro',key=q.key('RoadRunner RS5 Pro'),source='https://support.roadrunnerscooters.com/hc/en-us/articles/19310473625751-What-are-the-differences-between-the-RS5-PRO-and-the-RS5-MAX',variantNote='Manufacturer documents battery-only differentiation between RS5 PRO and MAX. Shared photographed PRO/MAX exterior; internal battery capacity is not represented.');e,err=dl(e)
if not err:r[e['name']]=e
for n,e in json.load(open(A/'extra-candidates.json')):
 if n not in ['Kaabo Wolf King GT','Kaabo Mantis 10'] or 'error' in e:continue
 e['variantNote']='Exact manufacturer product photograph.';e,err=dl(e);print(n,err)
 if not err:r[n]=e
# Manufacturer Apollo Go side-view photograph, linked directly by current exact Go product page.
e=dict(name='Apollo Go',key='apollo-go',source='https://apolloscooters.co/products/apollo-go',imageSource='https://cdn.shopify.com/s/files/1/0030/8183/0512/files/7_5caf06fb-3919-419f-af48-40e79916a1db.png?v=1776450086',credit='Apollo Scooters',variantNote='Go 2026 product side-view reference; not Go Stellar.',productTitle='Apollo Go');e,err=dl(e);print(e['name'],err)
if not err:r[e['name']]=e
# Manufacturer catalog photographs cropped exactly around their printed named products.
for name,page,box in [('Teverun Fighter 11',7,(.50,.06,.98,.70)),('Teverun Blade Mini',9,(.01,.06,.49,.71))]:
 im=Image.open(A/f'teverun-page-{page:02}.jpg');w,h=im.size;im=im.crop(tuple(int(v*(w if i%2==0 else h)) for i,v in enumerate(box)));im.thumbnail((1100,1100));k=q.key(name);f=P/(k+'.webp');im.save(f,'WEBP',quality=92)
 url='https://teverun.com/wp-content/uploads/2024/04/4.TEVERUN-CATALOG-202404.pdf';r[name]=dict(name=name,key=k,type='scooter',subtype='scooter',source=url+'#page='+str(page),imageSource=url+'#page='+str(page),credit='Teverun manufacturer catalog 2024',variantNote='Exact named manufacturer catalog photograph; cropped from page '+str(page)+'.',productTitle=name,image='/assets/vehicles/expansion/premium/'+f.name,dimensions=list(im.size),bytes=f.stat().st_size,license='Manufacturer reference photograph; no open license asserted',referenceKind='manufacturer-catalog-reference')
json.dump(list(r.values()),open(A/'references.json','w'),indent=2)
print('TOTAL',len(r))
