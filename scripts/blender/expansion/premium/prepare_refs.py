import sys,json,re,io,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];A=ROOT/'artifacts/blender/expansion/premium';P=ROOT/'apps/web/public/assets/vehicles/expansion/premium';sys.path.insert(0,str(Path(__file__).parent));import curate as q
c=json.load(open(A/'candidates.json')); refs={e['name']:e for e in c['candidates']};bad={}
# Source aliases documented in original product titles or on manufacturer pages.
for name,host,handle,note in [
 ('Dualtron Spider','dualtron.uk','dualtron-spider-60v-24-5ah','Original Spider 60V 24.5Ah manufacturer distributor listing; not Spider Max.'),
 ('Dualtron Forever','dualtron.uk','forever-18ah','Original Forever 60V 18.2Ah product; not the later Longbody.'),
 ('Dualtron Mini Special','dualtron.uk','dualtron-mini-long-body-13ah','Mini Special Long Body single-motor 52V 13Ah photographed configuration.'),
 ('Dualtron Victor','dualtron.uk','dualtron-victor-new-24ah','Victor 60V 24Ah photographed revision, distributor exact Victor listing.'),
 ('NAMI Burn-E 2','fluidfreeride.com','nami-burn-e-2','Exact Burn-E 2 product; no substitution with Burn-E 3.'),
 ('NAMI Burn-E 2 Max','fluidfreeride.com','nami-burn-e-open-box-refurbished','Exact named Burn-E 2 Max distributor product reference, refurbished stock listing.'),
 ('Apollo Explore','fluidfreeride.com','apollo-explore-open-box-refurbished','Original Explore, distributor refurbished product reference; not Explore 2.0.'),
 ('Apollo Phantom','fluidfreeride.com','apollo-phantom-v1-open-box-refurbished','Phantom V1 photograph from distributor refurbished listing; not Phantom 2.0.'),
 ]:
 q.catalog(name,host,handle,note);refs[name]=q.refs[name]
# Inokim manufacturer catalog keeps the underlying Light 2 handle with current Max revision.
# The requested Light 2 base remains unresolved until a base-model photograph is found.
for n in ['Hiley Tiger 9']:
 # Manufacturer page combines T9 and T9 Pro, photo cannot establish which motor configuration.
 refs.pop(n,None);bad[n]='Manufacturer product page groups Tiger9 and Tiger9pro; single-motor exterior image identity unverified.'
refs['Vsett 9']['imageSource']=refs['Vsett 9']['imageSource'].replace('http:https:','https:')
# Candidate identities are exact; images still require visual acceptance after download.
def dl(e):
 try:
  url=e['imageSource'];raw=q.get(url);im=Image.open(io.BytesIO(raw));im.load();im=im.convert('RGBA') if im.mode=='P' and 'transparency' in im.info else (im.convert('RGB') if im.mode not in ['RGB','RGBA'] else im)
  assert min(im.size)>=240,(im.size,url)
  im.thumbnail((1100,1100));f=P/(e['key']+'.webp');im.save(f,'WEBP',quality=90);e.update(type='scooter',subtype='scooter',image='/assets/vehicles/expansion/premium/'+f.name,dimensions=list(im.size),bytes=f.stat().st_size,license='Reference photograph; no open redistribution license asserted',referenceKind='manufacturer-product-reference' if any(t in e['source'] for t in ['nami-electric','kaabo.com','inokim','inmotionworld','yumescooter','varlascooter']) else 'distributor-product-reference');return e,None
 except Exception as err:return e,str(err)
if __name__=='__main__':
 result=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for e,err in ex.map(dl,refs.values()):
   if err:bad[e['name']]=err
   else:result.append(e)
 json.dump(result,open(A/'references.json','w'),indent=2);json.dump(bad,open(A/'reference-failures.json','w'),indent=2)
 for page in range((len(result)+19)//20):
  sheet=Image.new('RGB',(1200,1280),'#eceff2');d=ImageDraw.Draw(sheet)
  for i,e in enumerate(result[page*20:(page+1)*20]):
   im=Image.open(P/(e['key']+'.webp')).convert('RGB');im.thumbnail((285,216));x=(i%4)*300;y=(i//4)*256;sheet.paste(im,(x+(300-im.width)//2,y));d.text((x+6,y+222),e['name'],fill='black')
  sheet.save(A/f'references-{page+1}.jpg',quality=90)
 print('REFERENCES',len(result),'FAIL',bad)
