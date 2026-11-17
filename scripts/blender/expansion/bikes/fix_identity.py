from source import *
refs=json.load(open(OUT/'ready-references.json'));by={x['name']:x for x in refs}
u='https://engwe.pl/cdn/shop/files/ep2_pro_bk_d4a165e8-cb0c-4a8c-89af-6ea8e33f603c.jpg?v=1777357738&width=1500';data=fetch(u);im=Image.open(io.BytesIO(data));im.thumbnail((1200,1200));p=BASE/'apps/web/public/assets/vehicles/expansion/bikes/engwe-ep-2-pro.webp';im.save(p,'WEBP',quality=90);by['Engwe EP-2 Pro'].update(source='https://engwe.pl/products/engwe-ep-2-pro-rowery-elektryczne',imageSource=u,credit='ENGWE Poland',variantNote='EP-2 Pro original configuration, black; regional manufacturer catalog lists EP-2 Pro separately from EP-2 Boost.',dimensions=list(im.size),bytes=p.stat().st_size,referenceKind='manufacturer-product-reference')
old=next(x for x in json.load(open(BASE/'apps/web/src/data/vehicle-references.json')) if x['name']=='Altis Sigma MX');r=by['Altis Sigma'];p=BASE/('apps/web/public'+r['image']);p.write_bytes((BASE/('apps/web/public'+old['image'])).read_bytes());r.update(source=old['source'],imageSource=old['imageSource'],credit=old['credit'],variantNote='Sigma family represented by the black Sigma MX off-road trim. Manufacturer product page uses /products/altis-sigma for this same trim; no different-model alias inferred.',dimensions=old['dimensions'],bytes=p.stat().st_size,referenceKind='manufacturer-product-reference')
by['Fiido D21']['variantNote']='D21 folding torque-sensor city bicycle, grey regional product reference.'
by['Fiido D11']['variantNote']='Original D11 manufacturer Indiegogo campaign reference, blue-grey folding bicycle.'
by['Talaria Sting']['variantNote']='Original Sting family represented by the Sting MX3 trim from the Canadian distributor catalog.'
by['Talaria Sting MX3']['variantNote']='Sting MX3 off-road, Fastace fork trim, Canadian distributor product reference.'
by['Talaria X3']['variantNote']='X3 Concept / XXX low horizontal-battery platform, Smartwheel product reference.'
by['Talaria XXX L1E']['variantNote']='XXX TL2500 L1E road trim; official Iberian regional catalog, mirrors and registration bracket.'
by['Rad Power RadRunner']['variantNote']='RadRunner family represented by the RadRunner 2 utility trim; regional manufacturer technical catalog.'
by['Aventon Level']['variantNote']='Level family, low top-tube commuter reference pictured in Aventon manufacturer removable-battery guide.'
by['Arctic Leopard XE Pro S Super']['referenceKind']='manufacturer-product-illustration'
json.dump(refs,open(OUT/'ready-references.json','w'),indent=2)
print('Source identities corrected; exact EP-2 Pro and manufacturer-documented Sigma trim')
