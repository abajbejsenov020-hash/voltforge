import json,subprocess,time
from pathlib import Path
out=Path('artifacts/blender/expansion/commuter')
for domain,path in [('kukirin-escooter.com','collections/electric-scooters/products.json?limit=250'),('www.iscooterglobal.com','products.json?limit=250&page=2'),('joyorscooter.com','products.json?limit=250&page=2'),('kugoo.eu','collections/electric-scooters/products.json?limit=250'),('shop.segway.com','collections/electric-scooters/products.json?limit=250')]:
 r=subprocess.run(['curl','-L','-s','--fail','--max-time','45','-A','Mozilla/5.0','https://'+domain+'/'+path],capture_output=True)
 try:d=json.loads(r.stdout);json.dump(d,open(out/(domain+'-more.json'),'w'));print(domain,len(d.get('products',[])),flush=True)
 except:print(domain,r.returncode,r.stdout[:100],flush=True)
 time.sleep(.5)
