import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import build
parity=int(sys.argv[sys.argv.index('--')+1]);rs=json.load(open(build.ART/'references.json'));cs=json.load(open(Path(__file__).with_name('configs.json')))
for i,e in enumerate(rs):
 if i%2!=parity:continue
 build.build(e,cs[e['name']])
print('PREMIUM_REVISION_DONE',parity,flush=True)
