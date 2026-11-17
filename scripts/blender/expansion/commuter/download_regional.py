exec(open('scripts/blender/expansion/commuter/add_photos.py').read().split('for name,(dom,handle,idx)')[0])
for name,key,url in [('Kugoo S1','kugoo-s1-reg','https://kugoo-russia.ru/electrosamokaty/kugoo-s1'),('Kugoo S3 Pro','kugoo-s3-pro-reg','https://kugoo-russia.ru/electrosamokaty/kugoo-s3pro')]:
 s=(O/(key+'-page.html')).read_text();u=re.search('og:image" content="([^"]+)',s)[1];put(name,url,u,name,'Regional official distributor reference; trim and exact production year unknown.')
for name,key,url in [('Kugoo G1','kugoo-g1-real','https://kugoomotors.com/product/kugoo-g1/6'),('Kugoo G-Max','kugoo-gmax-reg-page','https://kugoomotors.com/product/kugoo-g-max/5')]:
 s=(O/(key+'.html')).read_text();u=re.search('href="(https://kugoomotors.com/upload/thumbs/source/productimage/[^\"]+)"',s)[1];put(name,url,u,name,'Regional official store reference; production year unknown.')
# ABE source explicitly identifies base Y8-S. Regional visual trim is disclosed.
p=next(p for p in json.load(open(O/'joyorscooter.com.json'))['products'] if p['handle']=='joyor-y8s-abe-electric-scooter');put('Joyor Y8-S','https://joyorscooter.com/products/'+p['handle'],p['images'][0]['src'],p['title'],'German ABE variant shown; equipment outside this market is not confirmed.')
# S5 original shell and current S5-ABE are distinguishable, so use regional title rather than assume global equivalence.
p=next(p for p in json.load(open(O/'joyorscooter.com.json'))['products'] if p['handle']=='joyor-s5-abe-electric-scooter');put('Joyor S5','https://joyorscooter.com/products/'+p['handle'],p['images'][0]['src'],p['title'],'German S5 ABE regional variant shown; global S5 equipment is not confirmed.')
json.dump(list(selected.values()),open(O/'selected.json','w'),indent=2)
