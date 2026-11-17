from source import *
from urllib.parse import urlparse
rows=json.load(open(OUT/'assigned.json'));candidates={x['name']:x for x in json.load(open(OUT/'candidates.json'))}
# Explicit audited source selections: manufacturer where available, established bicycle retailers otherwise.
select={'Trek Marlin':0,'Trek Marlin+':0,'Trek Powerfly':1,'Trek Rail':0,'Trek Allant+':0,'Trek Verve+':3,'Trek FX+':1,'Cube Reaction Hybrid':0,'Cube Stereo Hybrid':0,'Cube Kathmandu Hybrid':2,'Cube Touring Hybrid':7,'Cannondale Trail Neo':0,'Cannondale Adventure Neo':7,'Cannondale Tesoro Neo':2,'Haibike AllMtn':0,'Haibike HardNine':0,'Haibike HardSeven':3,'Haibike Trekking':2,'Specialized Turbo Como':4,'Specialized Turbo Tero':0,'Giant Explore E+':7,'Giant Reign E+':2,'Aventon Aventure':2,'Aventon Aventure.2':1,'Aventon Level':7,'Aventon Level.2':0,'Aventon Pace 500':7,'Aventon Pace 500.3':2,'Aventon Soltera':0,'Aventon Sinch':2,'Aventon Abound':5,'Aventon Ramblas':0,'Rad Power RadRunner':1,'Rad Power RadRunner 2':2,'Rad Power RadExpand 5':1,'Himiway Cruiser':4,'Himiway Cobra':5,'Himiway Big Dog':0,'Lectric XP 3.0':0,'Lectric XP Lite':7,'Lectric XPedition':4,'Lectric XPeak':2,'Engwe Engine Pro':0,'Engwe L20 2.0':4,'Fiido D11':0,'Fiido D21':4,'Super73 R':4,'Super73 RX':4,'KuKirin X1':0,'Sur-Ron Light Bee':4,'Sur-Ron Light Bee S':0,'Talaria Sting':1,'Talaria Sting MX3':1,'Talaria X3':4,'Talaria XXX L1E':0,'E Ride Pro SS':0,'Altis Sigma':0,'Altis Delta':0,'Stark Varg':0}
# Do not accept current-generation photos for explicitly numbered archived models.
reject={'Lectric XP 2.0','Arctic Leopard E-ZPRO','Arctic Leopard E-16Z','Arctic Leopard E-20Y','Arctic Leopard XE Pro S Super'}
def key(n):return re.sub('[^a-z0-9]+','-',n.lower().replace('+','-plus')).strip('-')
def process(r):
 n=r['name'];k=key(n);p=OUT/(k+'-source.json');d=json.load(open(p)) if p.exists() else {};src=d.get('source');imgs=d.get('images',[]);note=d.get('title') or ''
 if n in reject:return None
 if n in select:
  cs=candidates[n]['candidates'];c=cs[select[n]];src=c['source'];imgs=[c['imageSource']];note=c['text'].split('\n')[0]
 if not imgs:return None
 if n.startswith('Engwe X'):
  vv=[v for v in d.get('variants',[]) if v['title'].startswith(r['model']+' ')];imgs=[vv[0]['featured_image']];note='ENGWE '+vv[0]['title']
 elif n.startswith('Engwe') and n not in select and d.get('variants') and d['variants'][0].get('featured_image'):imgs=[d['variants'][0]['featured_image']];note+='; '+d['variants'][0]['title']
 imsrc=imgs[0].get('src') if isinstance(imgs[0],dict) else imgs[0]
 if imsrc.startswith('//'):imsrc='https:'+imsrc
 data=fetch(imsrc)
 if not data:return {'name':n,'error':'download failed','url':imsrc}
 try:
  im=Image.open(io.BytesIO(data));im.load();im.thumbnail((1200,1200));path=BASE/'apps/web/public/assets/vehicles/expansion/bikes'/ (k+'.webp');im.save(path,'WEBP',quality=90)
 except Exception as e:return {'name':n,'error':str(e),'url':imsrc}
 return dict(name=n,type='bike',subtype='emoto' if r['brand'] in ['KuKirin','Sur-Ron','Talaria','Arctic Leopard','Stark','E Ride Pro','Altis'] else 'bicycle',image='/assets/vehicles/expansion/bikes/'+k+'.webp',source=src,imageSource=imsrc,credit=urlparse(src).hostname,variantNote=note,license='Reference image; no open license asserted',dimensions=list(im.size),bytes=path.stat().st_size,referenceKind='manufacturer-product-reference' if any(x in src for x in ['engwe.com','fiido.com','giant-bicycles.com','specialized.com','trekbikes.com','cube.eu','cannondale.com','himiwaybike.com','lectricebikes.com','super73.com','radpowerbikes.com','radpowerbikes.ca']) else 'distributor-product-reference')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:res=list(ex.map(process,rows))
 json.dump(res,open(OUT/'download-results.json','w'),indent=2)
 print('Downloaded',sum(bool(x and x.get('image')) for x in res),'errors',[x for x in res if x and x.get('error')])
