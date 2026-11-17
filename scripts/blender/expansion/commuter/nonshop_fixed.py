exec(open('scripts/blender/expansion/commuter/nonshop.py').read().split('with concurrent')[0])
seg={'Max G30':'max-g30-e','Max G2':'max-g2-e','Max G3':'max-g3-e','F2':'f2-e','F2 Plus':'f2-plus-e','F2 Pro':'f2-pro-e','F3':'f3-e','F3 Pro':'f3-pro-e','E2':'e2-e','E2 Plus':'e2-plus-e','E2 Pro':'e2-pro-e','P65':'p65e','P100S':'p100se','GT1':'gt1e','GT2':'gt2p','GT3':'gt3-e','ZT3 Pro':'zt3-pro-e'}
def fixed(row):
 b=row['brand'];model=row['model'];key=row['id'].split(':')[1]
 if b=='Xiaomi' and model in ['M365','M365 Pro','Pro 2','Essential','1S']:u='https://www.mi.com/global/product/'+xiaomi[model].lower()+'/'
 elif b=='Segway Ninebot' and model in seg:u='https://eu-en.segway.com/ekickscooter/products/'+seg[model]+'.html'
 else:return
 h=fetch(u);(out/(key+'.html')).write_text(h);title=re.findall(r'<title>(.*?)</title>',h,re.S);meta=re.findall(r'<meta[^>]+(?:og:image|og:title)[^>]*>',h);print(row['name'],len(h),title[:1],meta[:2],flush=True);return {'name':row['name'],'url':u,'key':key,'title':title,'meta':meta}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=[r for r in ex.map(fixed,rows) if r]
json.dump(results,open(out/'nonshop-fixed.json','w'),indent=2)
