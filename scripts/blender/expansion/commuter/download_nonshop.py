import json,re,subprocess,html
from pathlib import Path
from PIL import Image
from io import BytesIO
R=Path('/Users/abay/Desktop/voltforge');O=R/'artifacts/blender/expansion/commuter';A=R/'apps/web/public/assets/vehicles/expansion/commuter';selected=json.load(open(O/'selected.json'));by={r['name']:r for r in json.load(open(O/'assigned.json'))};records={r['name']:r for r in json.load(open(O/'nonshop.json'))}
records.update({r['name']:r for r in json.load(open(O/'nonshop-fixed.json')) if 'Xiaomi' not in r['name']})
for name,r in records.items():
 s=(O/(r['key']+'.html')).read_text();u=None
 if '404' in ' '.join(r['title']) or not s:continue
 if name.startswith('Xiaomi'):
  m=re.search(r'<meta property="og:image" content="([^"]+)"',s);u=m[1] if m else None
 else:
  imgs=re.findall(r'<img[^>]+>',s)
  for tag in imgs:
   if 'product_full' in tag and 'src=' in tag:u=re.search('src="([^"]+)"',tag)[1];break
  mapping={'F3':'Kickscooter_F3_PC.png','F3 Pro':'Kickscooter_F3Pro_PC.png','Max G3':'Kickscooter_MaxG3_PC.png','GT3':'Kickscooter_GT3_PC.png','ZT3 Pro':'eKickScooter-ZT3_pro_D.png'}
  model=by[name]['model']
  if model in mapping:
   im=mapping[model];m=re.search(r'"(/content/dam/[^"\n]+/'+re.escape(im)+')"',s);u=m[1] if m else None
 if not u:print('NOIMAGE',name,flush=True);continue
 if u.startswith('//'):u='https:'+u
 elif u.startswith('/'):u='https://eu-en.segway.com'+u
 u=html.unescape(u).replace(' ','%20');target=A/(r['key']+'.webp')
 rr=subprocess.run(['curl','-L','-s','--fail','--max-time','35','-A','Mozilla/5.0',u],capture_output=True)
 try:im=Image.open(BytesIO(rr.stdout));im.thumbnail((900,900));im.save(target,'WEBP',quality=88)
 except Exception as err:print('IMGERR',name,len(rr.stdout),err,flush=True);continue
 e={'name':name,'type':'scooter','subtype':'scooter','key':r['key'],'image':'/assets/vehicles/expansion/commuter/'+target.name,'source':r['url'],'imageSource':u,'credit':by[name]['brand'],'variantNote':'Exact model product reference. Segway E/P regional hardware is shown where specified by source; regional accessories may vary. Photo-guided reconstruction, approximate proportions and inferred internal surfaces; not CAD.','license':'Reference image; no open license asserted','dimensions':list(im.size),'bytes':target.stat().st_size,'referenceKind':'manufacturer-product-reference','productTitle':r['title'][0]};selected.append(e);print('PHOTO',name,im.size,flush=True)
json.dump(selected,open(O/'selected.json','w'),indent=2)
