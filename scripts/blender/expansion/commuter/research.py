import json,subprocess,time
from pathlib import Path
ROOT=Path('/Users/abay/Desktop/voltforge');OUT=ROOT/'artifacts/blender/expansion/commuter'
domains=['kukirin-escooter.com','ausomstore.com','shop.niu.com','www.iscooterglobal.com','ienyrid.com','joyorscooter.com','bogistshop.com','kugoo.eu','www.ausom.com','shopeu.niu.com']
for domain in domains:
 p=OUT/(domain+'.json');r=subprocess.run(['curl','-L','-s','--fail','--max-time','45','-A','Mozilla/5.0','https://'+domain+'/products.json?limit=250'],capture_output=True)
 try:
  data=json.loads(r.stdout);p.write_text(json.dumps(data));print(domain,len(data['products']),flush=True)
 except Exception as e:print(domain,'error',r.returncode,r.stdout[:40],flush=True)
 time.sleep(.5)
