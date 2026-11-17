from download import *
res=json.load(open(OUT/'download-results.json'));by={x['name']:x for x in res if x and x.get('image')}
# Prefer exact full-vehicle side views and official pages over folded/detail photos.
fix={'Sur-Ron Light Bee':2,'Aventon Level.2':1,'Trek Marlin+':6,'Cube Reaction Hybrid':2,'Haibike AllMtn':3,'Haibike HardNine':3,'Haibike HardSeven':2,'Haibike Trekking':1,'Himiway Big Dog':7,'Altis Delta':3,'Aventon Pace 500.3':5,'Aventon Pace 500':6,'Cannondale Adventure Neo':5,'E Ride Pro SS':3,'Super73 R':0,'Super73 RX':4}
for n,i in fix.items():select[n]=i
for r in rows:
 n=r['name']
 if n in fix:
  x=process(r)
  if x and x.get('image'):by[n]=x
  else: print('FAIL',n,x,flush=True)
for n,h in [('Arctic Leopard E-16Z','e-16z'),('Arctic Leopard E-20Y','e-20y')]:
 p=next(x for x in json.load(open(OUT/'arctic-catalog.json')) if x['handle']==h)
 k=key(n);d={'name':n,'source':'https://arctic-leopard.bike/products/'+h,'title':p['title'],'images':p['images'],'variants':p['variants']};json.dump(d,open(OUT/(k+'-source.json'),'w'));reject.remove(n);x=process(next(r for r in rows if r['name']==n))
 if x and x.get('image'):by[n]=x
 else:print('FAIL',n,x,flush=True)
json.dump(list(by.values()),open(OUT/'ready-references.json','w'),indent=2);print('READY',len(by))
