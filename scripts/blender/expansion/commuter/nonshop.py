import subprocess,re,json,concurrent.futures
from pathlib import Path
out=Path('artifacts/blender/expansion/commuter');rows=json.load(open(out/'assigned.json'))
def fetch(u):
 r=subprocess.run(['curl','-L','-s','--fail','--max-time','35','-A','Mozilla/5.0',u],capture_output=True);return r.stdout.decode(errors='replace')
# Keep the exact source HTML to verify title, model and image membership.
xiaomi={'M365':'mi-electric-scooter','M365 Pro':'mi-electric-scooter-pro','Pro 2':'mi-electric-scooter-Pro2','Essential':'mi-electric-scooter-essential','1S':'mi-electric-scooter-1S','Mi 3':'mi-electric-scooter-3','4':'xiaomi-electric-scooter-4','4 Lite':'xiaomi-electric-scooter-4-lite','4 Pro':'xiaomi-electric-scooter-4-pro','4 Ultra':'xiaomi-electric-scooter-4-ultra','5':'xiaomi-electric-scooter-5','5 Pro':'xiaomi-electric-scooter-5-pro','5 Max':'xiaomi-electric-scooter-5-max'}
segway={'Max G30':'ninebot-kickscooter-max-g30','Max G30D':'ninebot-kickscooter-max-g30d','Max G30LP':'ninebot-kickscooter-max-g30le','Max G2':'ninebot-kickscooter-max-g2','Max G3':'ninebot-ekickscooter-max-g3','F2':'ninebot-kickscooter-f2','F2 Pro':'ninebot-kickscooter-f2-pro','F2 Plus':'ninebot-kickscooter-f2-plus','F3':'ninebot-ekickscooter-f3','F3 Pro':'ninebot-ekickscooter-f3-pro','E2':'ninebot-kickscooter-e2','E2 Plus':'ninebot-kickscooter-e2-plus','E2 Pro':'ninebot-kickscooter-e2-pro','ES1':'ninebot-by-segway-kickscooter-es1','ES2':'ninebot-by-segway-kickscooter-es2','ES4':'ninebot-by-segway-kickscooter-es4','P65':'segway-kickscooter-p65','P100S':'segway-kickscooter-p100s','GT1':'segway-superscooter-gt1','GT2':'segway-superscooter-gt2','GT3':'segway-superscooter-gt3','ZT3 Pro':'segway-zt3-pro'}
def job(row):
 b=row['brand'];model=row['model'];key=row['id'].split(':')[1]
 if b=='Xiaomi':u='https://www.mi.com/global/'+('product/' if model in ['Mi 3','4','4 Lite','4 Pro','4 Ultra','5','5 Pro','5 Max'] else '')+xiaomi[model]+'/'
 elif b=='Segway Ninebot':u='https://eu-en.segway.com/products/'+segway[model]
 else:return
 h=fetch(u);(out/(key+'.html')).write_text(h);meta=re.findall(r'<meta[^>]+(?:og:image|og:title)[^>]*>',h);title=re.findall(r'<title>(.*?)</title>',h,re.S);print(row['name'],len(h),title[:1],meta[:2],flush=True)
 return {'name':row['name'],'url':u,'key':key,'title':title,'meta':meta}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=[r for r in ex.map(job,rows) if r]
json.dump(results,open(out/'nonshop.json','w'),indent=2)
