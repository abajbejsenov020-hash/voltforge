import ast,json
from pathlib import Path
O=Path('artifacts/blender/expansion/commuter');p=Path('scripts/blender/expansion/commuter/build.py');tree=ast.parse(p.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='config');exec(compile(ast.Module(body=[fn],type_ignores=[]),str(p),'exec'))
keys=[]
for e in json.load(open(O/'selected.json')):
 f=O/(e['key']+'.json');new=config(e)
 if not f.exists():keys.append(e['key']);continue
 old=json.load(open(f))['parameters'];check={k:v for k,v in new.items() if k in old}
 if old!=check or new['solidArm']:keys.append(e['key'])
print(' '.join(keys))
json.dump(keys,open(O/'rerun-keys.json','w'))
