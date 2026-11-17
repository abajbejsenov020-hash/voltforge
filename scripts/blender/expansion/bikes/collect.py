from source import *
from urllib.parse import urljoin
import html
from html.parser import HTMLParser
class MetaParser(HTMLParser):
 def __init__(self):super().__init__();self.images=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=="meta" and (a.get("property") or a.get("name"))=="og:image":self.images.append(a.get("content"))
mapping={}
def add(brand,items):
 for model,url in items.items():mapping[brand+' '+model]=url
add('Engwe',{'EP-2 Pro':'https://engwe.com/products/engwe-ep-2-pro','Engine Pro':'https://us.engwe.com/products/engine-pro-750w-high-performance-electric-bike','Engine Pro 2.0':'https://engwe.com/products/engwe-engine-pro-2-0','M20':'https://engwe.com/products/engwe-m20','X20':'https://engwe.com/products/engwe-x26-x24-x20','X24':'https://engwe.com/products/engwe-x26-x24-x20','X26':'https://engwe.com/products/engwe-x26-x24-x20','L20':'https://engwe.com/products/engwe-l20','L20 2.0':'https://us.engwe.com/products/l20-2-0','P275 Pro':'https://engwe.com/products/engwe-p275-pro','MapFour N1 Air':'https://engwe.com/products/engwe-n1-air'})
add('Fiido',{'D4S':'https://fiido.ie/product/fiido-d4s-folding-electric-bike/','D11':'https://eu.fiido.com/products/fiido-d11-folding-electric-bike-for-commuter','D21':'https://eu.fiido.com/products/fiido-d21-folding-electric-bike-with-torque-sensor','M21':'https://fiido.com/products/fiido-m21-fat-tire-electric-bike-with-torque-sensor','T1':'https://fiido.com/products/fiido-t1-utility-electric-bike','T2':'https://fiido.com/products/fiido-t2-longtail-cargo-ebike-for-versatile-all-terrain','Titan':'https://fiido.com/products/fiido-titan-robust-cargo-electric-bike-with-ul-certified','C21':'https://fiido.com/products/fiido-c21-lightweight-step-over-urban-gravel-ebikes','Air':'https://fiido.com/products/fiido-air-carbon-fiber-electric-bike'})
add('Aventon',{'Aventure':'https://www.aventon.com/products/aventure-ebike','Aventure.2':'https://www.aventon.com/products/aventure2-ebike','Level':'https://www.aventon.com/products/aventon-level-commuter-ebike','Level.2':'https://www.aventon.com/products/aventon-level-commuter-ebike','Pace 500':'https://www.aventon.com/products/aventon-pace-500-complete-bike','Pace 500.3':'https://www.aventon.com/en-ca/products/pace500-3-step-through-ebike','Soltera':'https://www.aventon.com/products/soltera-ebike','Sinch':'https://www.aventon.com/products/aventon-sinch-foldable-electric-bike','Abound':'https://www.aventon.com/products/abound-ebike','Ramblas':'https://www.aventon.com/products/ramblas-electric-mountain-bike'})
add('Rad Power',{'RadRunner':'https://www.radpowerbikes.com/products/radrunner-electric-utility-bike','RadRunner 2':'https://www.radpowerbikes.com/products/radrunner-electric-utility-bike','RadRunner Plus':'https://www.radpowerbikes.com/products/radrunner-plus-electric-cargo-utility-bike','RadRover 6 Plus':'https://radpowerbikes.ca/pages/new-electric-fat-tire-bikes-2021-radrover','RadCity 5 Plus':'https://radpowerbikes.ca/pages/new-electric-commuter-bikes-2021-radcity','RadExpand 5':'https://www.radpowerbikes.com/products/radexpand-electric-folding-bike','RadWagon 4':'https://radpowerbikes.ca/blogs/the-scenic-route/radwagon-4-electric-cargo-bike-debut'})
add('Himiway',{'Cruiser':'https://himiwaybike.com/products/himiway-electric-fat-bike','Zebra':'https://himiwaybike.com/products/premium-all-terrain-electric-bike','Cobra':'https://himiwaybike.com/products/himiway-softail-electric-mountain-bike','Big Dog':'https://himiwaybike.com/products/moped-style-electric-bike'})
add('Lectric',{'XP 2.0':'https://lectricebikes.com/products/xp-black','XP 3.0':'https://lectricebikes.com/products/xp-black-long-range','XP Lite':'https://lectricebikes.com/products/xp-lite-lectric-blue','XPedition':'https://lectricebikes.com/products/xpedition-single-battery','XPeak':'https://lectricebikes.com/products/xpeak-high-step-ebike'})
add('Super73',{'S2':'https://super73.com/products/super73-s2-se-legacy','R':'https://eu.super73.com/products/super73-r-adventure-series-core','RX':'https://eu.super73.com/products/super73-rx','ZX':'https://super73.com/products/super73-zx-core-legacy','Z Miami':'https://super73.com/products/super73-z-miami-core-legacy'})
add('Trek',{'Marlin':'https://www.trekbikes.com/us/en_US/bikes/mountain-bikes/cross-country-mountain-bikes/marlin/marlin-5-gen-3/a/40773/','Marlin+':'https://www.trekbikes.com/us/en_US/bikes/mountain-bikes/electric-mountain-bikes/marlin/f/F358/marlin%252b-8/41707/','Powerfly':'https://www.trekbikes.com/us/en_US/bikes/mountain-bikes/electric-mountain-bikes/powerfly/powerfly-hardtail/powerfly-4-gen-4/p/37043/','Rail':'https://www.trekbikes.com/us/en_US/bikes/mountain-bikes/electric-mountain-bikes/rail/rail-5-gen-3/p/5275152/','Allant+':'https://www.trekbikes.com/fr/fr_FR/v%C3%A9los/v%C3%A9los-hybrides/v%C3%A9los-hybrides-%C3%A0-assistance-%C3%A9lectrique/allant/allant-7-9/allant-7/p/36931/','Verve+':'https://www.trekbikes.com/us/en_US/f/F436/verve%2B-2-lowstep-gen-3/41518/','FX+':'https://www.trekbikes.com/us/en_US/bikes/hybrid-bikes/electric-hybrid-bikes/fx/fx-2/p/35841/'})
add('Giant',{'Talon':'https://www.giant-bicycles.com/us/talon-1-2025','Talon E+':'https://www.giant-bicycles.com/us/talon-eplus','Explore E+':'https://www.giant-bicycles.com/us/explore-eplus-2','Trance X E+':'https://www.giant-bicycles.com/us/trance-x-eplus-3-20mph-2023','Reign E+':'https://www.giant-bicycles.com/us/reign-eplus-3','Fathom E+':'https://www.giant-bicycles.com/gb/fathom-eplus-2-2024'})
add('Specialized',{'Rockhopper':'https://www.specialized.com/us/en/rockhopper-275/p/199591','Turbo Levo':'https://www.specialized.com/us/en/turbo-levo-comp/p/170517','Turbo Kenevo':'https://www.specialized.com/us/en/turbo-kenevo-comp/p/199956','Turbo Vado':'https://www.specialized.com/us/en/turbo-vado-2-30/p/206163','Turbo Como':'https://www.specialized.com/us/en/turbo-como-30/p/206180','Turbo Tero':'https://www.specialized.com/us/en/turbo-tero-30/p/216840'})
add('Cube',{'Reaction Hybrid':'https://www.cube.eu/be-en/cube-reaction-hybrid-pro-800-blackline/108210','Stereo Hybrid':'https://www.cube.eu/cube-stereo-hybrid-one44-hpc-race-800-blackline/102300','Kathmandu Hybrid':'https://www.cube.eu/cube-kathmandu-hybrid-pro-800-coal-n-black/112201','Touring Hybrid':'https://www.cube.eu/cube-touring-hybrid-pro-800-electricblue-n-prizm/1111020'})
add('Cannondale',{'Moterra Neo':'https://www.cannondale.com/en/bikes/electric/e-mountain/moterra-neo/moterra-neo-eq','Trail Neo':'https://www.cannondale.com/en-us/bikes/electric/e-mountain/trail-neo/trail-neo-3','Adventure Neo':'https://www.cannondale.com/en-us/bikes/electric/e-urban/adventure-neo/adventure-neo-4','Tesoro Neo':'https://www.cannondale.com/en-us/bikes/electric/e-touring/tesoro-neo-x/tesoro-neo-x-3'})
add('Haibike',{'AllMtn':'https://haibike.com/en-de/products/allmtn-cf-95-abs-hmwu1','HardNine':'https://www.haibike.com/gb/en/electric-bikes/electric-mountain-bikes/electric-hardtail-bikes/hardnine-5-gb1242','HardSeven':'https://www.haibike.com/gb/en/electric-bikes/electric-mountain-bikes/electric-hardtail-bikes/hardseven-5-gb1241','Trekking':'https://haibike.com/en-de/collections/trekking-e-bikes'})
# Cache full responses for source auditing; never silently substitute a newer generation.
def process(kv):
 name,url=kv;key=re.sub('[^a-z0-9]+','-',name.lower()).strip('-');cache=OUT/(key+'-source.json');result={'name':name,'source':url,'checked':[url]}
 data=None
 for f in OUT.glob('*catalog.json'):
  for p in json.load(open(f)):
   if p['handle']==url.rstrip('/').split('/')[-1]:
    result.update(title=p['title'],images=p.get('images',[]),variants=p.get('variants',[]),description=p.get('body_html',''));data=p;break
  if data:break
 if '/products/' in url and not data:
  u=url+'.js';raw=fetch(u);result['checked'].append(u)
  if raw:
   try:
    p=json.loads(raw);result.update(title=p.get('title'),images=p.get('images',[]),variants=p.get('variants',[]),description=p.get('description',''));data=p
   except:pass
 if not data:
  raw=fetch(url)
  if raw:
   s=raw.decode('utf8','replace');parser=MetaParser();parser.feed(s);(OUT/(key+'-page.html')).write_text(s)
   titles=re.findall('<title[^>]*>(.*?)</title',s,re.S|re.I);imgs=re.findall('<meta[^>]*(?:property|name)=[\"\']og:image[\"\'][^>]*content=[\"\']([^\"\']+)',s,re.I)
   if not imgs:imgs=re.findall('<meta[^>]*content=[\"\']([^\"\']+)[\"\'][^>]*property=[\"\']og:image',s,re.I)
   result.update(title=html.unescape(titles[0].strip()) if titles else '',images=[html.unescape(urljoin(url,x)) for x in (parser.images or imgs)])
 json.dump(result,open(cache,'w'),indent=2);return name,result.get('title'),len(result.get('images',[]))
if __name__=='__main__':
 chosen=sys.argv[1:] if 'sys' in globals() else []
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
  for r in ex.map(process,mapping.items()):print(r,flush=True)
