import subprocess,json,time
from pathlib import Path
O=Path('artifacts/blender/expansion/commuter')
for domain in ['www.ausomstore.eu','www.iscooterglobal.eu','www.ienyridscooter.com','kukirinmobility.com','www.kukirin-escooters.com','www.kugookirineu.com','www.kugooitaly.com']:
 r=subprocess.run(['curl','-L','-s','--fail','--max-time','35','-A','Mozilla/5.0','https://'+domain+'/products.json?limit=250'],capture_output=True)
 try:d=json.loads(r.stdout);json.dump(d,open(O/(domain+'.json'),'w'));print(domain,len(d.get('products',[])),flush=True)
 except:print('ERR',domain,r.returncode,len(r.stdout),flush=True)
 time.sleep(.5)
