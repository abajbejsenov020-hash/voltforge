"""Explicit identity mapping; never fuzzy-match a model or substitute successor photos."""
import json,re,subprocess,html,concurrent.futures,io
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';P=ROOT/'apps/web/public/assets/vehicles/expansion/premium';P.mkdir(parents=True,exist_ok=True)
assigned=json.load(open(A/'assigned.json')); refs={};failed={}
def key(name):return re.sub('[^a-z0-9]+','-',name.lower().replace('+',' plus ')).strip('-')
def get(url):return subprocess.check_output(['curl','-fsSL','--max-time','40','-A','Mozilla/5.0',url],stderr=subprocess.DEVNULL)
def catalog(name,host,handle,note='',image=0):
 ps=json.load(open(A/(host+'.json')));p=next(x for x in ps if x['handle']==handle)
 assert p['images'],(name,handle)
 refs[name]=dict(name=name,key=key(name),source=f'https://{host}/products/{handle}',imageSource=p['images'][image]['src'],credit=p.get('vendor') or host,variantNote=note or 'Exact named product reference; photographed configuration reconstructed approximately.',productTitle=p['title'])
def batch(brand,host,rows):
 for model,handle in rows.items():catalog(brand+' '+model,host,handle)
batch('Dualtron','www.minimotors-nyc.com',{'Thunder 2':'dualtron-thunder-2','Ultra 2':'dualtron-ultra-ii-1','Victor Luxury':'dualtron-victor-luxury','Victor Luxury Plus':'dualtron-victor-luxury-1','Eagle Pro':'dualtron-eagle-pro','Storm':'dualtron-storm','Storm Limited':'dualtron-storm-ltd-limited','X2':'dualtron-x-ii','Spider 2':'dualtron-spider-2','City':'dualtron-city'})
batch('Dualtron','minimotorsusa.com',{'Thunder 3':'dualtron-thunder-3-electric-scooter','X Limited':'dualtron-limited','Togo':'dualtron-togo-electric-scooter-copy'})
batch('Dualtron','dual-tron.ca',{'Popular':'dualtron-popular','Achilleus':'dualtron-achilleus-electric-scooter'})
batch('Kaabo','www.kaabousa.com',{'Mantis King GT':'mantis-king-gt','Wolf King GTR':'kaabo-king-gtr'})
batch('Vsett','vsett.com.au',{'8':'vsett-8-electric-scooter','9+':'vsett-9-plus-electric-scooter','10+':'vsett-10-plus-electric-scooter','10 Apex':'vsett-10-apex-electric-scooter','11+':'vsett-11-plus-electric-scooter','11+ Super 72':'vsett-11-electric-scooter-super-72'})
batch('Vsett','www.minimotors-nyc.com',{'8+':'vsett-8-dual-motor'})
batch('Zero','www.falconpev.com.sg',{'8':'zero-8-electric-scooter','9':'zero-9-electric-scooter','10':'zero-10-electric-scooter','10X':'zero-10x-electric-scooter','11X':'zero-11x-electric-scooter'})
batch('Inokim','www.inokim.com',{'Quick 4':'quick-4','OX':'ox','OXO':'oxo'})
batch('InMotion','store.inmotionworld.com',{'S1F':'inmotion-s1f','Climber':'inmotion-climber','RS':'inmotion-rs','RS Lite':'inmotion-rs-lite'})
batch('Yume','www.yumescooter.com',{'Hawk':'hawk','Raptor':'raptor-6000w'})
batch('RoadRunner','roadrunnerscooters.com',{'RS5 Max':'rs5-max-electric-scooter','RX7':'roadrunner-rx7'})
batch('EMOVE','www.voromotors.com',{'Cruiser S':'emove-cruiser','RoadRunner Pro':'emove-roadrunner-pro-seated-electric-scooter'})
batch('Varla','varlascooter.com',{'Pegasus':'pegasus','Eagle One Pro':'eagle-one-pro'})
batch('Hiley','www.hileyrider.com',{'Tiger 10 Pro':'hiley-tiger-t10-pro-dual-motor-electric-scooter'})
# Additional exact product pages, including discontinued catalog URLs, are checked individually.
extra={
'Dualtron Thunder':'https://minimotorsusa.com/products/dualtron-thunder-electric-scooter',
'Dualtron Ultra':'https://dualtron.com.es/producto/patinetes-electricos/dualtron-patinetes-electricos/dualtron-ultra/',
'Dualtron Victor':'https://minimotorsusa.com/products/dualtron-victor-electric-scooter',
'Dualtron X':'https://dualtroneurope.com/en/dualtron/36-dualtron-x.html',
'Dualtron Spider':'https://minimotorsusa.com/products/dualtron-spider-electric-scooter',
'Dualtron Mini':'https://minimotorsusa.com/products/dualtron-mini-electric-scooter',
'Dualtron Mini Special':'https://dualtron-shop.com/product/dualtron-mini-special/',
'Dualtron Forever':'https://dualtron-shop.com/product/dualtron-forever/',
'Kaabo Mantis 8':'https://www.kaabo.com/mantis-8/',
'Kaabo Mantis 10':'https://kaabo.eu/producten/mantis-10/',
'Kaabo Mantis 10 Pro':'https://kaabo.eu/producten/mantis-10-pro-plus/',
'Kaabo Mantis X':'https://www.kaabo.com/mantis-x/',
'Kaabo Wolf Warrior 11':'https://www.voromotors.com/products/kaabo-wolf-warrior',
'Kaabo Wolf Warrior X':'https://www.voromotors.com/products/wolf-warrior-x',
'Kaabo Wolf King':'https://kaabo.eu/producten/wolf-king-72v/',
'Kaabo Wolf King GT':'https://www.voromotors.com/products/wolf-king-gt',
'NAMI Burn-E':'https://nami-electric.com/produit/burn-e/',
'NAMI Burn-E 2':'https://www.fluidfreeride.com/products/nami-burn-e-2',
'NAMI Burn-E 2 Max':'https://www.fluidfreeride.com/products/nami-burn-e-2-max',
'NAMI Klima':'https://nami-electric.com/produit/klima/',
'NAMI Klima Max':'https://nami-electric.com/produit/klima-max/',
'NAMI Stellar':'https://nami-electric.com/produit/stellar/',
'NAMI Super Stellar':'https://nami-electric.com/produit/super-stellar/',
'Vsett 9':'https://vsettscooters.com/pages/vsett-9',
'Inokim Light 2':'https://il.inokim.com/en/products/light-2',
'Apollo Air':'https://apolloscooters.co/products/apollo-air',
'Apollo Go':'https://apolloscooters.co/products/apollo-go',
'Apollo City':'https://apolloscooters.co/products/apollo-city',
'Apollo City Pro':'https://apolloscooters.co/products/apollo-city-2022',
'Apollo Explore':'https://apolloscooters.co/products/apollo-explore',
'Apollo Ghost':'https://apolloscooters.co/products/apollo-ghost',
'Apollo Phantom':'https://apolloscooters.co/products/apollo-phantom',
'Apollo Pro':'https://apolloscooters.co/products/apollo-pro',
'InMotion S1':'https://www.myinmotion.com/products/inmotion-s1',
'Yume Y10':'https://www.yumescooter.com/products/y10',
'Yume X11':'https://www.yumescooter.com/products/x11',
'Yume Hawk Pro':'https://www.yumescooter.com/products/hawk-pro',
'Yume Osprey':'https://www.yumescooter.com/products/osprey',
'Teverun Fighter Mini':'https://teverun-europe.com/product/fighter-mini/',
'Teverun Fighter 10':'https://teverun.com/fighter-ten/',
'Teverun Fighter 11':'https://teverun.lv/teverun-fighter-11/',
'Teverun Fighter Supreme':'https://teverun.com/fighter-supreme/',
'Teverun Blade Mini':'https://teverun.lv/teverun-blade-mini/',
'Teverun Blade GT':'https://teverun.com/blade-gt/',
'RoadRunner RS5':'https://roadrunnerscooters.com/products/roadrunner-rs5',
'RoadRunner RS5 Pro':'https://roadrunnerscooters.com/products/rs5-pro-electric-scooter',
'EMOVE Touring':'https://www.voromotors.com/products/emove-touring',
'EMOVE Cruiser':'https://www.voromotors.com/products/emove-cruiser',
'EMOVE RoadRunner':'https://www.voromotors.com/products/emove-roadrunner',
'Varla Eagle One':'https://varlascooter.com/products/varla-electric-scooter',
'Varla Eagle One V2.0':'https://varlascooter.com/products/eagle-one-v2-0',
'Hiley Tiger 8':'https://www.hiley-mobility.com/tiger-8-electric-scooter/',
'Hiley Tiger 9':'https://www.hiley-mobility.com/tiger-9-electric-scooters/62829289.html',
'Hiley Tiger 10':'https://www.hiley-mobility.com/tiger-10-electric-scooters/',
}
def scrape(row):
 name,url=row
 try:
  raw=get(url).decode('utf-8','replace');(A/(key(name)+'.html')).write_text(raw)
  # Exact heading is audited below; extraction does not auto-accept title aliases.
  title=re.search(r'<title[^>]*>(.*?)</title',raw,re.S);title=html.unescape(re.sub('<.*?>','',title[1])) if title else ''
  tags=re.findall(r'<meta[^>]+>',raw);tag=next(t for t in tags if re.search(r'(?:property|name)=[\'\"]og:image[\'\"]',t));img=html.unescape(re.search(r'content=[\'\"](.*?)[\'\"]',tag)[1]);img=('https:'+img) if img.startswith('//') else img
  return name,dict(name=name,key=key(name),source=url,imageSource=img,credit=url.split('/')[2],variantNote='',productTitle=title)
 except Exception as e:return name,{'error':str(e),'source':url}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for n,r in ex.map(scrape,extra.items()):
   if 'error' in r:failed[n]=r
   else:refs[n]=r
 json.dump({'candidates':list(refs.values()),'failed':failed},open(A/'candidates.json','w'),indent=2)
 for n,r in refs.items():print(n,'=>',r['productTitle'],r['imageSource'][:80])
 print('FAILED',failed)
