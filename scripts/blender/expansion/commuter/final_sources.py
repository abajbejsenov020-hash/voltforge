exec(open('scripts/blender/expansion/commuter/add_photos.py').read().split('for name,(dom,handle,idx)')[0])
def fetch(u):return subprocess.run(['curl','-L','-s','--max-time','30','-A','Mozilla/5.0',u],capture_output=True).stdout.decode(errors='replace')
for name,path in [('Kugoo S1 Pro','kugoo-kirin-s1-pro'),('Kugoo S3','kugoo-s3')]:
 u='https://spb.kugoo-russia.ru/electrosamokaty/'+path;s=fetch(u);(O/(name.lower().replace(' ','-')+'-spb.html')).write_text(s);m=re.search('og:image" content="([^"]+)',s)
 if m:put(name,u,m[1],name,'Official regional distributor reference; exact production year unknown.')
 else:print('UNAVAILABLE',name,len(s),flush=True)
# Segway exact region and reduced-range G30LP have their own source photographs.
for name,u in [('Segway Ninebot Max G30D','https://de-de.segway.com/ekickscooter/products/max-g30d.html'),('Segway Ninebot Max G30LP','https://support.segway.com/support_product.php?segcatid=8')]:
 s=fetch(u);(O/(rows[name]['id'].split(':')[1]+'-exact.html')).write_text(s);im=None
 if name.endswith('G30D'):
  for tag in re.findall('<img[^>]+>',s):
   if 'product_full' in tag:
    m=re.search('src="([^"]+)',tag)
    if m:im=m[1];break
 else:
  for tag in re.findall('<img[^>]+>',s):
   if 'G30LP' in tag or 'g30lp' in tag:
    m=re.search('src="([^"]+)',tag)
    if m:im=m[1];break
 if im:
  if im.startswith('/'):im='https://de-de.segway.com'+im
  put(name,u,im,name,'German market model shown.' if name.endswith('G30D') else 'Exact G30LP US model shown.')
 else:print('UNAVAILABLE',name,len(s),flush=True)
name='iENYRID ES10';put(name,'https://www.ienyridscooter.com/products/ienyrid-es10-electric-scooter','https://img-va.myshopline.com/image/store/1679384023487/iENYRID-ES10-Details-%282%29-min.jpeg?h=1000&w=1000',name,'Legacy US dual-motor variant shown.')
name='Kugoo G2 Pro';s=(O/'kugoo-g2-pro-reg-last.txt').read_text();m=re.search('href="(https://kugoomotors.com/upload/thumbs/source/productimage/[^\"]+)"',s)
if m:put(name,'https://kugoomotors.com/product/kugookirin-g2-pro/7',m[1],name,'Regional official store labels this scooter KugooKirin G2 Pro; exact production year unknown.')
json.dump(list(selected.values()),open(O/'selected.json','w'),indent=2)
