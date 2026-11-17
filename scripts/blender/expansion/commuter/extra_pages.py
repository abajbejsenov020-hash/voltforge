import subprocess,json,re,concurrent.futures
from pathlib import Path
O=Path('artifacts/blender/expansion/commuter')
urls=[('kugoo-m2-pro','https://www.jlkugoo.com/electric-scooter/m2-pro.html'),('kugoo-gmax','https://www.kugookirineu.com/products/kugoo-g-max-electric-scooter'),('kugoo-s1','https://www.kugoo-ireland.com/products/kugoo-s1'),('kugoo-s1-pro','https://www.kugoo-ireland.com/products/kugoo-s1-pro'),('kugoo-s3','https://www.kugoo-ireland.com/products/kugoo-s3'),('kugoo-s3-pro','https://www.kugoo-ireland.com/products/kugoo-s3-pro'),('scooter-pro','https://www.mi.com/es/mi-electric-scooter-pro/'),('scooter-essential','https://www.mi.com/es/mi-electric-scooter-essential/'),('scooter-1s','https://www.mi.com/es/mi-electric-scooter-1S/'),('ienyrid10','https://www.ienyridscooter.com/products/ienyrid-es10-electric-scooter'),('ausom-leopard-blog','https://ausomstore.com/blogs/electric-scooter-guide/ausom-leopard-unleashing-the-pinnacle-of-off-road-electric-scooters')]
def f(t):
 k,u=t;r=subprocess.run(['curl','-L','-s','--max-time','30','-A','Mozilla/5.0',u],capture_output=True);s=r.stdout.decode(errors='replace');(O/(k+'-page.html')).write_text(s);print(k,len(s),re.findall('<title>(.*?)</title>',s,re.S)[:1],re.findall('<meta[^>]+og:image[^>]+>',s)[:1],flush=True);return {'key':k,'url':u,'bytes':len(s)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:r=list(ex.map(f,urls))
json.dump(r,open(O/'extra-pages.json','w'),indent=2)
