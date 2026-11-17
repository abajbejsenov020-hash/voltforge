from source import *
rows=json.load(open(OUT/'assigned.json'))
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
for brand,site in sites.items():
 p=json.load(open(OUT/(brand.lower().replace(' ','-')+'-catalog.json')))
 if brand=='Fiido':
  for page in range(4,8):
   b=fetch(site+'/products.json?limit=250&page='+str(page))
   try:more=json.loads(b)['products'];p+=more
   except:break
   if len(more)<250:break
  json.dump(p,open(OUT/(brand.lower().replace(' ','-')+'-catalog.json'),'w'))
 for r in [r for r in rows if r['brand']==brand]:
  m=norm(r['model']); matches=[x for x in p if m in norm(x['title'])]
  matches.sort(key=lambda x:(any(t in x['title'].lower() for t in ['battery','tire','tyre','bag','rack','charger','saddle','brake','motor','display','cover','phone','controller','fender','parts','seat','throttle','screw','lock','replacement','tube','basket','headlight']),len(norm(x['title']))))
  print(r['name'],'=>',[(x['title'],x['handle'],len(x.get('images',[]))) for x in matches[:5]],flush=True)
