import subprocess,re,json,concurrent.futures
from pathlib import Path
O=Path('artifacts/blender/expansion/commuter')
urls=[('kugoo-s1-reg','https://kugoo-russia.ru/electrosamokaty/kugoo-s1'),('kugoo-s1-pro-reg','https://kugoo-russia.ru/electrosamokaty/kugoo-kirin-s1-pro'),('kugoo-s3-reg','https://kugoo-russia.ru/electrosamokaty/kugoo-s3'),('kugoo-s3-pro-reg','https://kugoo-russia.ru/electrosamokaty/kugoo-s3pro'),('kugoo-gmax-reg','https://kugoomotors.com/product/kugoo-g-max/5'),('segway-30d','https://de-de.segway.com/ekickscooter/products/max-g30-d.html'),('segway-30lp','https://support.segway.com/support_product.php?segcatid=18'),('ienyrid-es10-alt','https://ienyridscooter.com/products/ienyrid-es10-electric-scooter'),('iscooter-uk-catalog','https://www.iscooterglobal.co.uk/collections/off-road-electric-scooter/products.json?limit=250'),('joyor-s5-old','https://joyor.com/products/joyor-s5-electric-scooter'),('joyor-s10s-old','https://joyor.com/products/joyor-s10-s-electric-scooter')]
def f(t):
 k,u=t;r=subprocess.run(['curl','-L','-s','--max-time','30','-A','Mozilla/5.0',u],capture_output=True);s=r.stdout.decode(errors='replace');(O/(k+'-page.html')).write_text(s);print(k,len(s),re.findall('<title>(.*?)</title>',s,re.S)[:1],re.findall('<meta[^>]+og:image[^>]+>',s)[:1],flush=True);return {'key':k,'url':u,'bytes':len(s)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:r=list(ex.map(f,urls))
json.dump(r,open(O/'regional-pages.json','w'),indent=2)
