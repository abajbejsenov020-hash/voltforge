import json,sys,io
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent));import curate as q
from prepare_refs import dl
r={e['name']:e for e in json.load(open(q.A/'references.json'))}
for n,h,k,note in [('Dualtron Mini','scootidoo.com','dualtron-mini','Original Dualtron Mini single motor, 52V 17.5Ah; not Mini Special.'),('Yume Y10','centralscoot.com','yume-y10','Exact Y10 distributor reference.'),('Yume Osprey','centralscoot.com','yume-osprey','Exact Osprey distributor product; not Predator successor.'),('Yume X11','scootidoo.com','yume-x11','Original X11 distributor listing, explicitly distinguished from X11+ by seller.'),('Varla Eagle One','scootidoo.com','varla-eagle-one','Original Eagle One dealer listing; not Eagle One V2.0 or V3.0.'),('InMotion S1','scootidoo.com','inmotion-s1','Original S1 distributor product; not S1F.'),('Kaabo Wolf Warrior 11','scootidoo.com','kaabo-wolf-warrior-11','Wolf Warrior 11 original dealer reference, distinct from listed 11 Plus and newer Max.')]:
 q.catalog(n,h,k,note);e,err=dl(q.refs[n]);print(n,err)
 if not err:r[n]=e
for n,e in json.load(open(q.A/'second-candidates.json')):
 if n not in ['Apollo Ghost','Varla Eagle One V2.0'] or 'error' in e:continue
 e['variantNote']='Exact named '+('dealer product' if n=='Apollo Ghost' else 'manufacturer introduction')+' photograph.';e,err=dl(e);print(n,err)
 if not err:r[n]=e
json.dump(list(r.values()),open(q.A/'references.json','w'),indent=2)
print('TOTAL',len(r))
