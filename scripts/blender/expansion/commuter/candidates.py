import json,re
from pathlib import Path
out=Path('artifacts/blender/expansion/commuter'); rows=json.load(open(out/'assigned.json')); sources=[]
for f in out.glob('*.json'):
 d=json.load(open(f))
 if isinstance(d,dict) and 'products' in d:
  domain=f.name.replace('-more.json','').removesuffix('.json')
  sources += [(domain,p) for p in d['products']]
brands={'KuKirin':['kukirin-escooter.com','kugoo.eu'],'Kugoo':['kugoo.eu'],'Ausom':['ausomstore.com','www.ausom.com'],'NIU':['shop.niu.com'],'Joyor':['joyorscooter.com'],'iScooter':['www.iscooterglobal.com'],'iENYRID':['ienyrid.com'],'Bogist':['bogistshop.com']}
result={}
for row in rows:
 if row['brand'] not in brands:continue
 model=row['model'];norm=lambda s:re.sub('[^a-z0-9]','',s.lower());needle=norm(model)
 matches=[]
 for domain,p in sources:
  if domain not in brands[row['brand']]:continue
  title=p['title'];text=norm(title)
  if needle not in text or not p.get('images'):continue
  if max([float(v.get('price',0)) for v in p.get('variants',[])] or [0])<185:continue
  if re.search('battery|charging|charger|controller|replacement|suspension|rear motor|front motor|hub motor|seat kits',title,re.I):continue
  matches.append({'domain':domain,'handle':p['handle'],'title':title,'image':p['images'][0]['src']})
 seen=set(); matches=[m for m in matches if not (m['handle'] in seen or seen.add(m['handle']))]
 result[row['name']]=matches
 print(row['name'],':',[(m['domain'],m['handle']) for m in matches[:5]])
json.dump(result,open(out/'candidates.json','w'),indent=2)
