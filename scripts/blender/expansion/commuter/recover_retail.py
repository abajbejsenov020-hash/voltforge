exec(open('scripts/blender/expansion/commuter/add_photos.py').read().split('for name,(dom,handle,idx)')[0])
for name,key,source in [('Kugoo S1 Pro','s1pro-retailer','https://mikrofahrzeuge.com/product/kugoo-kirin-s1-pro-e-scooter/'),('Bogist M5 Pro','m5pro-retailer','https://www.boulanger.com/ref/9000921800')]:
 s=(O/(key+'.html')).read_text();url=re.search('og:image" content="([^"]+)',s)[1];put(name,source,url,name,'Exact retailer listing; regional trim/production year unknown. No Pro+ or TWOFISH substitution.' if name.startswith('Bogist') else 'Retailer labels this model Kugoo Kirin S1 Pro; regional trim/production year unknown.')
 selected[name]['referenceKind']='retailer-product-reference';selected[name]['credit']='BOGIST / Boulanger marketplace listing' if name.startswith('Bogist') else 'Kugoo / Mikrofahrzeuge'
json.dump(list(selected.values()),open(O/'selected.json','w'),indent=2)
a=json.load(open(O/'unresolved-audit.json'));a=[e for e in a if e['name'] not in ['Kugoo S1 Pro','Bogist M5 Pro']];json.dump(a,open(O/'unresolved-audit.json','w'),indent=2)
