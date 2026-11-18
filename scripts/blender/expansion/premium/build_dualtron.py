"""Rebuild only 23 audited Dualtron exteriors, or four visual-gate representatives."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import build
rs=json.load(open(build.ART/'references.json'));cs=json.load(open(Path(__file__).with_name('configs.json')))
gate={'Dualtron Thunder 3','Dualtron Spider','Dualtron Mini','Dualtron X2'}
for e in rs:
 if not e['name'].startswith('Dualtron'):continue
 if '--gate' in sys.argv and e['name'] not in gate:continue
 if '--remaining' in sys.argv and e['name'] in gate:continue
 build.build(e,cs[e['name']])
print('DUALTRON_REFINEMENT_COMPLETE',flush=True)
