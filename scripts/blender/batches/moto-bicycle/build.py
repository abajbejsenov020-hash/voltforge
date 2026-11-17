"""19 photo-derived catalog vehicles, X forward/Z up/metres. No manufacturer CAD.
Run Blender -b -t 3 --python scripts/blender/batches/moto-bicycle/build.py [-- key ...]
Source images are packed into every editable .blend. Full batch regenerates manifest.
"""
import bpy, math, json, os, sys
from mathutils import Vector
from math import sin, cos, pi
BASE=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../..'))
MAN=os.path.join(BASE,'apps/web/src/data/blender-moto-bicycle.json')
OUT='moto-bicycle'
GROUPS=['Chassis','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount','Bodywork','Fork','RearSuspension','Drive','Cockpit']
M={}; buckets={}; groups={}
def material(n,c,metal=0,rough=.45):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[n]=m;return n
def mesh(n,vs,fs,m,g='Chassis',smooth=False):
 # Aggregate small manufactured parts by material and semantic mount.
 key=(g,m,smooth); a,b=buckets.setdefault(key,([],[]));k=len(a);a.extend(vs);b.extend(tuple(k+i for i in f) for f in fs)
def box(n,p,d,m,g='Chassis',rot=0):
 vs=[]
 for x,y,z in [(-1,-1,-1),(-1,1,-1),(1,1,-1),(1,-1,-1),(-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)]:
  xx=x*d[0]/2;zz=z*d[2]/2;vs.append((p[0]+xx*cos(rot)+zz*sin(rot),p[1]+y*d[1]/2,p[2]-xx*sin(rot)+zz*cos(rot)))
 mesh(n,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,g)
def cyl(n,a,b,r,m,g='Chassis',N=16,r2=None):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0)))
 if u.length<.01:u=axis.cross(Vector((1,0,0)))
 u.normalize();v=axis.cross(u);vs=[]
 for c,rr in [(a,r),(b,r if r2 is None else r2)]:
  vs += [tuple(c+(u*cos(i*2*pi/N)+v*sin(i*2*pi/N))*rr) for i in range(N)]
 mesh(n,vs,[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))],m,g,True)
def tube(n,pts,r,m,g='Chassis',N=10):
 if 2<len(pts)<10:
  old=[Vector(p) for p in pts];pts=[]
  for i in range(len(old)-1):
   p0,p1,p2,p3=[old[max(0,min(len(old)-1,j))] for j in [i-1,i,i+1,i+2]]
   for k in range(5):
    t=k/5;pts.append(tuple(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)))
  pts.append(tuple(old[-1]))
 vs=[]
 for i,p in enumerate(pts):
  p=Vector(p);axis=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(i-1,0)])
  if axis.length<1e-8:axis=Vector((1,0,0))
  axis.normalize();u=axis.cross(Vector((0,1,0)))
  if u.length<.01:u=axis.cross(Vector((1,0,0)))
  u.normalize();v=axis.cross(u)
  vs.extend(tuple(p+(u*cos(j*2*pi/N)+v*sin(j*2*pi/N))*r) for j in range(N))
 fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(pts)-1) for j in range(N)]
 mesh(n,vs,fs,m,g,True)
def plate(n,poly,y,depth,m,g='Chassis'):
 N=len(poly);vs=[(x,y+d,z) for d in [-depth/2,depth/2] for x,z in poly];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];mesh(n,vs,fs,m,g)
def annulus(n,x,y,z,R,r,m,g,depth=.006,N=72,wave=0):
 vs=[(x+(rad+wave*sin(i*12*2*pi/N))*cos(i*2*pi/N),y+d,z+(rad+wave*sin(i*12*2*pi/N))*sin(i*2*pi/N)) for d in [-depth/2,depth/2] for rad in [R,r] for i in range(N)];fs=[]
 for i in range(N):
  j=(i+1)%N;fs +=[(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)]
 mesh(n,vs,fs,m,g,True)
def loft(n,sections,m,g='Bodywork',y=0):
 old=[Vector(p) for p in sections];sections=[]
 for i in range(len(old)-1):
  p0,p1,p2,p3=[old[max(0,min(len(old)-1,j))] for j in [i-1,i,i+1,i+2]]
  for k in range(5):
   t=k/5;sections.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 sections.append(old[-1]);vs=[];N=12
 for x,z,w,h in sections:
  vs.extend((x,y+max(.002,w)*sin(i*2*pi/N),z+max(.003,h)*.5*cos(i*2*pi/N)) for i in range(N))
 fs=[tuple(range(N-1,-1,-1)),tuple(range((len(sections)-1)*N,len(sections)*N))]+[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(sections)-1) for j in range(N)]
 mesh(n,vs,fs,m,g,True)

def hollow(n,outer,inner,y,d,m):
 def rounding(loop):
  pts=[]
  for i,p in enumerate(loop):
   p=Vector(p);prev=Vector(loop[(i-1)%len(loop)]);nex=Vector(loop[(i+1)%len(loop)]);a=p+(prev-p).normalized()*min(.045,(prev-p).length*.25);b=p+(nex-p).normalized()*min(.045,(nex-p).length*.25)
   for j in range(5):
    t=j/4;pts.append(tuple((1-t)**2*a+2*t*(1-t)*p+t*t*b))
  return pts
 outer,inner=rounding(outer),rounding(inner)
 N=len(outer);vs=[(x,y+dy,z) for dy in [-d/2,d/2] for loop in [outer,inner] for x,z in loop];fs=[]
 for i in range(N):
  j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
 mesh(n,vs,fs,m)
def text(n,word,loc,size,m,side=1):
 c=bpy.data.curves.new(n,'FONT');c.body=word;c.size=size;c.extrude=.0002;c.align_x='CENTER';o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(pi/2 if side<0 else pi/2,0,pi if side>0 else 0);o.data.materials.append(M[m]);o.parent=groups['Bodywork']
def wheel(x,R,w,off,g,tan=False,cast=False,hubmotor=False,accent='steel'):
 z=R;rim=R-(.064 if R>.3 else .055);N=80
 profile=[(rim,-w*.38),(rim+.022,-w*.51),(R-.013,-w*.40),(R-.004,-w*.20),(R-.002,0),(R-.004,w*.20),(R-.013,w*.40),(rim+.022,w*.51),(rim,w*.38)]
 vs=[(x+r*cos(i*2*pi/N),y,z+r*sin(i*2*pi/N)) for r,y in profile for i in range(N)];fs=[(j*N+i,j*N+(i+1)%N,((j+1)%len(profile))*N+(i+1)%N,((j+1)%len(profile))*N+i) for j in range(len(profile)) for i in range(N)];mesh('Tyre carcass',vs,fs,'rubber',g,True)
 if tan:
  for yy in [-w*.485,w*.485]:annulus('Tan sidewall',x,yy,z,R-.025,rim+.006,'tan',g,.002)
 if off:
  for i in range(44):
   for j in range(5):
    a=(i+(j%2)*.5)*2*pi/44;r=R-.003-abs(j-2)*.003
    box('Knobby tread',(x+r*cos(a),(j-2)*w*.18,z+r*sin(a)),(.022,w*.15,.016),'rubber',g,pi/2-a)
 else:
  for i in range(42):
   a=i*2*pi/42
   for side in [-1,1]:tube('Road tread groove',[(x+(R-.001)*cos(a),0,z+(R-.001)*sin(a)),(x+(R-.011)*cos(a+.06),side*w*.34,z+(R-.011)*sin(a+.06))],.0015,'tread',g,5)
 for y in [-w*.30,w*.30]:annulus('Anodized rim lips',x,y,z,rim+.004,rim-.009,'black',g,.008)
 annulus('Rim barrel',x,0,z,rim-.002,rim-.009,'graphite',g,w*.60)
 cyl('Wheel hub',(x,-w*.50,z),(x,w*.50,z),.072 if hubmotor else .032,'red' if accent=='red' else 'graphite',g,32)
 for s in [-1,1]:
  if cast:
   for i in range(6):
    a=i*pi/3;aa=a+.11;tube('Cast six spoke wheel',[(x+.035*cos(a),s*w*.22,z+.035*sin(a)),(x+(rim-.01)*cos(aa),s*w*.21,z+(rim-.01)*sin(aa))],.012,'black',g)
  else:
   for i in range(18):
    a=i*2*pi/18+(pi/18 if s>0 else 0);b=a+(.24 if i%2 else -.24)
    cyl('Cross laced spoke',(x+.03*cos(a),s*w*.43,z+.03*sin(a)),(x+(rim-.006)*cos(b),s*w*.23,z+(rim-.006)*sin(b)),.0014,'steel',g,6)
 yy=w*.58;rr=.112 if R>.3 else .084
 # Perforations separated by narrow bridges.
 for i in range(48):
  a=i*2*pi/48;b=a+2*pi/48*.76
  pts=[(x+r*cos(t),yy,z+r*sin(t)) for r,t in [(rr-.016,a),(rr,a),(rr,b),(rr-.016,b)]];mesh('Ventilated rotor',pts,[(0,1,2,3)],'steel',g)
 for i in range(6):
  a=i*pi/3;cyl('Rotor spider',(x+.025*cos(a),yy,z+.025*sin(a)),(x+(rr-.012)*cos(a+.23),yy,z+(rr-.012)*sin(a+.23)),.006,'steel',g,6)
 box('Hydraulic caliper',(x-.078,yy+.012,z+.069),(.052,.029,.045),'red' if cast else 'graphite',g)
 cyl('Axle',(x,-w*.68,z),(x,w*.68,z),.012,'steel',g,12)
def coil(a,b,r=.032,m='red'):
 a,b=Vector(a),Vector(b);v=b-a;axis=v.normalized();u=Vector((0,1,0));w=axis.cross(u)
 cyl('Shock damper',a,b,r*.57,'steel','RearSuspension');pts=[tuple(a+v*(.06+.88*i/160)+(u*cos(i/160*16*pi)+w*sin(i/160*16*pi))*r) for i in range(161)];tube('Helical coil spring',pts,r*.16,m,'RearSuspension',8)
 for p in [a,b]:cyl('Shock collar',p-axis*.01,p+axis*.01,r*1.08,'graphite','RearSuspension')
def chain(rear,rr,front,fr,y,accent='steel'):
 rx,rz=rear;fx,fz=front;pts=[]
 for i in range(17):
  a=pi/2+i*pi/16;pts.append((rx+rr*cos(a),rz+rr*sin(a)))
 for i in range(17):
  a=-pi/2+i*pi/16;pts.append((fx+fr*cos(a),fz+fr*sin(a)))
 expanded=[]
 for i,p in enumerate(pts):
  q=pts[(i+1)%len(pts)];N=max(1,int(math.dist(p,q)/.014))
  for j in range(N):expanded.append((p[0]+(q[0]-p[0])*j/N,p[1]+(q[1]-p[1])*j/N))
 for i,(x,z) in enumerate(expanded):
  nx,nz=expanded[(i+1)%len(expanded)];a=math.atan2(nz-z,nx-x)
  for yy in [y-.006,y+.006]:box('Chain side plate',(x,yy,z),(.015,.0025,.006),'chain','Drive',-a)
  cyl('Roller pin',(x,y-.007,z),(x,y+.007,z),.0025,'steel','Drive',6)
 for x,z,r in [(rx,rz,rr),(fx,fz,fr)]:
  annulus('Drive sprocket',x,y,z,r,r*.76,accent if x==rx else 'steel','Drive',.007)
  for i in range(8):
   a=i*pi/4;cyl('Sprocket spider',(x+.02*cos(a),y,z+.02*sin(a)),(x+r*.85*cos(a+.12),y,z+r*.85*sin(a+.12)),.005,'steel','Drive',6)
def cockpit(hx,hz,width=.40,bicycle=False,light=False,mirrors=False,handguards=False):
 pts=[(hx+.04,-width,hz+.04),(hx+.02,-width*.54,hz+.045),(hx, -.09,hz-.015),(hx,.09,hz-.015),(hx+.02,width*.54,hz+.045),(hx+.04,width,hz+.04)];tube('Riser handlebar',pts,.012,'graphite','Cockpit')
 for s in [-1,1]:
  cyl('Rubber grip',(hx+.04,s*(width-.115),hz+.04),(hx+.04,s*width,hz+.04),.018,'rubber','Cockpit',24)
  for i in range(10):cyl('Grip ribs',(hx+.04,s*(width-.11+i*.010),hz+.04),(hx+.04,s*(width-.108+i*.010),hz+.04),.019,'black','Cockpit',18)
  tube('Brake lever',[(hx+.07,s*(width-.13),hz+.05),(hx+.10,s*(width-.09),hz+.05),(hx+.10,s*(width-.02),hz+.04)],.004,'steel','Cockpit')
  box('Brake master cylinder',(hx+.04,s*(width-.15),hz+.045),(.042,.048,.025),'black','Cockpit')
  tube('Brake cable',[(hx+.07,s*(width-.13),hz+.025),(hx+.14,s*.18,hz-.12),(hx+.16,s*.11,hz-.30),(hx+.30,s*.08,.46)],.003,'rubber','Cockpit')
  if mirrors:
   tube('Mirror stem',[(hx,s*.27,hz+.07),(hx-.03,s*.32,hz+.25)],.005,'black','Cockpit');loft('Rounded street mirror pod',[(hx-.075,hz+.27,.012,.025),(hx-.04,hz+.27,.036,.05),(hx+.006,hz+.27,.018,.032)],'graphite','Cockpit',y=s*.33)
  if handguards:loft('White handguard',[(hx+.11,hz+.04,.02,.045),(hx+.13,hz+.04,.085,.05),(hx+.10,hz+.06,.11,.04)],'white','Cockpit',y=s*(width-.08))
 box('Digital dash',(hx+.06,0,hz+.028),(.07,.11,.017),'black','Cockpit');box('Dash glass',(hx+.06,0,hz+.038),(.057,.091,.002),'lens','Cockpit')
def curved_panel(n,sections,m,g='Bodywork'):
 # Compound curved plastic shell, variable width and rolled top/bottom edges.
 old=[Vector(p) for p in sections];secs=[]
 for i in range(len(old)-1):
  p0,p1,p2,p3=[old[max(0,min(len(old)-1,j))] for j in [i-1,i,i+1,i+2]]
  for k in range(6):
   t=k/6;secs.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 secs.append(old[-1]);N=9
 for sign in [-1,1]:
  vs=[]
  for back in [0,1]:
   for x,top,bot,wt,wb,bulge in secs:
    for j in range(N):
     t=j/(N-1);yy=wt*(1-t)+wb*t+(bulge-(wt+wb)*.5)*sin(t*pi)
     vs.append((x,sign*(yy-back*.012),top*(1-t)+bot*t))
  L=len(secs);layer=L*N;fs=[]
  for i in range(L-1):
   for j in range(N-1):
    a=i*N+j;b=a+N;fs.extend([(a,b,b+1,a+1),(a+layer,a+1+layer,b+1+layer,b+layer)])
   for j in [0,N-1]:a=i*N+j;b=a+N;fs.append((a,a+layer,b+layer,b))
  for i in [0,L-1]:
   for j in range(N-1):a=i*N+j;fs.append((a,a+1,a+1+layer,a+layer))
  mesh(n,vs,fs,m,g,True)
def mx_body(stark,full,redbody,skoll,factory,key):
 col='red' if redbody else 'graphite';seat=.975 if stark else 1.0
 if skoll:col='black'
 loft('Sculpted foam MX seat',[(-.69,seat+.058,.045,.025),(-.53,seat+.025,.088,.045),(-.30,seat-.005,.093,.050),(-.06,seat+.015,.072,.048),(.14,seat+.075,.044,.034)],'seat')
 loft('Rear tapered MX mudguard',[(-.85 if skoll else -.88,seat+.10,.009,.006),(-.71,seat+.068,.058,.015),(-.48,seat-.01,.09,.021),(-.29,seat-.035,.085,.025)],col)
 if stark:
  curved_panel('Varg compound curved radiator shrouds',[(-.42,.97,.89,.07,.10,.12),(-.26,.965,.855,.065,.12,.15),(-.06,1.01,.82,.05,.12,.16),(.10,1.075,.73,.034,.085,.15),(.24,1.09,.91,.022,.055,.09),(.30,1.065,1.025,.014,.025,.035)],col)
  curved_panel('Varg rolled rear side plastics',[(-.68,1.02,.97,.04,.04,.045),(-.57,.99,.78,.075,.095,.12),(-.45,.96,.64,.087,.08,.12),(-.36,.94,.70,.085,.08,.13),(-.28,.94,.87,.08,.09,.11)],col)
  if factory:curved_panel('Factory white number field',[(-.60,.96,.92,.09,.09,.115),(-.53,.94,.83,.105,.112,.137),(-.44,.92,.79,.105,.105,.139),(-.38,.91,.84,.105,.108,.14)],'white')
 else:
  curved_panel('Arctic compound radiator shrouds',[(-.30,.95,.87,.075,.10,.14),(-.13,1.01,.81,.065,.11,.165),(.07,1.10,.75,.04,.09,.16),(.23,1.10,.92,.025,.06,.10),(.34,1.06,1.02,.018,.022,.03)],col)
  curved_panel('Arctic rear quarter fairing',[(-.67,1.02,.96,.038,.04,.05),(-.56,1.0,.85,.075,.10,.13),(-.38,.96,.63,.09,.08,.14),(-.26,.94,.75,.08,.075,.13),(-.23,.95,.90,.07,.085,.10)],col)
  for sign in [-1,1]:
   plate('Shroud white race graphic',[(.19,1.055),(.11,1.07),(-.10,.98),(-.04,.91),(.08,.82),(.10,.98)],sign*.163,.001,'white' if redbody else 'silvergrey','Bodywork')
   plate('Quarter lightning graphic',[(-.29,.90),(-.59,.97),(-.52,.88),(-.38,.80),(-.35,.71),(-.30,.76)],sign*.142,.001,'white' if redbody else 'silvergrey','Bodywork')
   for j in range(2):plate('Shroud intake slot',[(.08,.99-j*.036),(-.05,.965-j*.036),(-.08,.944-j*.036),(.055,.971-j*.036)],sign*.166,.002,'black','Bodywork')
 for sign in [-1,1]:text('Brand mark','VARG' if stark else 'ARCTIC LEOPARD',(.045,sign*.174,.94),.021,'white',sign)
 # Rounded faceted high voltage casing, tapered belly rather than a rectangular box.
 curved_panel('Contoured high voltage battery',[(-.39,.66,.46,.07,.065,.105),(-.30,.79,.37,.10,.10,.115),(-.12,.86,.335,.105,.105,.13),(.08,.85,.36,.09,.10,.12),(.19,.74,.45,.065,.065,.085)],'black','BatteryMount')
 finpoly=[(.15,.78),(.12,.65),(.035,.39),(-.22,.375),(-.335,.46),(-.34,.65),(-.18,.80)]
 for sign in [-1,1]:
  plate('Cast cooling face',finpoly,sign*.121,.010,'packmetal','BatteryMount')
  # Clip each rib to the polygon so the two triangular cooling zones retain their silhouette.
  for i in range(28):
   z=.39+i*.014;hits=[]
   for j,(x1,z1) in enumerate(finpoly):
    x2,z2=finpoly[(j+1)%len(finpoly)];c1=z1-.14*x1;c2=z2-.14*x2
    if (c1<=z<c2) or (c2<=z<c1):
     t=(z-c1)/(c2-c1);hits.append(x1+t*(x2-x1))
   if len(hits)>=2:
    lo,hi=min(hits)+.005,max(hits)-.005
    if hi>lo:tube('Cast diagonal battery cooling rib',[(lo,sign*.131,z+.14*lo),(hi,sign*.131,z+.14*hi)],.0027,'silvergrey','BatteryMount',6)
  cyl('Diagonal cast chassis spar',(-.32,sign*.145,.40),(.24,sign*.13,.90),.022,'graphite')
  cyl('Rear chassis spar',(-.33,sign*.15,.42),(-.37,sign*.14,.82),.024,'graphite')
  for x,z in [(-.32,.45),(.2,.85),(-.36,.77)]:cyl('Chassis fixing',(x,sign*.14,z),(x,sign*.17,z),.012,'steel','Chassis',6)
 loft('Rounded battery belly skid',[(-.37,.40,.08,.025),(-.30,.35,.115,.055),(-.12,.32,.13,.065),(.07,.37,.11,.055),(.14,.43,.07,.025)],'black','BatteryMount')
 motorcol='graphite' if key=='stark-varg-mx' or skoll else ('silvergrey' if stark else 'graphite')
 cyl('Cast motor housing',(-.25,-.173,.51),(-.25,.173,.51),.10,motorcol,'MotorMount',48)
 for sign in [-1,1]:
  cyl('Motor cover',(-.25,sign*.174,.51),(-.25,sign*.183,.51),.086,motorcol,'MotorMount',48)
  if key.endswith('mx-12') or factory:plate('Revised Varg motor casting',[(-.34,.48),(-.34,.60),(-.29,.70),(-.23,.65),(-.16,.53),(-.17,.44)],sign*.174,.014,motorcol,'MotorMount')
 if not stark:
  for sign in [-1,1]:
   plate('Arctic vented secondary drive casing',[(-.35,.45),(-.34,.56),(-.26,.63),(-.15,.60),(-.11,.51),(-.17,.42)],sign*.187,.016,'graphite','MotorMount')
   for j in range(5):
    x=-.31+j*.026
    tube('Arctic drive cover ventilation slot',[(x,sign*.198,.46),(x+.022,sign*.198,.53)],.0045,'black','MotorMount',8)
 box('Controller behind battery',(.14,0,.60),(.05,.14,.19),'black','ControllerMount')
 return seat

def moto(key):
 stark=key.startswith('stark');full=stark or '-e-xe-' in key;street=('super' in key or '-sm' in key);skoll='skoll' in key;factory='factory' in key;light=('-ex' in key or '-sm' in key or 'l1e' in key or 'l3e' in key or '880-enduro' in key)
 tall=('pro-r' in key or 's-enduro' in key);wb=1.49 if full else (1.34 if tall else 1.30);F=wb/2;R=-F;rf=.305 if street else (.362 if full else (.348 if tall else .325));rr=.315 if street else (.343 if full else .322)
 wheel(F,rf,.11 if street else .085,not street,'FrontWheel',accent='red' if full and not stark else 'steel');wheel(R,rr,.145 if street else .105,not street,'RearWheel',accent='red' if full and not stark else 'steel')
 if full:
  seat=mx_body(stark,full,not skoll and ('880-enduro' in key or 'l3e' in key or stark),skoll,factory,key);hx=.34;hz=1.17
 else:
  lime=key.endswith('xf-pro');pink=key.endswith('xf-pro-super');col='lime' if lime else ('pink' if pink else 'graphite');seat=.91;hx=.30;hz=1.07
  outer=[(.29,.97),(.16,.97),(-.24,.78),(-.27,.37),(-.13,.29),(.01,.31),(.10,.42),(.20,.80)]
  inner=[(.215,.885),(.15,.88),(-.155,.72),(-.177,.43),(-.10,.39),(-.04,.40),(.012,.46),(.115,.76)]
  for s in [-1,1]:
   hollow('Arctic monocoque perimeter frame',outer,inner,s*.115,.040,col)
   for x,z in [(-.18,.40),(.17,.9),(-.20,.73),(-.20,.61)]:cyl('Perimeter frame bolt',(x,s*.135,z),(x,s*.145,z),.008,'steel',N=6)
   tube('Seat support rail',[(.14,s*.08,.94),(-.31,s*.082,.83),(-.62,s*.04,.96)],.016,'graphite')
   plate('Arctic side battery decal',[(-.13,.47),(-.14,.71),(.11,.84),(.05,.57)],s*.099,.002,'silvergrey','BatteryMount')
   for i in range(14):tube('Pack rib',[(-.10+i*.011,s*.104,.47+i*.009),(-.08+i*.011,s*.104,.74+i*.004)],.0018,'black','BatteryMount',5)
   text('Battery brand','ARCTIC',(-.02,s*.109,.68),.027,'white',s)
  plate('Removable rectangular battery',[(-.16,.44),(-.17,.74),(.14,.89),(.18,.78),(.07,.44)],0,.184,'black','BatteryMount')
  loft('Narrow Arctic seat',[(-.53,.93,.037,.023),(-.40,.902,.085,.035),(-.19,.905,.09,.04),(.025,.935,.058,.03)],'seat')
  loft('Long exposed rear blade',[(-.76,.994,.008,.007),(-.55,.95,.04,.013),(-.34,.88,.085,.025),(-.18,.86,.09,.025)],'black')
  cyl('Round Arctic motor',(-.13,-.166,.405),(-.13,.166,.405),.095,'graphite','MotorMount',48)
  for s in [-1,1]:
   annulus('Machined circular motor face',-.13,s*.17,.405,.077,.067,'black','MotorMount')
   for i in range(8):
    a=i*pi/4;cyl('Motor fixing',(-.13+.079*cos(a),s*.17,.405+.079*sin(a)),(-.13+.079*cos(a),s*.178,.405+.079*sin(a)),.004,'steel','MotorMount',6)
  plate('Integrated black finned controller',[(.21,.83),(.25,.80),(.14,.46),(.10,.43),(.11,.50)],0,.145,'black','ControllerMount')
  for i in range(14):
   z=.48+i*.022;x=.13+(z-.48)*.31
   box('Controller cooling fins',(x,0,z),(.012,.152,.004),'graphite','ControllerMount')
  for sign in [-1,1]:
   text('Controller brand','ARCTIC',(.19,sign*.079,.68),.017,'white',sign)
   for j in range(3):tube('Controller circuit face stripe',[(.222-j*.009,sign*.080,.79),(.197-j*.009,sign*.080,.75),(.147-j*.009,sign*.080,.50)],.0012,'silvergrey','ControllerMount',5)
 # Swing arm, visible rear spring, chain and foot controls.
 pivot=(-.21,.43 if full else .405)
 for s in [-1,1]:
  plate('Tapered alloy swingarm',[(pivot[0],pivot[1]+.022),(R-.02,rr+.028),(R-.025,rr-.027),(pivot[0]-.015,pivot[1]-.045)],s*.105,.042,'steel' if full else col,'RearSuspension')
  cyl('Swingarm axle nut',(R,s*.13,rr),(R,s*.15,rr),.014,'steel','RearSuspension',6)
  cyl('Foot control bracket',(-.25,s*.12,.44),(-.24,s*.20,.36),.013,'steel')
  box('Serrated footpeg',(-.245,s*.21,.36),(.085,.07,.02),'steel')
  for i in range(6):box('Peg traction teeth',(-.28+i*.014,s*.238,.375),(.006,.006,.008),'steel')
 coil((-.46,0,.47 if full else .42),(-.31,0,.78 if full else .75),.034,'black' if stark or not full else 'red')
 if not full and ('xe-pro' in key or 'l1e' in key):tube('Rear wheel hugger',[(R+(rr+.025)*cos(a),0,rr+(rr+.025)*sin(a)) for a in [i*pi/36 for i in range(2,18)]],.025,'black','Bodywork',8)
 chain((R,rr),.105,(-.25,.49 if full else .405),.041,-.17,accent='red' if full and not stark else 'steel')
 # Telescopic fork geometry follows rake to the front hub.
 top=(.36,1.12) if full else (.29,1.01)
 for s in [-1,1]:
  low=Vector((F,s*.092,rf));high=Vector((top[0],s*.092,top[1]));v=high-low
  cyl('Fork stanchion',low+v*.20,high,.022,'gold' if stark or (not full and key not in ['arctic-leopard-xe-pro-s','arctic-leopard-xe-l1e']) else 'black','Fork',24)
  cyl('Lower fork leg',low,low+v*.47,.031,'black','Fork',24)
  if full and not stark:loft('White fork protector',[(F-.01,rf,.035,.06),(F-.04,rf+.15,.040,.05),(F-.09,rf+.27,.03,.02)],'white','Fork',y=s*.092)
  for t in [.88,.99]:cyl('Fork clamping collar',low+v*(t-.014),low+v*(t+.014),.032,'graphite','Fork')
  tube('Front hydraulic line',[tuple(low+Vector((-.03,.025,.06))),tuple(low+v*.5+Vector((0,.025,0))),tuple(high+Vector((0,.03,.02)))],.003,'black','Fork')
 for z in [top[1]-.08,top[1]-.015]:box('Triple clamp',(top[0]+.01,0,z),(.077,.27,.026),'graphite','Fork')
 cyl('Steering head',(top[0]-.04,0,top[1]-.13),(top[0]-.09,0,top[1]+.01),.033,'graphite')
 # High mounted curved front mudguard, shorter supermoto road blade.
 zz=.94 if full else .84
 loft('Sculpted front mudguard',[(.33,zz,.067,.025),(.55,zz+.05,.083,.03),(.81,zz+.015,.069,.025),(.99 if full else .90,zz-.075,.023,.008)],'red' if full and not skoll and (stark or '880-enduro' in key or 'l3e' in key) else 'black')
 face='white' if stark and not skoll else ('red' if full and ('880-enduro' in key or 'l3e' in key) else 'black')
 loft('Front number and light cowl',[(.43,zz+.06,.065,.014),(.40,zz+.20,.10,.025),(.35,zz+.33,.089,.018)],face)
 if light:
  lz=zz+(.285 if 'l1e' in key else .17);wy=.055 if 'l1e' in key else (.025 if stark else .045);hh=.012 if 'l1e' in key else (.055 if stark else .05)
  box('Headlamp housing',(.435,0,lz),(.024,wy*2.3,hh*2.25),'black','Bodywork')
  vs=[(.453,wy*cos(i*pi/12),lz+hh*sin(i*pi/12)) for i in range(24)];mesh('Shaped LED headlamp lens',vs,[tuple(range(24))],'lens','Bodywork')
  if 'l1e' in key:
   for j in range(4):cyl('Individual LED emitter',(.454,-.038+j*.025,lz),(.457,-.038+j*.025,lz),.008,'white','Bodywork',12)
  box('Tail light',(-.78,0,seat+.065),(.024,.065,.018),'red','Bodywork')
  tube('Tail plate hanger',[(-.73,0,seat+.06),(-.85,0,seat-.04),(-.86,0,seat-.17)],.008,'black','Bodywork');box('Rear registration plate',(-.87,0,seat-.15),(.012,.14,.10),'white','Bodywork')
 cockpit(hx,hz,.405,light=light,mirrors='l3e' in key,handguards=key.endswith('-ex'))
 tube('High voltage cable',[(.1,.1,.75),(.08,.14,.58),(-.20,.16,.50)],.008,'black','BatteryMount')

def bicycle(key):
 fold='m1-pro' in key;F=.58 if fold else .56;R=-F;rad=.275 if fold else .355;w=.095 if fold else .044;col='teal';wheel(F,rad,w,False,'FrontWheel',tan=fold,cast=fold);wheel(R,rad,w,False,'RearWheel',tan=fold,cast=fold,hubmotor=True)
 bb=(-.13,rad+.045 if fold else .30);sx=-.25;sz=.71 if fold else .76;hx=.43;hz=.79 if fold else .87
 if fold:
  # Hinged low rectangular main beam, full suspension rear triangle.
  plate('Large folding battery beam',[(-.24,.50),(-.26,.61),(.39,.79),(.42,.65)],0,.095,col,'BatteryMount')
  for s in [-1,1]:
   tube('Seat mast',[(bb[0],s*.017,bb[1]),(sx,s*.017,sz)],.026,col)
   for a,b in [((R,s*.055,rad),(-.37,s*.05,.48)),((R,s*.055,rad),(bb[0],s*.03,bb[1])),((-.37,s*.05,.48),(-.29,s*.04,.61))]:cyl('Folding rear triangle',a,b,.015,col)
  coil((-.39,0,.52),(-.29,0,.63),.023,'red')
  box('Central folding hinge',(-.06,0,.62),(.034,.12,.17),'graphite');box('Silver hinge latch',(-.03,-.071,.64),(.11,.022,.02),'steel')
  cyl('Handlebar folding stem',(.43,0,.79),(.38,0,1.03),.021,'teal','Cockpit');hz=1.04;hx=.38
  for s in [-1,1]:cyl('Gold suspension stanchion',(.42,s*.058,.72),(.51,s*.058,.43),.017,'gold','Fork');cyl('Lower fork',(.51,s*.058,.45),(F,s*.058,rad),.022,'black','Fork')
 else:
  # Low step-through: no upper diamond tube. Broad battery downtube plus curved bottom joint.
  for s in [-1,1]:
   tube('Swept low entry frame',[(sx,s*.018,sz),(-.18,s*.018,.38),(-.15,s*.018,.31),(-.03,s*.018,.30),(.10,s*.018,.48),(.36,s*.018,.85)],.027,col)
   cyl('Rear chain stay',(bb[0],s*.038,bb[1]),(R,s*.052,rad),.013,col)
   cyl('Rear seat stay',(sx,s*.025,.62),(R,s*.052,rad),.011,col)
  plate('Step through downtube battery',[(.00,.34),(.09,.35),(.39,.81),(.33,.85)],0,.082,col,'BatteryMount')
  for sign in [-1,1]:
   plate('Dark integrated battery insert',[(.055,.39),(.095,.40),(.352,.80),(.32,.824)],sign*.048,.003,'black','BatteryMount')
   for x,z in [(.213,.613),(.248,.67)]:cyl('Bottle mount threaded boss',(x,sign*.050,z),(x,sign*.056,z),.004,'steel','BatteryMount',12)
  tube('Black integrated battery seam',[(.015,-.047,.36),(.13,-.047,.53),(.35,-.047,.81)],.009,'black','BatteryMount')
  for s in [-1,1]:cyl('Suspension fork upper',(.38,s*.055,.79),(.445,s*.055,.61),.015,'steel','Fork');cyl('Commuter fork lower',(.425,s*.055,.67),(F,s*.055,rad),.022,'graphite','Fork')
  for x in [R,F]:
   tube('Full coverage mudguard',[(x+(rad+.022)*cos(a),0,rad+(rad+.022)*sin(a)) for a in [i*pi/40 for i in range(-3,45)]],.024,'black','Bodywork',8)
  # Rear cargo rack visible in supplied reference, no fabricated basket.
  for s in [-1,1]:
   tube('Rear cargo rack top',[(R-.23,s*.078,.79),(R+.12,s*.078,.79)],.008,'graphite','Bodywork');tube('Rear cargo rack stays',[(R,s*.06,rad+.025),(R-.14,s*.08,.79)],.006,'graphite','Bodywork')
  for i in range(5):cyl('Rear cargo rack crossbar',(R-.22+i*.08,-.08,.79),(R-.22+i*.08,.08,.79),.005,'graphite','Bodywork')
  cyl('Handlebar stem',(.36,0,.84),(.38,0,.98),.020,'graphite','Cockpit');hz=.99;hx=.38
 # Seatpost, realistic separate bicycle saddle.
 cyl('Adjustable seatpost',(sx,0,sz-.05),(sx-.07,0,.90 if fold else 1.00),.016,'graphite','Chassis')
 saddlez=.925 if fold else 1.055
 loft('Bicycle saddle',[(sx-.19,saddlez-.015,.045,.028),(sx-.13,saddlez,.083,.04),(sx-.04,saddlez,.066,.035),(sx+.08,saddlez-.01,.025,.022)],'seat')
 cyl('Pedal spindle',(bb[0],-.14,bb[1]),(bb[0],.14,bb[1]),.017,'steel','Drive')
 for s in [-1,1]:
  p=(bb[0]+s*.16,s*.13,bb[1]+s*.045);cyl('Pedal crank arm',(bb[0],s*.13,bb[1]),p,.013,'graphite','Drive');box('Platform bicycle pedal',(p[0],s*.18,p[2]),(.09,.10,.025),'black','Drive')
  for i in range(4):box('Pedal traction rib',(p[0]-.03+i*.02,s*.18,p[2]+.016),(.004,.1,.005),'steel','Drive')
 chain((R,rad),.060,bb,.10,-.103)
 annulus('Black chainring face',bb[0],-.117,bb[1],.099,.077,'black','Drive',.004)
 for i in range(6):
  a=i*pi/3;cyl('Black chainring spider',(bb[0]+.02*cos(a),-.12,bb[1]+.02*sin(a)),(bb[0]+.09*cos(a+.16),-.12,bb[1]+.09*sin(a+.16)),.008,'black','Drive',8)
 if not fold:
  annulus('Chainring guard',bb[0],-.119,bb[1],.113,.083,'black','Drive',.008)
  plate('Long chain guard',[(R+.05,rad+.055),(bb[0]+.05,bb[1]+.11),(bb[0]+.075,bb[1]+.065),(R+.07,rad+.015)],-.12,.017,'black','Drive')
 cyl('Rear electric hub',(R,-.074,rad),(R,.074,rad),.068,'black','MotorMount',40);box('Bicycle motor controller',(bb[0],0,bb[1]+.10),(.09,.055,.045),'black','ControllerMount')
 tube('Derailleur cage',[(R+.06,-.11,rad),(R+.11,-.12,rad-.10),(R+.07,-.12,rad-.14)],.009,'graphite','Drive')
 for x,z in [(R+.10,rad-.07),(R+.07,rad-.14)]:cyl('Derailleur jockey wheel',(x,-.13,z),(x,-.12,z),.019,'black','Drive',16)
 cockpit(hx,hz,.31,True)
 lampz=rad+(.29 if fold else .44)
 box('Bicycle headlamp',(F-.04,0,lampz),(.055,.05,.04),'black','Bodywork');box('White lamp lens',(F-.01,0,lampz),(.003,.041,.025),'lens','Bodywork')
 tube('Headlamp bracket',[(F-.04,0,lampz-.01),(F-.02,0,rad+.14)],.006,'steel','Bodywork')
 for s in [-1,1]:
  text('Fiido brand','Fiido',(.14 if fold else .235,s*.055,.66 if fold else .62),.065 if fold else .055,'white',s)
  if fold:
   o=bpy.context.scene.objects.get('Fiido brand' if s<0 else 'Fiido brand.001')
   if o:o.rotation_euler.y=-.25
  if not fold:
   o=bpy.context.scene.objects.get('Fiido brand' if s<0 else 'Fiido brand.001')
   if o:o.rotation_euler.y=-.98

def finish_build(entry):
 global buckets,groups,M
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.0
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for d in list(bpy.data.materials):bpy.data.materials.remove(d)
 buckets={};groups={};M={}
 for n,c,mt,r in [('black',(.014,.017,.019),.1,.39),('graphite',(.055,.067,.072),.65,.35),('silvergrey',(.28,.32,.34),.72,.4),('packmetal',(.11,.14,.15),.68,.43),('rubber',(.015,.018,.02),0,.9),('tread',(.032,.037,.04),0,.85),('seat',(.025,.027,.030),0,.91),('steel',(.58,.63,.66),.9,.24),('gold',(.59,.39,.11),.8,.28),('red',(.63,.004,.012),.12,.32),('white',(.85,.87,.88),.05,.35),('lime',(.12,.87,.001),.1,.35),('pink',(.95,.09,.49),.1,.35),('teal',(.002,.15,.145),.58,.33),('tan',(.45,.31,.18),0,.9),('chain',(.44,.38,.20),.8,.37),('lens',(.60,.78,.84),.3,.17)]:material(n,c,mt,r)
 root=bpy.data.objects.new(entry['key'],None);bpy.context.collection.objects.link(root);root['source']=entry['source'];root['reference_image']=entry['image'];root['reconstruction']='Photo based visual reconstruction, not manufacturer CAD';root['units']='metres'
 for n in GROUPS:
  o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.parent=root;groups[n]=o
 if entry['key'].startswith('fiido'):bicycle(entry['key'])
 else:moto(entry['key'])
 for (g,m,smooth),(vs,fs) in buckets.items():
  d=bpy.data.meshes.new(g+' '+m);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(g+' | '+m,d);bpy.context.collection.objects.link(o);o.parent=groups[g];o.data.materials.append(M[m]);o['part_group']=g
  for p in d.polygons:p.use_smooth=smooth and len(p.vertices)==4
  if not smooth and g in {'Chassis','Bodywork','BatteryMount','ControllerMount','RearSuspension','Drive'}:
   mod=o.modifiers.new('Manufactured edge fillets','BEVEL');mod.width=.004 if g!='Bodywork' else .007;mod.segments=3;mod.affect='EDGES';mod.limit_method='ANGLE';mod.angle_limit=.45
   bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
   mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 # Convert brand fonts and preserve names of semantic mounts.
 for o in list(bpy.context.scene.objects):
  if o.type=='FONT':bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
 bpy.context.view_layer.update()
 coords=[o.matrix_world@Vector(c) for o in root.children_recursive if o.type=='MESH' for c in o.bound_box];minz=min(c.z for c in coords)
 # Floor origin; centre longitudinal and lateral axes already at wheelbase midpoint.
 for o in groups.values():o.location.z=-minz
 bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 glb=os.path.join(BASE,'apps/web/public/models/catalog',OUT,entry['key']+'.glb')
 bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True)
 obs=[o for o in root.children_recursive if o.type=='MESH'];tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs)
 entry.update(triangles=tri,meshes=len(obs),bytes=os.path.getsize(glb));json.dump(manifest,open(MAN,'w'),indent=2)
 ref=bpy.data.images.load(os.path.join(BASE,'apps/web/public'+entry['image']),check_existing=True);ref.use_fake_user=True;ref.pack()
 # Neutral studio render, editable blend contains excluded studio rig.
 material('floor',(.70,.72,.74),0,.8);bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));bpy.context.object.name='Studio floor';bpy.context.object.data.materials.append(M['floor'])
 world=bpy.data.worlds.new('Neutral studio');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.68,.74,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
 target=Vector((0,0,.63 if not entry['key'].startswith('fiido') else .58))
 for n,loc,power,size in [('Key',(2,-3,4),500,4),('Rim',(-2,2,3),450,3),('Fill',(3,3,2),230,3)]:
  d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(2.4,-4.2,1.9));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.55 if '-e-xe-' in entry['key'] or entry['key'].startswith('stark') else 2.22
 scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.25;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(BASE,'artifacts/blender/catalog',OUT,entry['key']+'-three-quarter.png')
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,entry['nativeSource']));bpy.ops.render.render(write_still=True)
 proof=dict(entry,dimensions_m=[round(max(c[i] for c in coords)-min(c[i] for c in coords),4) for i in range(3)],floor_min_z=0,semanticNodes=GROUPS,render=scene.render.filepath,referencePacked=True)
 json.dump(proof,open(os.path.join(BASE,'artifacts/blender/catalog',OUT,entry['key']+'-validation.json'),'w'),indent=2)
 print('MODEL_COMPLETE',entry['key'],tri,len(obs),entry['bytes'],flush=True)
def catalog_manifest():
 refs=json.load(open(os.path.join(BASE,'apps/web/src/data/vehicle-references.json')))
 old={r['key']:r for r in json.load(open(MAN))} if os.path.exists(MAN) else {}
 notes={
 'stark-varg-mx':'Red compound curved MX shrouds, dark original motor, white number plate, knobby 21/18-style wheels.',
 'stark-varg-mx-12':'Red Varg plastics; revised silver cast motor case visible in the MX 1.2 reference.',
 'stark-varg-ex':'Red Varg enduro with white handguards, headlamp, rear road equipment and knobby wheels.',
 'stark-varg-sm':'Red Varg supermoto, headlamp, wide smooth road tyres and rear registration hanger.',
 'stark-varg-sm-skoll':'Black Skoll plastics, black light cowl, shorter rear blade and smooth supermoto wheels.',
 'stark-varg-factory-edition':'Red Factory Varg with white rear number fields, revised silver motor casting and gold fork.',
 'arctic-leopard-xf-pro':'Reference lime-green open perimeter monocoque, gold fork and knobby wheels.',
 'arctic-leopard-xf-pro-mx':'Reference graphite XF open perimeter chassis, gold fork, MX number plate and knobbies.',
 'arctic-leopard-xf-pro-super':'Reference bright pink frame and swingarm, gold fork, smooth road tyres.',
 'arctic-leopard-xe-pro-r':'Graphite perimeter frame, larger front enduro wheel, gold fork and rear hugger.',
 'arctic-leopard-xe-pro-s':'Graphite perimeter frame, black fork, compact wheel proportions and rear hugger.',
 'arctic-leopard-xe-pro-s-enduro':'Reference gold-fork Enduro trim with larger knobby front wheel and graphite frame.',
 'arctic-leopard-xe-l1e':'Black fork and graphite chassis with LED headlamp, tail equipment and rear hugger.',
 'arctic-leopard-e-xe-880-enduro':'Full-size red/white radiator fairings, integrated pack, white fork guards and headlamp.',
 'arctic-leopard-e-xe-880-super':'Full-size graphite/grey Super fairings, wide road tyres and white fork guards.',
 'arctic-leopard-e-xe-800-enduro':'Full-size black/grey MX-style Enduro with white fork guards, red shock and knobby wheels.',
 'arctic-leopard-e-xe-l3e':'Full-size red/white road trim, headlamp, mirrors, registration hanger and knobby wheels.',
 'fiido-m1-pro':'Teal folding fat-tyre full-suspension bicycle, tan sidewalls, six-spoke cast wheels, red rear coil, pedals and gold fork.',
 'fiido-c11':'Teal low step-through commuter, dark downtube battery, full fenders, headlamp, rear cargo rack and pedals. Reference has a rack, no basket.',
 }
 rows=[]
 for r in refs:
  if not any(x in r['name'] for x in ['Arctic Leopard','Stark','Fiido']):continue
  key=os.path.splitext(os.path.basename(r['image']))[0]
  family=('fiido-folding' if 'm1-pro' in key else 'fiido-step-through') if key.startswith('fiido') else ('stark-varg' if key.startswith('stark') else ('arctic-fullsize-exe' if '-e-xe-' in key else ('arctic-xf' if '-xf-' in key else 'arctic-xe-pro')))
  rows.append(dict(name=r['name'],key=key,url='/models/catalog/moto-bicycle/'+key+'.glb',source=r['source'],image=r['image'],nativeSource='assets/blender/catalog/moto-bicycle/'+key+'.blend',family=family,variantNote=notes[key]+' Photo-based visual reconstruction; no manufacturer CAD.',triangles=old.get(key,{}).get('triangles',0),meshes=old.get(key,{}).get('meshes',0),bytes=old.get(key,{}).get('bytes',0)))
 return rows
manifest=catalog_manifest();json.dump(manifest,open(MAN,'w'),indent=2)
chosen=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for entry in manifest:
 if not chosen or entry['key'] in chosen:finish_build(entry)
