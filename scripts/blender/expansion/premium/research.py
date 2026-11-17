import urllib.request,json,concurrent.futures,re,time,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; ART=ROOT/'artifacts/blender/expansion/premium'
HOSTS=['minimotorsusa.com','dualtronusa.com','www.minimotors-nyc.com','www.kaabousa.com','www.kaaboeu.com','vsett.com.au','www.falconpev.com.sg','www.inokim.com','apolloscooters.co','store.inmotionworld.com','www.yumeway.com','www.teverun.com','roadrunnerscooters.com','www.voromotors.com','varlascooter.com','www.hileyrider.com','hileymobility.com']
def fetch(host):
 try:
  url='https://'+host+'/products.json?limit=250';raw=subprocess.check_output(['curl','-fsSL','--max-time','35',url]); data=json.loads(raw); ps=data.get('products',[]);json.dump(ps,open(ART/(host+'.json'),'w'))
  return host,len(ps),[p['title'] for p in ps if len(p.get('variants',[])) and ('scooter' in p['title'].lower() or p.get('product_type','').lower() in ['scooter','electric scooter'])][:40]
 except Exception as e:return host,str(e)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
  for r in ex.map(fetch,HOSTS):print(r,flush=True)
