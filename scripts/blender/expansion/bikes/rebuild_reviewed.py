import json,subprocess,sys,pathlib,re
BASE=pathlib.Path(__file__).resolve().parents[4];sys.path.insert(0,str(BASE/'scripts/blender/expansion/bikes'));from specs import S
names={'KuKirin X1','Talaria X3','Talaria XXX L1E','Talaria Sting','Talaria Sting MX3','E Ride Pro SS','Sur-Ron Light Bee','Sur-Ron Light Bee S','Arctic Leopard E-16Z','Arctic Leopard E-20Y','Super73 R','Engwe M20','Engwe L20','Aventon Pace 500','Aventon Abound','Himiway Big Dog','Lectric XP 2.0'}
for n,c in S.items():
 if c[0] in ['hardtail','hardtailfat','fullmtb','stepfat','stepcurve','foldstep','cargo']:names.add(n)
keys=[re.sub('[^a-z0-9]+','-',n.lower().replace('+','-plus')).strip('-') for n in names]
print('REVIEWED_REBUILD_COUNT',len(keys),flush=True)
subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','-t','2','--python','scripts/blender/expansion/bikes/build.py','--']+keys,cwd=str(BASE),check=True)
