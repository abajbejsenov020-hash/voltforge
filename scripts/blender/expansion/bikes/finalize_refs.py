from download import *
from urllib.parse import quote
refs={x['name']:x for x in json.load(open(OUT/'ready-references.json'))}
# Retain citations per exact model when switching to a clearer photograph from the same catalog/dealer.
def save(n,src,img,note):
 k=key(n);data=fetch(img)
 if not data and '?' in img:data=fetch(img.split('?')[0])
 try:
  im=Image.open(io.BytesIO(data));im.load();im.thumbnail((1200,1200));p=BASE/'apps/web/public/assets/vehicles/expansion/bikes'/(k+'.webp');im.save(p,'WEBP',quality=90)
 except Exception as e: print('FAIL',n,str(e),flush=True);return False
 refs[n]=dict(name=n,type='bike',subtype='emoto' if next(r['brand'] for r in rows if r['name']==n) in ['KuKirin','Sur-Ron','Talaria','Arctic Leopard','Stark','E Ride Pro','Altis'] else 'bicycle',image='/assets/vehicles/expansion/bikes/'+k+'.webp',source=src,imageSource=img,credit=urlparse(src).hostname,variantNote=note,license='Reference image; no open license asserted',dimensions=list(im.size),bytes=p.stat().st_size,referenceKind='manufacturer-product-reference' if any(v in src for v in ['lectricebikes.com','radpowerbikes.com','arctic-leopard.com','engwe.com']) else 'distributor-product-reference');print('SAVED',n,flush=True);return True
# Exact recoveries and side photographs.
for n,indices in {'Sur-Ron Light Bee':[3,6,5,9,11],'Himiway Big Dog':[2,4,6,8,10],'Aventon Pace 500.3':[8,6,10,11],'Cannondale Adventure Neo':[0,8,9,10],'E Ride Pro SS':[5,6,7,8],'Engwe Engine Pro':[4,5,8,10]}.items():
 for i in indices:
  c=candidates[n]['candidates'][i]
  if save(n,c['source'],c['imageSource'],c['text'].split('\n')[0]):break
# Product family entries may represent a specifically named generation; the trim is explicit.
for n,src,h in [('Lectric XP Lite','https://lectricebikes.com/products/xp-lite-lectric-blue','xp-lite-lectric-blue'),('Lectric XPedition','https://lectricebikes.com/products/xpedition-single-battery','xpedition-single-battery'),('Lectric XPeak','https://lectricebikes.com/products/xpeak-high-step-ebike','xpeak-high-step-ebike')]:
 p=next((x for x in json.load(open(OUT/'lectric-catalog.json')) if x['handle']==h),None)
 if p:save(n,src,p['images'][0]['src'],p['title']+'; explicit trim used for the unnumbered catalog family.')
# Parse the second source search, selecting manufacturer/retailer images only after review.
arr=json.load(open(OUT/'image-queries-5.json'))
for q in arr:
 n=q['name']
 if n not in ['Rad Power RadCity 5 Plus','Rad Power RadRover 6 Plus','Rad Power RadWagon 4','Trek Allant+','Lectric XP 2.0']:continue
 cs=[]
 for b in q['results'].split('--------------------------------------------------------------------------------'):
  us=re.findall(r'\((https://[^\n]+)\)',b);ims=re.findall(r'Image URL: (https://[^\n#]+)',b)
  if us and ims:cs.append((us[0],ims[0],b.split('Image URL:')[0].strip().split('\n')[0]))
 order={'Rad Power RadCity 5 Plus':[2,3,4,5,6,7,8,0],'Rad Power RadRover 6 Plus':[0,2,3,4,5],'Rad Power RadWagon 4':[0,3,4,5],'Trek Allant+':[0,1,2,3,4],'Lectric XP 2.0':[0]}[n]
 for i in order:
  if i<len(cs) and save(n,*cs[i]):break
# XP 2.0 official archive promos photo is confirmed by image metadata; inspect full image before accepting.
# Exact E-ZPRO kids model is listed by a specialist sports retailer; do not relabel the larger E-X PRO.
save('Arctic Leopard E-ZPRO','https://sportorg.com.ua/item/leopard-e-zpro','https://sportorg.com.ua/images/product/l/29342d6ff9.jpg','E-ZPRO youth electric dirt bike as explicitly listed by SportORG; distinct from the full-size E-X PRO.')
# Manufacturer visual explicitly labelled as an illustration; retain that limitation.
save('Arctic Leopard XE Pro S Super','https://arctic-leopard.com/produit/xe-pro-s-super/','https://arctic-leopard.com/wp-content/uploads/2026/09/'+quote('非实拍图，谨慎使用，后续会更新')+'.png','XE PRO S Super; manufacturer product illustration (source filename states not a real photograph). Shape is a photo-reference visual reconstruction, not CAD.')
json.dump(list(refs.values()),open(OUT/'ready-references.json','w'),indent=2);print('TOTAL',len(refs))
