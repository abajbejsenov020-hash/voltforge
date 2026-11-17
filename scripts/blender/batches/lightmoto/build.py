"""Build all 22 photo-derived lightweight motorcycles.
Blender --background --threads 2 --python scripts/blender/batches/lightmoto/build.py [-- --key slug]
Sources are the existing vehicle-references.json photographs, packed into each native file.
Silhouettes and components are visual reconstructions, not manufacturer CAD or fitment data.
"""
import bpy, os, sys, json, math, re
from mathutils import Vector
from math import sin, cos, pi
HERE=os.path.dirname(os.path.abspath(__file__))
BASE=os.path.abspath(os.path.join(HERE,'../../../..'))
exec(compile(open(os.path.join(HERE,'primitives.py')).read(),'primitives.py','exec'))
MANIFEST=os.path.join(BASE,'apps/web/src/data/blender-lightmoto.json')
rows=json.load(open(MANIFEST))
# family, wheelbase, front radius, rear radius, seat height, bar height, colour, fork colour, body width
specs={
 'talaria-sting-r-mx4':('sting',1.25,.326,.326,.84,1.06,'graphite','black',.105),
 'talaria-sting-pro-mx5':('stingpro',1.25,.326,.326,.86,1.08,'graphite','black',.111),
 'talaria-komodo':('komodo',1.38,.355,.318,.91,1.17,'graphite','black',.124),
 'e-ride-pro-ss-2-0':('eride',1.27,.326,.326,.84,1.055,'graphite','black',.112),
 'e-ride-pro-ss-3-0':('eride3',1.29,.339,.308,.86,1.08,'graphite','black',.116),
 'e-ride-pro-sr':('eridesr',1.32,.350,.318,.89,1.16,'black','black',.125),
 'sur-ron-ultra-bee':('ultra',1.38,.354,.327,.91,1.19,'silver','bronze',.145),
 'sur-ron-storm-bee':('storm',1.43,.360,.333,.94,1.25,'white','bronze',.158),
 'sur-ron-hyper-bee':('hyper',1.00,.257,.223,.66,.85,'black','gold',.095),
 'talaria-xxx':('xxx',1.20,.304,.292,.79,1.04,'black','black',.095),
 'altis-sigma-mx':('sigma',1.28,.339,.308,.85,1.10,'black','gold',.120),
 'talaria-komodo-l3e':('komodo',1.38,.355,.318,.91,1.17,'graphite','gold',.124),
 'talaria-sting-pro-l1e':('stingpro',1.25,.326,.326,.86,1.08,'graphite','black',.111),
 'talaria-junior-et01':('junior',.78,.205,.205,.52,.72,'graphite','silver',.070),
 'e-ride-pro-s':('erides',1.22,.311,.294,.81,1.06,'silver','black',.110),
 'e-ride-pro-4-0':('eride4',1.31,.350,.318,.89,1.16,'graphite','black',.125),
 'e-ride-pro-mini-r':('eridemini',1.15,.292,.263,.76,1.01,'graphite','black',.102),
 'altis-delta-x-dbk':('delta',1.24,.320,.285,.82,1.08,'black','bronze',.119),
 'altis-omega':('omega',1.33,.350,.315,.89,1.17,'black','gold',.130),
 'talaria-komodo-mx':('komodo',1.38,.355,.318,.91,1.17,'graphite','black',.124),
 'talaria-xxx-mx':('xxx',1.20,.304,.292,.79,1.04,'black','black',.095),
 'talaria-sting-pro':('stingpro',1.25,.326,.326,.86,1.08,'graphite','black',.111),
}

def setup(row,cfg):
 global frame,black,rubber,seatmat,silver,darkmetal,gold,lime,chainmat,white,red,lens,root,groups,accent,paint,bronze
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for image in list(bpy.data.images):image.use_fake_user=False
 for data in [bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.images,bpy.data.cameras,bpy.data.lights,bpy.data.worlds]:
  for d in list(data):
   if d.users==0:data.remove(d)
 frame=mat('Cast graphite aluminium',(.055,.062,.065),.72,.32)
 black=mat('Satin black polymer',(.018,.023,.026),.12,.39)
 rubber=mat('Offroad tyre rubber',(.018,.021,.022),0,.88)
 seatmat=mat('Grained charcoal saddle',(.043,.046,.049),0,.84)
 silver=mat('Machined satin aluminium',(.55,.59,.60),.87,.27)
 darkmetal=mat('Anodized gunmetal',(.10,.12,.13),.85,.30)
 gold=mat('Gold fork anodizing',(.66,.40,.09),.82,.23)
 bronze=mat('Bronze fork tubes',(.075,.035,.022),.65,.3)
 lime=mat('Model accent',(.85,.70,.001) if cfg[0] in ['ultra','storm'] else (.80,.001,.19) if cfg[0]=='hyper' else (.73,.76,.72),0,.40)
 accent=lime
 chainmat=mat('Gold roller chain',(.42,.32,.12),.85,.34)
 white=mat('Printed white graphics',(.83,.86,.85),.03,.35)
 red=mat('Red lamp and accents',(.60,.009,.015),.2,.28)
 lens=mat('Headlamp lens',(.72,.84,.9),.45,.15)
 paint={'black':black,'graphite':frame,'silver':silver,'white':white}[cfg[6]]
 root=bpy.data.objects.new(row['name'],None);bpy.context.collection.objects.link(root)
 root['source']=row['source'];root['reference_image']=row['image'];root['reconstruction']='Photo-derived approximate exterior; not manufacturer CAD';root['units']='metres';root['front_axis']='+X'
 groups={}
 for name in ['Chassis','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount','Fork','Cockpit','Bodywork','RearSuspension','Drive']:
  o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=root;groups[name]=o

def textside(label,x,y,z,size,m= None):
 c=bpy.data.curves.new('Printed '+label,'FONT');c.body=label;c.align_x='CENTER';c.size=size;c.extrude=.00015;c.resolution_u=3
 o=bpy.data.objects.new('Printed '+label,c);bpy.context.collection.objects.link(o);o.location=(x,y,z);o.rotation_euler=(pi/2,0,0) if y<0 else (pi/2,0,pi);o.data.materials.append(m or white);o.parent=groups['Bodywork'];return o

def body(row,c):
 family,wb,rf,rr,seat,bar,col,forkcol,bw=c
 X=wb/1.3; Z=seat/.86
 def P(p):return (p[0]*X,p[1]*Z)
 def pts(poly):return [P(p) for p in poly]
 def cp(x,y,z):return (x*X,y,z*Z)
 def pl(name,poly,y,depth,m,g='Chassis',bevel=.006):
  if any(t in name for t in ['side shroud','side shield','battery fairing','power shield']):
   pp=pts(poly);n=len(pp);sgn=1 if y>0 else -1
   cx=sum(p[0] for p in pp)/n;cz=sum(p[1] for p in pp)/n
   vs=[(x,y+sgn*depth*.5,z) for x,z in pp]+[(x,y-sgn*depth*.5,z) for x,z in pp]+[(cx,y+sgn*(depth*.5+.024*Z),cz)]
   fs=[(i,(i+1)%n,2*n) for i in range(n)]+[tuple(range(n,2*n))]+[(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)]
   return mesh(name,vs,fs,m,g,bevel,False)
  return plate(name,pts(poly),y,depth,m,g,bevel)
 def rod(name,a,b,r,m,g='Chassis'):return cyl(name,cp(*a),cp(*b),r,m,g)
 fx,rx=wb/2,-wb/2
 # Wheels use the accepted detailed tread/rotor/spoke construction. Independently sized axles.
 for x,r,g in [(fx,rf,'FrontWheel'),(rx,rr,'RearWheel')]:
  wheel(0,g);groups[g].scale=(r/.313,(1.15 if g=='RearWheel' else 1.0)*(1.14 if family in ['storm','omega'] else 1),r/.313);groups[g].location=(x,0,r-.313*r/.313)
 # Junior uses cast three-spoke wheels; discard cycle spokes and brake spider.
 if family=='junior':
  for g in ['FrontWheel','RearWheel']:
   for o in list(groups[g].children):
    if any(n in o.name for n in ['spoke','Spoke','brake','rotor','Rotor','Caliper','caliper']):bpy.data.objects.remove(o,do_unlink=True)
   for i in range(3):
    a=i*2*pi/3
    left=[];right=[]
    for radius,width in [(.028,.022),(.11,.029),(.24,.018)]:
     angle=a+(radius-.028)*.85;x=radius*cos(angle);z=.313+radius*sin(angle);tx=-sin(angle)*width;tz=cos(angle)*width;left.append((x+tx,z+tz));right.append((x-tx,z-tz))
    plate('Cast three blade wheel spoke',left+list(reversed(right)),0,.032,black,g,.006)
 # Frame profiles traced by eye from each photographed family.
 profiles={
 'sting':([(.29,.87),(.18,.85),(-.18,.65),(-.24,.37),(-.13,.32),(.04,.36),(.16,.68)],[(.21,.79),(.15,.78),(-.12,.60),(-.16,.41),(-.09,.39),(-.02,.43),(.09,.66)]),
 'komodo':([(.30,.88),(.16,.86),(-.20,.66),(-.25,.36),(-.12,.29),(.05,.34),(.19,.67)],[(.21,.80),(.13,.77),(-.14,.60),(-.17,.41),(-.08,.38),(-.01,.41),(.11,.65)]),
 'eride':([(.30,.86),(.16,.86),(-.15,.70),(-.26,.40),(-.20,.31),(-.04,.32),(.09,.49)],[(.21,.79),(.14,.79),(-.09,.66),(-.18,.41),(-.13,.39),(-.07,.41),(.025,.51)]),
 'altis':([(.30,.86),(.13,.87),(-.16,.69),(-.22,.37),(-.11,.30),(.05,.37),(.18,.61)],[(.20,.78),(.11,.78),(-.09,.64),(-.14,.41),(-.07,.39),(-.01,.44),(.10,.62)]),
 'ultra':([(.31,.88),(.17,.88),(-.20,.71),(-.27,.36),(-.17,.28),(.03,.29),(.17,.55)],[(.23,.80),(.15,.80),(-.13,.66),(-.19,.39),(-.12,.36),(-.03,.37),(.10,.55)]),
 'storm':([(.31,.87),(.12,.88),(-.19,.70),(-.29,.36),(-.21,.28),(.03,.28),(.18,.55)],[(.22,.80),(.12,.80),(-.12,.66),(-.20,.40),(-.15,.36),(-.04,.36),(.10,.56)]),
 'hyper':([(.30,.86),(.10,.82),(-.15,.67),(-.27,.38),(-.18,.29),(.04,.29),(.15,.57)],[(.20,.77),(.09,.75),(-.09,.62),(-.18,.41),(-.12,.37),(-.02,.37),(.08,.56)]),
 'xxx':([(.31,.86),(.20,.83),(-.03,.77),(-.19,.40),(-.11,.33),(.01,.37),(.16,.67)],[(.23,.78),(.17,.77),(.02,.72),(-.12,.42),(-.08,.40),(-.04,.44),(.10,.64)]),
 }
 pf='sting' if family.startswith('sting') else 'eride' if family.startswith('eride') else 'altis' if family in ['sigma','delta','omega'] else family
 if family!='junior':
  outer,inner=profiles[pf]
  for s in [-1,1]:hollow('Photo traced open perimeter frame',pts(outer),pts(inner),s*bw,.036 if family not in ['storm','ultra'] else .048,paint)
  rod('Steering head',(.28,0,.78),(.235,0,.94),.035,paint)
 # Battery differs fundamentally for XXX (long horizontal underseat) and youth ET01 (low triangular deck).
 if family=='xxx':
  battery=[(-.57,.74),(-.56,.80),(.13,.86),(.20,.80),(-.05,.71),(-.44,.68)]
 elif family=='junior':battery=[(-.22,.25),(.08,.25),(.20,.44),(.04,.43),(-.08,.33)]
 elif family=='hyper':battery=[(-.015,.40),(-.01,.61),(.14,.75),(.18,.70),(.10,.43),(.06,.36)]
 elif family in ['storm','ultra']:battery=[(-.16,.40),(-.15,.69),(.12,.82),(.19,.76),(.08,.43),(-.04,.36)]
 elif family in ['delta','omega','sigma']:battery=[(-.16,.42),(-.13,.68),(.14,.81),(.20,.76),(.10,.49),(-.03,.37)]
 elif family=='komodo':battery=[(-.13,.43),(-.12,.66),(.17,.82),(.20,.73),(.09,.46),(-.02,.41)]
 else:battery=[(-.14,.43),(-.10,.66),(.15,.82),(.21,.76),(.09,.46),(-.02,.40)]
 pl('Removable model battery enclosure',battery,0,bw*1.7,black,'BatteryMount',.012)
 if family!='junior':
  for s in [-1,1]:
   # Battery side fins follow the pack taper instead of a solid block.
   if family not in ['xxx','hyper']:
    for i in range(4 if family=='komodo' else 3):
     x=-.10+i*.057;pl('Battery vertical moulded rib',[(x,.46),(x+.016,.46),(x+.13,.74),(x+.11,.75)],s*bw*.865,.004,darkmetal,'BatteryMount',.002)
   for x,z in [(-.18,.37),(.257,.82),(-.11,.68)]:
    rod('Frame machined pivot boss',(x,s*bw,z),(x,s*(bw+.027),z),.022,paint)
    rod('Hexagonal fastener',(x,s*(bw+.028),z),(x,s*(bw+.033),z),.009,silver)
  # Dedicated battery top slopes and lift handle, absent from horizontal XXX battery.
  if family!='xxx':
   loft('Battery lid',[(.19*X,.061,.845*Z,.018),(.10*X,bw,.842*Z,.028),(-.09*X,bw*.8,.78*Z,.026)],paint,'BatteryMount',.008)
   path('Recessed battery lifting handle',[cp(.13,-.04,.85),cp(.08,-.065,.88),cp(.015,-.065,.86),cp(-.03,-.04,.82)],.009,darkmetal,'BatteryMount')
 if family=='komodo' and 'l3e' not in row['key']:
  for sy in [-1,1]:
   for iz in range(7):
    for ix in range(7):
     xx=-.105+ix*.032+(iz%2)*.016;zz=.455+iz*.037
     if xx>.10+(zz-.46)*.28:continue
     hexpts=[cp(xx+.015*cos(a*pi/3),sy*(bw*.88+.003),zz+.015*sin(a*pi/3)) for a in range(7)]
     path('Komodo hexagonal pack mesh',hexpts,.0013,darkmetal,'BatteryMount',1)
 if family in ['eride3','eridesr','eride4','eridemini']:
  for sy in [-1,1]:
   for i in range(3 if family=='eride3' else 4):
    xx=-.12+i*.068;zz=.65+i*.037
    rod('E Ride machined side spar bolt',(xx,sy*(bw+.027),zz),(xx,sy*(bw+.038),zz),.006,silver)
   if family=='eridesr':
    pl('SR deep lower power shield',[(-.23,.42),(-.18,.30),(.02,.30),(.10,.46)],sy*(bw+.022),.018,frame,'Bodywork')
 # Mid drive motor with radial bolted covers.
 mx,mz=(-.15,.36) if family!='junior' else (-.15,.29)
 motorR=(.090 if family not in ['storm','ultra','omega','komodo'] else .106)*Z
 cyl('Finned mid drive motor',cp(mx,-bw*1.32,mz),cp(mx,bw*1.32,mz),motorR,frame,'MotorMount',48)
 for s in [-1,1]:
  yy=s*bw*1.35
  cyl('Round motor end cap',cp(mx,yy,mz),cp(mx,yy+s*.009,mz),motorR*.89,black,'MotorMount',48)
  ring('Motor machined annulus',mx*X,yy+s*.010,mz*Z,motorR*.73,motorR*.66,darkmetal,'MotorMount',.004,48)
  for i in range(8):
   a=i*pi/4;xx=mx*X+motorR*.78*cos(a);zz=mz*Z+motorR*.78*sin(a);cyl('Motor case bolt',(xx,yy,zz),(xx,yy+s*.014,zz),.004,silver,'MotorMount',6)
  if family in ['storm','hyper']:
   for i in range(12):
    xx=mx-.065+i*.011;rod('Cast motor cooling rib',(xx,-bw*1.33,mz-.04),(xx,-bw*1.33,mz+.04),.003,darkmetal,'MotorMount')
 if family!='junior':
  pl('Motor skid plate',[(.09,.39),(.06,.28),(-.13,.25),(-.28,.29),(-.27,.34)],0,bw*1.8,black,'MotorMount')
  pl('Front mounted controller',[(.21,.72),(.25,.72),(.13,.43),(.08,.42)],0,bw*1.40,frame,'ControllerMount')
  for i in range(10):rod('Controller cooling fin',(.105+i*.01,-bw*.76,.45+i*.024),(.105+i*.01,bw*.76,.45+i*.024),.004,silver if family=='hyper' else darkmetal,'ControllerMount')
  path('High current cable',[cp(.17,bw,.73),cp(.20,bw*1.1,.62),cp(.09,bw*1.25,.41),cp(mx,bw*1.30,mz)],.008,black,'MotorMount')
 if family=='junior':
  box('Youth compact lower pack controller',cp(.12,0,.35),(.065,.095,.038),black,'ControllerMount',.004)
  for i in range(5):
   box('Youth controller cooling fin',cp(.08+i*.02,0,.382),(.004,.098,.009),darkmetal,'ControllerMount',.001)
 # Tapered swingarm follows actual rear axle height, unlike globally scaling a donor chassis.
 pivot=cp(-.19,0,.39)
 for s in [-1,1]:
  y=s*(bw+.015)
  poly=[(pivot[0]+.02,pivot[2]+.025),(-wb*.30,rr+.07),(rx-.025,rr+.035),(rx-.03,rr-.022),(rx+.05,rr-.034),(-wb*.28,rr+.01),(pivot[0]-.005,pivot[2]-.035)]
  plate('Box section tapered swingarm',poly,y,.030,paint,'RearSuspension',.007)
  cyl('Raised swingarm spine',(pivot[0],y+s*.019,pivot[2]),(rx,y+s*.019,rr),.007,darkmetal,'RearSuspension')
  cyl('Axle slider',(rx-.025,y,rr),(rx+.045,y,rr),.012,silver,'RearSuspension',12)
  if family not in ['junior']:
   for a,b,r in [((-.14,y,.72),(-.51,y,.84),.014),((-.51,y,.84),(-.31,y,.52),.014),((-.31,y,.52),(-.14,y,.72),.011)]:rod('Triangulated rear seat subframe',a,b,r,paint,'RearSuspension')
   peg=box('Serrated alloy footpeg',cp(-.22,s*(bw+.08),.32),(.08*X,.072,.018),silver,bevel=.003)
   for i in range(5):box('Footpeg tooth',cp(-.25+i*.014,s*(bw+.109),.332),(.005,.006,.009),darkmetal,bevel=0)
 if family not in ['junior','xxx']:
  a=Vector(cp(-.36,0,.47));b=Vector(cp(-.20,0,.71));v=b-a;axis=v.normalized();u=Vector((0,1,0));w=axis.cross(u)
  cyl('Rear shock body',a,b,.022,darkmetal,'RearSuspension');cyl('Shock shaft',a-v*.12,b,.009,silver,'RearSuspension')
  pp=[tuple(a+v*(.06+.88*i/160)+(u*cos(i/160*9*2*pi)+w*sin(i/160*9*2*pi))*.030) for i in range(161)]
  path('Visible rear shock wound spring',pp,.0045,red if family in ['delta','sigma','omega'] else gold,'RearSuspension',1)
 elif family=='xxx':
  rod('Low mounted horizontal rear shock',(-.43,0,.43),(-.15,0,.44),.025,darkmetal,'RearSuspension')
 # Roller chain / sprockets.
 if family!='junior':
  y=bw+.035
  ring('Rear chain sprocket',rx,y,rr,.095*Z,.068*Z,red if family=='omega' else darkmetal,'Drive',.007,64)
  for i in range(42):
   a=i*2*pi/42;o=box('Sprocket tooth',(rx+.097*Z*cos(a),y,rr+.097*Z*sin(a)),(.008,.01,.008),silver,'Drive',0);o.rotation_euler.y=-a
  for s in [-1,1]:
   pp=[(rx+.087*Z*cos(pi/2-j*pi/18),y,rr+.087*Z*sin(pi/2-j*pi/18)) for j in range(37)] if False else [(rx,y,rr+s*.091*Z),(pivot[0],y,pivot[2]+s*.034*Z)]
   path('Gold chain upper run' if s==1 else 'Gold chain lower run',pp,.004,chainmat,'Drive',1)
   for i in range(35):
    t=i/34;xx=rx+(pivot[0]-rx)*t;zz=rr+s*.091*Z+(pivot[2]+s*.034*Z-rr-s*.091*Z)*t
    cyl('Roller chain pin',(xx,y-.004,zz),(xx,y+.006,zz),.003,silver,'Drive',6)
 else:
  pl('Enclosed youth chain guard',[(-.65,.32),(-.15,.37),(.015,.30),(-.01,.19),(-.64,.19)],-.071,.027,black,'Drive')
 # Fork and cockpit: front axle to distinct family crown geometry.
 top=cp(.26,0,.97 if family!='junior' else .80)
 for s in [-1,1]:
  y=s*(.083 if family!='junior' else .055);a=Vector((fx,y,rf));b=Vector((top[0],y,top[2]));d=(b-a).normalized();L=(b-a).length
  forkmat={'black':darkmetal,'silver':silver,'gold':gold,'bronze':bronze}[forkcol]
  cyl('USD fork anodized upper',a+d*L*.34,b,.020 if family!='junior' else .013,forkmat,'Fork',32)
  cyl('Cast black fork lower',a-d*.012,a+d*L*.39,.024 if family!='junior' else .017,black,'Fork',32)
  cyl('Fork seal collar',a+d*L*.36,a+d*L*.40,.026,darkmetal,'Fork',24)
  cyl('Front axle lug',(fx,y-.023,rf),(fx,y+.023,rf),.028 if family!='junior' else .018,paint,'Fork',24)
  for t in [.82,.94]:
   p=a+(b-a)*t;cyl('Triple clamp collar',(p.x,y-.028,p.z),(p.x,y+.028,p.z),.027,frame,'Fork',20)
 for t in [.81,.94]:
  p=Vector((fx,0,rf))+(Vector(top)-Vector((fx,0,rf)))*t;box('Forged triple clamp',tuple(p),(.054,.22 if family!='junior' else .15,.023),frame,'Fork',.006)
 bh=bar;hx=top[0]-.02;hw=.30 if family=='hyper' else .37 if family!='junior' else .25
 cyl('Steering stem riser',(top[0],0,top[2]-.03),(hx+.018,0,bh-.057),.018,frame,'Cockpit',24)
 for sy in [-.048,.048]:box('Handlebar clamp',(hx+.018,sy,bh-.049),(.042,.027,.038),frame,'Cockpit',.005)
 path('Swept riser handlebar',[(hx,-hw,bh),(hx-.015,-hw*.55,bh-.018),(hx+.01,-.09,bh-.055),(hx+.018,0,bh-.057),(hx+.01,.09,bh-.055),(hx-.015,hw*.55,bh-.018),(hx,hw,bh)],.011 if family!='junior' else .008,darkmetal,'Cockpit')
 for s in [-1,1]:
  cyl('Rubber handle grip',(hx,s*(hw-.105),bh),(hx,s*(hw+.008),bh),.017 if family!='junior' else .013,rubber,'Cockpit',24)
  for i in range(10):cyl('Grip rib',(hx,s*(hw-.096+i*.010),bh),(hx,s*(hw-.093+i*.010),bh),.018,seatmat,'Cockpit',16)
  box('Brake master cylinder',(hx+.02,s*(hw-.14),bh-.002),(.05,.037,.022),black,'Cockpit',.004)
  path('Curved brake lever',[(hx+.04,s*(hw-.13),bh),(hx+.067,s*(hw-.07),bh-.008),(hx+.062,s*hw,bh)],.0045,silver,'Cockpit')
  path('Front hydraulic brake cable',[(hx+.02,s*(hw-.14),bh),(top[0]+.12,s*.15,bh-.06),(top[0]+.16,s*.09,top[2]-.09),(fx-.04,s*.10,rf+.07)],.003,black,'Cockpit')
 box('Digital display',(hx+.048,0,bh-.03),(.05,.073,.018),black,'Cockpit',.005);box('LCD screen',(hx+.048,0,bh-.019),(.04,.061,.002),lens,'Cockpit',.001)
 # Seat/upper body/fenders.
 if family=='junior':
  # Sloping bicycle-style frame and separate saddle with seatpost.
  for s in [-1,1]:
   y=s*.036;path('Youth low step backbone',[(-.25*X,y,.36*Z),(-.03*X,y,.45*Z),(.26*X,y,.78*Z)],.018,paint)
   rod('Youth diagonal frame tube',(-.08,y,.29),(.26,y,.78),.013,paint)
  rod('Adjustable saddle post',(-.30,0,.34),(-.30,0,.80),.013,silver)
  loft('Contoured narrow saddle',[(-.45*X,.04,seat,.025),(-.35*X,.08,seat+.01,.04),(-.23*X,.07,seat,.04),(-.15*X,.025,seat-.01,.02)],seatmat,'Bodywork')
 else:
  sections=[(-.65*X,.025,seat+.035,.014),(-.56*X,.058,seat+.026,.025),(-.43*X,.077,seat+.005,.050),(-.28*X,.078,seat-.018,.052),(-.16*X,.06,seat-.035,.038),(-.09*X,.032,seat-.028,.022)]
  if family=='xxx':sections=[(-.62*X,.028,seat+.015,.012),(-.52*X,.06,seat+.018,.024),(-.35*X,.075,seat+.01,.035),(-.12*X,.058,seat+.005,.03),(.02*X,.025,seat+.025,.02)]
  if family in ['ultra','storm']:sections=[(x,w*1.22,z,t*1.08) for x,w,z,t in sections]
  loft('Contoured narrow saddle',sections,seatmat,'Bodywork')
  loft('Seat underside structural pan',[(x,w*.90,z-t-.005,.012) for x,w,z,t in sections],black,'Bodywork')
  loft('Long rear fender',[(-.82*X,.006,seat+.055,.005),(-.66*X,.041,seat+.043,.008),(-.48*X,.071,seat-.011,.012),(-.26*X,.062,seat-.052,.013)],white if family in ['hyper','storm'] else black,'Bodywork')
  fz=top[2]-.20*Z
  loft('High front mudguard',[(.25*X,.022,fz-.025,.006),(.42*X,.055,fz,.009),(.61*X,.064,fz+.015,.009),(.81*X,.052,fz+.005,.008),(.92*X,.006,fz-.025,.004)],accent if family=='storm' else white if family=='hyper' else black,'Bodywork')
  loft('Rear tyre splash guard',[(-.24*X,.023,rr+.15,.007),(-.36*X,.047,rr+.25,.007),(-.50*X,.052,rr+.31,.008),(-.63*X,.023,rr+.31,.006)],black,'Bodywork')
 # Family-specific fairings and livery geometry.
 for s in [-1,1]:
  yy=s*(bw+.026)
  if family in ['ultra','storm','hyper','sigma','omega','delta']:
   if family=='storm':
    panel=[(-.53,.80),(-.15,.79),(.12,.82),(.20,.73),(-.04,.66),(-.24,.71)]
   elif family=='hyper':panel=[(-.55,.82),(-.25,.78),(.17,.83),(.12,.69),(-.12,.64),(-.24,.71)]
   elif family in ['sigma','omega','delta']:panel=[(-.52,.81),(-.23,.75),(.17,.83),(.20,.75),(-.02,.67),(-.16,.69)]
   else:panel=[(-.57,.83),(-.23,.77),(.18,.86),(.24,.79),(-.04,.68),(-.21,.70)]
   pl('Sculpted model radiator side shroud',panel,yy,.016,white if family in ['hyper','storm'] else black,'Bodywork',.008)
   if family in ['ultra','storm','hyper']:
    pl('Angular colour livery',[(.14,.81),(.07,.80),(-.04,.73),(-.21,.74),(-.17,.69),(-.02,.69)],s*(bw+.036),.0015,accent,'Bodywork',.0005)
    pl('Rear shroud colour flash',[(-.54,.81),(-.32,.77),(-.27,.74),(-.44,.77)],s*(bw+.037),.0015,accent,'Bodywork',.0005)
   elif family=='delta':
    pl('DBK white rear number graphic',[(-.55,.80),(-.31,.75),(-.18,.70),(-.31,.71)],s*(bw+.038),.0015,white,'Bodywork',.0004)
   else:
    pl('Angular white Altis stripe',[(.18,.82),(.08,.78),(-.02,.73),(.03,.72)],s*(bw+.036),.001,white,'Bodywork',.0002)
    pl('Altis white side spear',[(-.47,.80),(-.30,.76),(-.23,.76),(-.37,.79)],s*(bw+.036),.001,white,'Bodywork',.0002)
   if family in ['delta','omega']:
    pl('Full length polygonal side battery fairing',[(-.13,.66),(.10,.76),(.17,.67),(.08,.49),(-.10,.40),(-.20,.46)],s*(bw+.019),.012,frame,'Bodywork',.006)
  if family.startswith('eride'):
   # E Ride distinctive diagonal side spar across battery aperture.
   pl('E Ride diagonal aperture brace',[(-.17,.43),(-.12,.43),(.17,.67),(.19,.74),(.14,.74)],s*(bw+.021),.018,paint,'Chassis',.006)
   if family=='eride4':pl('4.0 sculpted forward side shield',[(.25,.79),(.15,.80),(-.03,.70),(-.09,.54),(.05,.59),(.14,.69)],s*(bw+.034),.018,frame,'Bodywork')
   textside('E' if family=='eride4' else 'ERIDE',.12*X,s*(bw+.045),.66*Z,.043*Z if family=='eride4' else .023*Z)
  elif family.startswith('sting') or family=='komodo':
   pl('Talaria upper open diagonal rail',[(-.25,.69),(-.21,.65),(.24,.86),(.26,.90)],s*(bw+.025),.020,paint)
   textside('TALARIA',.18*X,s*(bw+.041),.82*Z,.016*Z)
   if 'l1e' in row['key']:
    pl('Road red graphic accent',[(-.11,.69),(-.06,.68),(.03,.58),(-.01,.59)],s*(bw+.039),.001,red,'Bodywork',.0004)
  elif family in ['sigma','delta','omega']:
   textside('dbk' if family=='delta' else 'ALTIS',.04*X,s*(bw+.045),.75*Z,.026*Z)
  elif family in ['ultra','storm','hyper']:textside('SUR-RON',-.38*X,s*(bw+.040),.77*Z,.023*Z)
  elif family=='xxx':textside('XXX',-.28*X,s*(bw+.02),.76*Z,.03*Z)
  elif family=='junior':textside('JUNIOR',-.27*X,s*.087,.37*Z,.023*Z)
 # Lamps distinguish MX number plates and road homologation packages.
 if family not in ['junior']:
  lx=top[0]+.08;lz=top[2]-.045
  if family in ['ultra','storm','hyper','omega','delta','eride4'] or 'l3e' in row['key']:
   plate('Front number and headlamp mask',[(lx,lz+.08),(lx+.035,lz+.065),(lx+.085,lz-.09),(lx+.025,lz-.11)],0,.115,white if family=='storm' else black,'Bodywork',.008)
  if family not in ['hyper','delta','omega']:
   if family in ['ultra','storm'] or 'l3e' in row['key']:
    box('Rectangular LED headlight',(lx+.05,0,lz),(.047,.095,.068),black,'Cockpit',.009);box('Headlight clear lens',(lx+.075,0,lz),(.003,.075,.046),lens,'Cockpit',.005)
   else:
    cyl('Round projector lamp housing',(lx-.012,0,lz),(lx+.04,0,lz),.034,black,'Cockpit',40);cyl('Round LED lens',(lx+.041,0,lz),(lx+.045,0,lz),.027,lens,'Cockpit',40)
  box('Red tail lamp',(-.68*X,0,seat+.015),(.02,.045,.016),red,'Bodywork',.002)
 if 'l1e' in row['key'] or 'l3e' in row['key'] or family in ['ultra','storm']:
  for s in [-1,1]:
   if 'l1e' in row['key'] or 'l3e' in row['key']:
    path('Mirror stem',[(top[0]-.04,s*.24,bar),(top[0]-.03,s*.29,bar+.16)],.005,darkmetal,'Cockpit')
    o=box('Road mirror',(top[0]-.025,s*.29,bar+.18),(.035,.095,.10),black,'Cockpit',.014);box('Mirror glass',(top[0]-.045,s*.29,bar+.18),(.002,.076,.079),silver,'Cockpit',.01)
   box('Amber road reflector',(top[0]+.05,s*.11,top[2]-.13),(.023,.013,.036),gold,'Bodywork',.005)
  pl('Tail number plate carrier',[(-.68,.85),(-.77,.80),(-.80,.72),(-.78,.71),(-.73,.79)],0,.025,black,'Bodywork')
  o=box('Rear registration blank',(-.79*X,0,.74*Z),(.008,.125,.077),black,'Bodywork',.003)
 if family=='ultra':
  for sy in [-1,1]:
   pl('Ultra split diagonal cast frame brace',[(-.19,.68),(-.15,.72),(.12,.48),(.11,.42)],sy*(bw+.033),.028,silver,'Chassis',.008)
   # Curved handguard wraps beyond the ribbed grip and brake lever.
   path('Ultra handguard aluminium spine',[(hx-.005,sy*.36,bh),(hx+.11,sy*.385,bh-.018),(hx+.14,sy*.26,bh-.025),(hx+.085,sy*.19,bh-.03)],.009,black,'Cockpit')
   vs=[(hx+.09,sy*.40,bh+.022),(hx+.15,sy*.34,bh+.028),(hx+.165,sy*.24,bh+.008),(hx+.13,sy*.20,bh-.015),(hx+.11,sy*.27,bh-.055),(hx+.075,sy*.38,bh-.04)]
   mesh('Ultra molded handguard shield',vs,[(0,1,2,3,4,5)],black,'Cockpit',.004,True)
 if family=='storm':
  for sy in [-1,1]:
   aa=Vector((fx,sy*.092,rf));bb=Vector((top[0],sy*.092,top[2]));d=(bb-aa).normalized();L=(bb-aa).length
   poly=[(aa.x-.018,aa.z+.015),(aa.x+.025,aa.z+.025),(aa.x+d.x*L*.39+.025,aa.z+d.z*L*.39),(aa.x+d.x*L*.39-.028,aa.z+d.z*L*.39+.016)]
   plate('Sur-Ron molded lower fork protector',poly,sy*.11,.027,white,'Fork',.006)
   pl('Fork protector livery',[(.60,.35),(.57,.40),(.49,.52),(.50,.54),(.62,.38)],sy*.128,.001,accent,'Fork',.0002)
 if family=='hyper':
  for sy in [-1,1]:
   # White upper wings wrap a black central inset and a broad hot-pink lower insert.
   pl('Hyper black molded shroud inset',[(-.45,.79),(-.23,.75),(.12,.81),(.10,.74),(-.10,.68),(-.25,.70)],sy*(bw+.046),.009,black,'Bodywork',.005)
   pl('Hyper bold pink lower graphic',[(-.19,.70),(.02,.735),(.10,.71),(-.04,.62),(-.13,.65)],sy*(bw+.058),.0015,accent,'Bodywork',.0004)
   pl('Hyper rear pink wing graphic',[(-.54,.81),(-.33,.77),(-.27,.74),(-.44,.765)],sy*(bw+.058),.0015,accent,'Bodywork',.0003)
   # Hot pink stripe follows the rear swingarm forging.
   yy=sy*(bw+.033)
   plate('Hyper swingarm pink stripe',[(rx+.035,rr+.018),(rx+.09,rr+.02),(pivot[0]-.025,pivot[2]-.009),(pivot[0]-.01,pivot[2]-.025)],yy,.0015,accent,'RearSuspension',.0005)
   plate('Hyper white lower fork insert',[(fx-.014,rf+.012),(fx+.009,rf+.02),(fx-.07,rf+.14),(fx-.085,rf+.14)],sy*.108,.002,white,'Fork',.002)
   pl('Hyper mask pink graphic',[(.34,.98),(.355,.96),(.40,.84),(.385,.84)],sy*.058,.0015,accent,'Bodywork',.0004)
  fz=top[2]-.20*Z
  loft('Hyper pink front fender center stripe',[(.30*X,.008,fz-.010,.001),(.43*X,.014,fz+.010,.001),(.61*X,.019,fz+.025,.001),(.81*X,.015,fz+.015,.001),(.90*X,.002,fz-.014,.001)],accent,'Bodywork',.0004)
 if family=='storm':
  for sy in [-1,1]:
   pl('Storm side battery fairing',[(-.21,.70),(-.12,.73),(.11,.79),(.18,.67),(.08,.51),(-.15,.46)],sy*(bw+.018),.022,black,'Bodywork',.009)
   pl('Storm white tank edge',[(.24,.84),(.10,.83),(-.13,.78),(-.17,.73),(.04,.76),(.16,.75)],sy*(bw+.043),.014,white,'Bodywork',.007)
 # Photo-based family labels in native metadata.
 root['family']=family;root['wheelbase_m']=wb;root['seat_height_approx_m']=seat


def export_render(row,c):
 # Bake curves, bevels and normals; combine each semantic group by material.
 bpy.ops.object.select_all(action='DESELECT')
 for o in list(bpy.context.scene.objects):
  if o.type in {'MESH','CURVE','FONT'}:
   bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
 for g,parent in groups.items():
  buckets={}
  for o in list(parent.children):
   if o.type=='MESH':buckets.setdefault(o.data.materials[0].name,[]).append(o)
  for m,obs in buckets.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in obs:o.select_set(True)
   bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=g+' | '+m;obs[0]['part_group']=g
 for o in [o for o in root.children_recursive if o.type=='MESH']:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.context.view_layer.update()
 project_body_livery(root,c[0],c[8],c[4])
 coords=[o.matrix_world @ Vector(corner) for o in root.children_recursive if o.type=='MESH' for corner in o.bound_box]
 floor=min(p.z for p in coords)
 # Root at world origin / floor, geometry offset inside semantic groups.
 for g in groups.values():g.location.z-=floor
 bpy.context.view_layer.update()
 coords=[o.matrix_world @ Vector(corner) for o in root.children_recursive if o.type=='MESH' for corner in o.bound_box]
 dims=[max(p[i] for p in coords)-min(p[i] for p in coords) for i in range(3)]
 ref=bpy.data.images.load(os.path.join(BASE,'apps/web/public'+row['image']),check_existing=True);ref.pack();ref.use_fake_user=True
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 glb=os.path.join(BASE,'apps/web/public'+row['url']);bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True)
 meshes=[o for o in root.children_recursive if o.type=='MESH']
 row.update(triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),meshes=len(meshes),bytes=os.path.getsize(glb))
 row['family']=c[0]
 row['variantNote']=row['variantNote'].split(' Photo-derived')[0]+' Photo-derived visual reconstruction; approximate dimensions, no manufacturer CAD.'
 # Neutral studio stored only in BLEND.
 groundmat=mat('Studio warm grey',(.60,.63,.64),0,.86)
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));ground=bpy.context.object;ground.name='Studio floor (excluded from export)';ground.data.materials.append(groundmat)
 world=bpy.data.worlds.new('Neutral studio');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.76,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
 def area(name,loc,power,size):
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,c[4]*.65))-o.location).to_track_quat('-Z','Y').to_euler()
 area('Key softbox',(1.5,-2.5,3.2),550,3);area('Rim softbox',(-1.6,1.5,2.8),500,2.3);area('Fill',(2,1,2),250,2)
 bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='Three quarter studio camera';bpy.context.scene.camera=camera
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2
 scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
 camera.location=(2.4,4.4,1.9);target=Vector((0,0,dims[2]*.48));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=max(dims[0]*1.16,dims[2]*1.44)
 if c[0] in ['ultra','storm','hyper']:
  scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=-1.5
 scene.render.filepath=os.path.join(BASE,'artifacts/blender/catalog/lightmoto/'+row['key']+'.png');bpy.ops.render.render(write_still=True)
 bpy.context.preferences.filepaths.save_version=0
 # Purge unreferenced data before saving so batch files contain only their own meshes and packed photo.
 for data in [bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.images,bpy.data.cameras,bpy.data.lights,bpy.data.worlds]:
  for d in list(data):
   if d.users==0:data.remove(d)
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,row['nativeSource']),compress=True)
 proof=dict(name=row['name'],key=row['key'],triangles=row['triangles'],meshes=row['meshes'],bytes=row['bytes'],dimensions_m=[round(x,4) for x in dims],wheelbase_m=c[1],floor_offset_m=round(floor,6),packedReference=ref.name)
 json.dump(proof,open(os.path.join(BASE,'artifacts/blender/catalog/lightmoto/'+row['key']+'.json'),'w'),indent=2)
 print('LIGHTMOTO_COMPLETE '+json.dumps(proof),flush=True)
 # Keep current disk manifest, allowing single model rebuilds without discarding other counts.
 current=json.load(open(MANIFEST));current=[row if x['key']==row['key'] else x for x in current];json.dump(current,open(MANIFEST,'w'),indent=2)

only=None
start=None
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:]
 if '--key' in args:only=args[args.index('--key')+1]
 if '--start-from' in args:start=args[args.index('--start-from')+1]
for row in rows:
 if start and row['key']!=start:continue
 start=None
 if only and row['key']!=only:continue
 c=specs[row['key']];setup(row,c);body(row,c);export_render(row,c)
