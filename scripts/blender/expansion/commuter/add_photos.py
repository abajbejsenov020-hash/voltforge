import json,subprocess,re,html,concurrent.futures
from pathlib import Path
from PIL import Image
from io import BytesIO
R=Path('/Users/abay/Desktop/voltforge');O=R/'artifacts/blender/expansion/commuter';A=R/'apps/web/public/assets/vehicles/expansion/commuter';rows={r['name']:r for r in json.load(open(O/'assigned.json'))};selected={r['name']:r for r in json.load(open(O/'selected.json'))}
pool={}
for f in O.glob('*.json'):
 d=json.load(open(f))
 if isinstance(d,dict) and 'products' in d:
  dom=f.name.replace('-more.json','').removesuffix('.json')
  for p in d['products']:pool[(dom,p['handle'])]=p
pool.update({('www.iscooterglobal.eu',p['handle']):p for p in json.load(open(O/'iscooter-eu2-source.txt'))['products']})
M={'KuKirin A1':('kukirinmobility.com','kukirin-a1-electric-scooter',0),'KuKirin T3':('kugoo.eu','kukirin-t3-electric-scooter',0),'KuKirin G2 VMP':('kukirinmobility.com','kukirin-g2-vmp-spain-street-legal-dgt-approved',1),'KuKirin S1 Max':('kukirinmobility.com','kukirin-s1-max-electric-scooter',0),'Ausom Gosoul 2 Pro':('www.ausomstore.eu','ausom-gosoul-2-pro-electric-scooter',0),'Ausom K20 Pro':('www.ausomstore.eu','ausom-k20-pro-k20-pro-dual-motor-e-scooter',0),'iScooter iX6':('www.iscooterglobal.eu','iscooter-ix6-off-road-electric-scooter',0),'iENYRID M4 Pro S+':('ienyrid.com','ienyrid-m4-pro-s-new-version-electric-scooter',1)}
def put(name,src,url,title,note=''):
 row=rows[name];key=row['id'].split(':')[1];url=html.unescape(url)
 if url.startswith('//'):url='https:'+url
 r=subprocess.run(['curl','-L','-s','--fail','--max-time','35','-A','Mozilla/5.0',url.replace(' ','%20')],capture_output=True)
 try:im=Image.open(BytesIO(r.stdout));im.thumbnail((900,900));p=A/(key+'.webp');im.save(p,'WEBP',quality=88)
 except Exception as err:print('FAIL',name,len(r.stdout),err,flush=True);return
 e={'name':name,'type':'scooter','subtype':'scooter','key':key,'image':'/assets/vehicles/expansion/commuter/'+p.name,'source':src,'imageSource':url,'credit':row['brand'],'variantNote':note+' Exact model product-page reference. Photo-guided reconstruction; photographic proportions and inferred hidden/internal surfaces; not measured CAD. Regional equipment may vary.','license':'Reference image; no open license asserted','dimensions':list(im.size),'bytes':p.stat().st_size,'referenceKind':'manufacturer-product-reference','productTitle':title};selected[name]=e;print('PHOTO',name,title,flush=True)
for name,(dom,handle,idx) in M.items():
 p=pool[(dom,handle)];idx=min(idx,len(p['images'])-1);img=p['images'][idx]['src'];put(name,'https://'+dom+'/products/'+handle,img+('&' if '?' in img else '?')+'width=900',p['title'],'EU product variant shown.' if name.startswith('Ausom') else '')
for name,key in [('KuKirin C1 Pro','kukirin-c1-pro'),('Xiaomi M365','xiaomi-m365'),('Xiaomi Pro 2','xiaomi-pro2')]:
 s=(O/(key+'-source.txt')).read_text()
 if name=='KuKirin C1 Pro':url=re.search('og:image:secure_url" content="([^"]+)',s)[1];source='https://www.kukirin-escooters.com/products/kukirin-c1-pro'
 elif name=='Xiaomi M365':
  imgs=re.findall(r'(?:src|data-src)="([^"]+)"',s);url=next((u for u in imgs if '/mi-scooter/' in u and ('section01' in u or 'scooter.png' in u)),None);source='https://www.mi.com/es/mi-electric-scooter/'
 else:
  imgs=re.findall(r'(?:src|data-src)="([^"]+)"',s);url=next((u for u in imgs if 'mi-electric-scooter-Pro2' in u and ('section01' in u or 'section1' in u)),None);source='https://www.mi.com/uk/mi-electric-scooter-Pro2/'
 if url:put(name,source,url,name)
 else:print('NOIMG',name,[u for u in imgs if 'scooter' in u][:10],flush=True)
json.dump(list(selected.values()),open(O/'selected.json','w'),indent=2)
