import urllib.request,json,re,concurrent.futures,pathlib,time,io,subprocess
from PIL import Image
BASE=pathlib.Path(__file__).resolve().parents[4]; OUT=BASE/'artifacts/blender/expansion/bikes'
def fetch(u):
 try:
  return subprocess.check_output(['curl','-L','-s','--fail','--max-time','45','-A','Mozilla/5.0',u])
 except Exception as e:return None
sites={'Engwe':'https://engwe.com','Fiido':'https://fiido.com','Aventon':'https://www.aventon.com','Rad Power':'https://www.radpowerbikes.com','Himiway':'https://himiwaybike.com','Lectric':'https://lectricebikes.com','Super73':'https://super73.com'}
def catalog(kv):
 brand,site=kv;data=fetch(site+'/products.json?limit=250');p=[]
 if data:
  try:p=json.loads(data)['products']
  except:pass
 json.dump(p,open(OUT/(brand.lower().replace(' ','-')+'-catalog.json'),'w'))
 return brand,len(p)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
  for r in ex.map(catalog,sites.items()):print(r,flush=True)
