import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import curate as q
from prepare_refs import dl
r={e['name']:e for e in json.load(open(q.A/'references.json'))}
for n,h,k,note in [('Hiley Tiger 10','hileymobility.com','tiger-10v5','Tiger 10 family represented by explicitly named Tiger10 V5 2026 manufacturer version; not T10 Pro.'),('Yume Hawk Pro','www.yumescooter.com','hawk-pro-wide-6000w','Hawk Pro family represented by manufacturer Hawk Pro Wide 6000W version with 10x4.5-inch road tyres.')]:
 q.catalog(n,h,k,note);e,err=dl(q.refs[n]);print(n,err)
 if not err:r[n]=e
for n,ref,src,note in [('RoadRunner RS5','RoadRunner RS5 Max','https://roadrunnerscooters.com/collections/rs5','Unspecified RS5 family is represented by current RS5 MAX trim. Manufacturer RS5 family page explicitly lists PRO/MAX. Original RS5 1.0 is not claimed.'),('EMOVE Cruiser','EMOVE Cruiser S','https://www.voromotors.com/products/emove-cruiser','Unspecified Cruiser family is represented by manufacturer Cruiser S 52V trim on the Cruiser product page. Original pre-S generation is not claimed.')]:
 e=dict(r[ref]);e.update(name=n,key=q.key(n),source=src,variantNote=note);e,err=dl(e);print(n,err)
 if not err:r[n]=e
q.catalog('EMOVE RoadRunner','www.voromotors.com','emove-roadrunner','RoadRunner family represented by manufacturer RoadRunner V2 base version, not RoadRunner Pro.');e,err=dl(q.refs['EMOVE RoadRunner']);print(e['name'],err)
if not err:r[e['name']]=e
json.dump(list(r.values()),open(q.A/'references.json','w'),indent=2);print('TOTAL',len(r))
