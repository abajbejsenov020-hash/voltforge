import subprocess,re,json,concurrent.futures
from pathlib import Path
O=Path('artifacts/blender/expansion/commuter')
urls=[('kugoo-s1-pro-good','https://www.kugoo-russia.ru/electrosamokaty/kugoo-kirin-s1-pro'),('kugoo-s3-good','https://www.kugoo-russia.ru/electrosamokaty/kugoo-s3'),('kugoo-g2-pro-reg','https://kugoomotors.com/product/kugookirin-g2-pro/7'),('ausom-dt1-retailer','https://www.oolactive.com/products/ausom-leopard-dt1-electric-scooter.js'),('ausom-dt1pro-retailer','https://www.oolactive.com/products/ausom-leopard-dt1-pro-electric-scooter.js'),('ausom-gallop-retailer','https://www.oolactive.com/products/ausom-gallop-electric-scooter.js'),('ausom-leopard-retailer','https://www.oolactive.com/products/ausom-leopard-electric-scooter.js'),('segway-g30lp-us','https://support.segway.com/support_product.php?segcatid=19'),('segway-g30d-de','https://de-de.segway.com/sitemap.xml')]
def f(t):
 k,u=t;r=subprocess.run(['curl','-L','-s','--fail','--max-time','30','-A','Mozilla/5.0',u],capture_output=True);s=r.stdout.decode(errors='replace');(O/(k+'-last.txt')).write_text(s);print(k,len(s),re.findall('<title>(.*?)</title>',s,re.S)[:1],re.findall('<meta[^>]+og:image[^>]+>',s)[:1],flush=True);return {'key':k,'url':u,'bytes':len(s)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:r=list(ex.map(f,urls))
json.dump(r,open(O/'last-sources.json','w'),indent=2)
