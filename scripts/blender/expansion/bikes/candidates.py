from source import *
import html
all=[]
for f in sorted(OUT.glob('image-queries-*.json')):
 for q in json.load(open(f)):
  candidates=[]
  for block in q['results'].split('--------------------------------------------------------------------------------'):
   urls=re.findall(r'\((https://[^\n]+)\)',block)
   images=re.findall(r'Image URL: (https://[^\n#]+)',block)
   if urls and images:candidates.append({'source':urls[0],'imageSource':images[0],'text':block.split('Image URL:')[0].strip()})
  all.append({'name':q['name'],'q':q['q'],'candidates':candidates})
json.dump(all,open(OUT/'candidates.json','w'),indent=2)
for q in all:
 print('\n'+q['name'])
 for i,c in enumerate(q['candidates'][:8]):print(i,c['source'])
