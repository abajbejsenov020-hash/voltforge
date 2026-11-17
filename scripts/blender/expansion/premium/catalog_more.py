import sys,json,subprocess,concurrent.futures
from pathlib import Path
ART=Path(__file__).resolve().parents[4]/'artifacts/blender/expansion/premium'
def go(host):
 ps=[]
 for page in range(1,9):
  try:
   data=json.loads(subprocess.check_output(['curl','-fsSL','--max-time','35',f'https://{host}/products.json?limit=250&page={page}'],stderr=subprocess.DEVNULL)).get('products',[]);ps.extend(data)
   if len(data)<250:break
  except:break
 if ps:json.dump(ps,open(ART/(host+'.json'),'w'))
 return host,len(ps)
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
 for r in ex.map(go,sys.argv[1:]):print(r,flush=True)
