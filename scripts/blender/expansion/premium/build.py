"""Photographic premium scooter reconstruction; dedicated chassis/suspension families.
Approximate visible exterior, not measured CAD. Internal mount markers are inferred.
"""
import bpy,sys,json,math,importlib.util
from pathlib import Path
from mathutils import Vector
from math import pi,sin,cos
ROOT=Path(__file__).resolve().parents[4];ART=ROOT/'artifacts/blender/expansion/premium';OUT=ROOT/'apps/web/public/models/expansion/premium';NATIVE=ROOT/'assets/blender/expansion/premium'
for d in [ART,OUT,NATIVE]:d.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('premium_primitives',Path(__file__).with_name('primitives.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
# Parameters are audited against each packed reference. Every revision is named explicitly.
def build(e,c):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 p.groups={};p.parts=[]
 materials=dict(black=((.002,.003,.004),.05,.53),edge=((.045,.055,.065),.65,.35),steel=((.10,.12,.14),.72,.33),silver=((.48,.53,.58),.85,.28),rubber=((.019,.022,.025),0,.79),grip=((.025,.029,.031),0,.73),red=((.65,.005,.008),.2,.28),rotor=((.34,.38,.41),.9,.30),lens=((.74,.86,.95),.3,.2),screen=((.005,.018,.022),.35,.14),white=((.7,.75,.79),.2,.4),purple=((.16,.012,.95),.2,.3),orange=((1,.22,.009),.3,.36),gold=((.85,.48,.025),.5,.35))
 for n,(rgb,metal,rough) in materials.items():setattr(p,n,p.mat(n,rgb,metal,rough))
 p.paint=p.mat('Model body finish',tuple(v*.35 for v in c['body']),.16,.48);accent=p.mat('Observed accent',c['accent'],.5,.34);led=p.mat('Flank LED',c.get('led',(.1,.4,1)),.2,.3,1.2)
 root=bpy.data.objects.new(e['name'],None);bpy.context.collection.objects.link(root)
 for n in ['Chassis','Steering','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.parent=root;p.groups[n]=o
 root['source']=e['source'];root['reference']=e['image'];root['accuracy']='Photo-guided exterior; no measured CAD claims. Hidden internal mounts inferred.';root['appearance']=c['notes'];root['frontAxis']='+X';root['units']='metres';root['reconstructionRevision']=2
 r=c['r'];p.R=r;wb=c['wb'];F=wb/2;B=-F;dl=c['dl'];dw=c['dw'];dz=c['dz'];H=c['h'];bar=c['bar'];kind=c['kind'];sx=dl*.48+.07;topx=sx-.14;neck=c.get('neck',.49)
 # Wheels retain distinct tread, rim, motor, and brake detail from the photo.
 tc=dict(r=r,wide=c.get('wide'),dual=c.get('dual',True),tread=c.get('tread','street'),kind='premium')
 p.tire(F,'FrontWheel',tc);p.tire(B,'RearWheel',tc)
 if c.get('dual',True):
  for xx in [F,B]:
   for sy in [-1,1]:p.rod('Closed motor end cover',(xx,sy*(tc.get('wide') or (.044 if r<.14 else .052)),r),(xx,sy*((tc.get('wide') or (.044 if r<.14 else .052))+.003),r),r-.044,p.black,'MotorMount',64)
 if c.get('dual',True):
  hubmat=p.mat('Opaque black motor end plates',(.001,.001,.001),0,1);hubmat.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=0
  wide=tc.get('wide') or (.044 if r<.14 else .052)
  for xx in [F,B]:
   for sy in [-1,1]:p.rod('Motor closed outside face',(xx,sy*(wide+.022),r),(xx,sy*(wide+.024),r),r*.49,hubmat,'MotorMount',64)
 # Shell and pad profiles are family-specific rather than a shared renamed donor.
 if kind in ['apollo','inmotion','nami-compact']:
  pts=[(-dl*.5,dz-.07),(dl*.40,dz-.07),(dl*.54,dz-.035),(dl*.51,dz+.005),(-dl*.46,dz+.008),(-dl*.54,dz-.018)]
 elif kind=='nami':
  pts=[(-dl*.5,dz-.08),(dl*.5,dz-.08),(dl*.5,dz-.014),(-dl*.5,dz-.014)]
 elif kind=='rs5':
  pts=[(-dl*.5-.02,dz-.09),(dl*.5,dz-.09),(dl*.54,dz-.05),(dl*.49,dz+.005),(-dl*.5,dz+.005)]
 else:pts=[(-dl*.5,dz-.08),(dl*.5,dz-.08),(dl*.53,dz-.045),(dl*.5,dz+.005),(-dl*.5,dz+.005)]
 p.profile('Photographed deck extrusion',pts,dw,p.paint,b=.007)
 if kind=='dualtron-x':
  p.cube('X deep rectangular battery chassis',(0,0,dz-.045),(dl,dw,.115),p.paint,b=.009)
  for sy in [-1,1]:p.cube('X inset flanking panel',(0,sy*(dw/2+.003),dz-.045),(dl*.79,.006,.071),p.black,b=.003)
 p.cube('Battery lower tray',(-.025,0,dz-.079),(dl*.95,dw*.90,.016),p.edge,'BatteryMount',.004)
 p.cube('Controller protective housing',(dl*.33,0,dz-.038),(dl*.18,dw*.8,.045),p.black,'ControllerMount',.004)
 p.cube('Rubber standing pad',(0,0,dz+.013),(dl*.94,dw*.93,.014),p.grip,b=.009)
 for j in range(-5,6):p.curve('Deck traction groove',[(-dl*.43,j*dw*.076,dz+.022),(dl*.43,j*dw*.076,dz+.022)],.0008,p.black)
 for x in [-dl*.43,dl*.43]:
  for y in [-dw*.39,dw*.39]:p.bolt('Deck perimeter fastener',(x,y,dz+.024),.003,axis='Z')
 for sy in [-1,1]:
  y=sy*(dw*.5+.003)
  if c.get('rgb'):p.curve('Model flank illumination',[(-dl*.44,y,dz-.04),(dl*.43,y,dz-.04)],.003,led)
  p.label('Deck manufacturer marking',e['name'].split()[0].upper(),(0,y,dz-.032),.021,p.white)
 # Raised rear kickplate occurs only on sport platforms, not compact commuters.
 if c.get('kick',True) and c.get('kickKind')=='brace':
  for sy in [-1,1]:p.window_arm('Open rear carry footbrace',(-dl*.43,dz+.035),(-dl*.64,dz+.145),.017,p.paint,sy*dw*.27)
  p.rod('Rear carry brace end rail',(-dl*.64,-dw*.29,dz+.145),(-dl*.64,dw*.29,dz+.145),.012,p.paint)
 elif c.get('kick',True):
  p.profile('Angled rear foot brace',[(-dl*.47,dz+.017),(-dl*.65,dz+.12),(-dl*.66,dz+.10),(-dl*.49,dz-.008)],dw*.72,p.edge)
  for j in range(5):p.rod('Foot brace traction',(-dl*.50-j*.022,-dw*.29,dz+.045+j*.012),(-dl*.50-j*.022,dw*.29,dz+.045+j*.012),.003,p.grip,n=8)
 # Neck geometry: open welded NAMI tubes, curved cast modern commuters,
 # squared Dualtron hinge, or the characteristic Wolf twin stanchions.
 if c.get('frontFamily') in ['y10','osprey']:
  # Both references fold behind a long twin telescopic fork. No sport C-arm neck.
  for sy in [-1,1]:
   p.profile('YUME low folding chassis cheek',[(dl*.27,dz-.025),(F-.13,dz+.055),(F-.09,dz+.18),(F-.15,dz+.18),(dl*.23,dz+.025)],.017,p.paint,y=sy*.065)
  p.rod('YUME low fold pivot',(F-.14,-.095,dz+.075),(F-.14,.095,dz+.075),.022,p.edge)
 elif kind=='nami':
  for sy in [-1,1]:
   yy=sy*(dw*.5+.012)
   p.curve('NAMI continuous welded deck perimeter tube',[(B+.12,yy,dz+.09),(-dl*.47,yy,dz+.025),(dl*.40,yy,dz+.025),(sx+.10,sy*.055,neck+.07)],.014,p.paint)
   p.curve('NAMI lower side frame rail',[(-dl*.47,yy,dz-.055),(dl*.43,yy,dz-.055),(sx+.10,sy*.055,neck+.07)],.013,p.paint)
   for j in range(4):
    x=-dl*.42+j*dl*.21;p.rod('NAMI triangular side cage brace',(x,yy,dz-.054),(x+dl*.16,yy,dz+.024),.007,p.paint)
  for sy in [-1,1]:
   p.curve('NAMI welded open neck tube',[(dl*.22,sy*dw*.47,dz-.02),(sx+.025,sy*dw*.47,dz+.045),(sx+.12,sy*.065,neck-.035),(sx+.075,sy*.05,neck+.08)],.018,p.paint)
   p.rod('NAMI diagonal tubular brace',(dl*.17,sy*dw*.46,dz+.01),(sx+.095,sy*.052,neck+.07),.015,p.paint)
  p.rod('NAMI head tube bridge',(sx+.075,-.055,neck),(sx+.075,.055,neck),.032,p.edge,'Steering')
 elif kind=='wolf':
  for sy in [-1,1]:p.profile('Wolf long neck side rail',[(dl*.2,dz-.045),(sx+.12,neck-.16),(sx+.16,neck-.09),(sx+.04,dz-.02)],.023,p.paint,y=sy*.07)
 elif kind in ['apollo','inmotion','nami-compact']:
  p.profile('Curved cast headstock',[(dl*.34,dz-.05),(sx+.10,dz+.02),(sx+.14,neck-.13),(sx+.08,neck+.035),(sx+.025,neck+.045),(sx-.025,dz+.05),(dl*.3,dz+.02)],dw*.48,p.paint,b=.014)
 elif kind=='dualtron-x':
  p.profile('X deep integrated headstock',[(dl*.22,dz-.08),(sx+.15,neck-.18),(sx+.145,neck+.06),(sx+.025,neck+.07),(sx-.09,dz+.025)],.12,p.paint,b=.014)
  for sy in [-1,1]:p.profile('X headstock recessed side insert',[(sx-.04,dz+.06),(sx+.105,neck-.10),(sx+.10,neck-.02),(sx+.06,neck-.02)],.006,p.black,y=sy*.063,b=.003)
 elif kind=='inokim':
  p.profile('Inokim sculpted neck',[(dl*.24,dz-.06),(sx+.09,neck-.15),(sx+.07,neck+.055),(sx-.015,neck+.04),(sx-.06,dz+.06)],dw*.4,p.paint,b=.012)
 elif kind=='seated':pass
 else:
  for sy in [-1,1]:
   yy=sy*dw*.19
   p.curve('Open forged headstock side rail',[(dl*.32,yy,dz-.025),(sx+.04,yy,dz+.07),(sx+.08,yy,neck+.005),(sx+.045,yy,neck+.05)],.015,p.paint)
   p.rod('Headstock diagonal brace',(dl*.24,yy,dz+.005),(sx+.045,yy,neck+.035),.012,p.paint)
  p.rod('Upper steering bearing housing',(sx+.045,0,neck-.018),(sx+.045,0,neck+.055),.029,p.edge,'Steering')
 # Distinct front and rear suspensions, with mechanical hinge and spring visibility.
 if c.get('frontFamily') in ['y10','osprey']:
  family=c['frontFamily'];forkTop=c['forkTop'];forkY=.067;topForkX=F-.085
  for sy in [-1,1]:
   yy=sy*forkY
   if family=='y10':
    # Y10: long exposed silver stanchions, short black lowers and bellows.
    p.rod('Y10 long polished front stanchion',(F-.035,yy,r+.16),(topForkX,yy,forkTop),.0155,p.silver,'Steering',32)
    p.rod('Y10 black lower fork leg',(F,yy,r),(F-.035,yy,r+.18),.0225,p.black,'Steering',32)
    for j in range(10):
     z=r+.10+j*.009;xx=F-.035*(z-r)/.18;p.rod('Y10 lower fork rubber bellows',(xx,yy,z-.003),(xx,yy,z+.003),.026,p.grip,'Steering',24)
   else:
    # Osprey: tall dark hydraulic housings, short exposed pistons and cast dropouts.
    p.rod('Osprey long black fork housing',(F-.045,yy,r+.19),(topForkX,yy,forkTop),.022,p.edge,'Steering',32)
    p.rod('Osprey exposed lower piston',(F-.045,yy,r+.055),(F-.045,yy,r+.23),.014,p.silver,'Steering',32)
    p.profile('Osprey short cast axle dropout',[(F-.075,r+.18),(F-.030,r+.15),(F+.018,r+.020),(F-.008,r-.022),(F-.055,r+.015)],.025,p.paint,'Steering',yy)
   for z in [r+.24,forkTop-.012]:
    xx=F-.035+(topForkX-F+.035)*(z-r-.16)/(forkTop-r-.16)
    p.rod('YUME fork collar',(xx,yy,z-.012),(xx,yy,z+.012),.027,p.black,'Steering',32)
   p.bolt('YUME fork top adjuster',(topForkX,yy,forkTop+.021),.009,'Steering',axis='Z')
  for z in [r+.24,forkTop-.005]:
   xx=F-.035+(topForkX-F+.035)*(z-r-.16)/(forkTop-r-.16);p.cube('YUME twin fork crown bridge',(xx,0,z),(.075,.20,.024),p.edge,'Steering',.005)
  p.rod('YUME central lower steering sleeve',(F-.11,0,dz+.08),(topForkX-.015,0,forkTop),.026,p.black,'Steering',32)
  if family=='y10':
   sx=topForkX-.01;topx=topForkX-.10;neck=forkTop
   mid=(forkTop+H)*.54;mx=sx+(topx-sx)*(mid-forkTop)/(H-forkTop)
   p.rod('Y10 lower branded upper mast',(sx,0,forkTop),(mx,0,mid),.025,p.paint,'Steering',32)
   p.rod('Y10 telescopic upper handlebar post',(mx,0,mid),(topx,0,H),.0175,p.black,'Steering',32)
   p.rod('Y10 upper mast telescopic collar',(mx,0,mid-.012),(mx,0,mid+.012),.031,p.edge,'Steering',32)
   p.label('Y10 vertical YUME marking','YUME',((sx+mx)/2,-.027,(forkTop+mid)/2),.025,p.white,'Steering',angle=pi/2+.15)
  else:
   sx=topForkX-.005;topx=F-.075;neck=forkTop
   a=(sx,forkTop+.015);b=(sx-.09,H-.45);d=(topx,H-.035)
   # Two joined, angular open box sections reproduce Osprey's kinked slotted mast.
   for title,u,v in [('Osprey lower reverse-rake mast',a,b),('Osprey upper windowed mast',b,d)]:
    p.window_arm(title,u,v,.087,p.paint,0);p.parts[-1].parent=p.groups['Steering']
   dx=d[0]-b[0];dzm=d[1]-b[1];ll=(dx*dx+dzm*dzm)**.5;nx=dzm/ll;nz=-dx/ll
   for j in range(1,7):
    t=j/7;xx=b[0]+dx*t;zz=b[1]+dzm*t
    p.profile('Osprey mast slot cross web',[(xx-nx*.022,zz-nz*.022-.004),(xx+nx*.022,zz+nz*.022-.004),(xx+nx*.022,zz+nz*.022+.004),(xx-nx*.022,zz-nz*.022+.004)],.087,p.paint,'Steering')
   p.rod('Osprey handlebar mast cap',(topx,0,H-.04),(topx,0,H),.024,p.edge,'Steering',32)
   p.label('Osprey diagonal YUME marking','YUME',((a[0]+b[0])/2,-.046,(a[1]+b[1])/2),.022,p.white,'Steering',angle=pi/2+.35)
  p.cube('YUME paired headlamp cross bracket',(F-.045,0,c['lampZ']-.025),(.11,.21,.020),p.edge,'Steering',.004)
 elif kind=='wolf':
  for sy in [-1,1]:
   y=sy*.075
   p.rod('Wolf upper twin steering tube',(F-.05,y,H-.10),(F-.005,y,neck-.08),.022,accent if c.get('goldFork') else p.steel,'Steering')
   p.rod('Wolf lower structural housing',(F-.02,y,neck+.33),(F-.005,y,neck-.08),.033,p.edge,'Steering')
   for z in [neck+.15,neck+.30,H-.13]:p.rod('Wolf stanchion clamping collar',(F-.025,y,z-.015),(F-.025,y,z+.015),.031,p.black,'Steering')
   p.bolt('Wolf top adjuster',(F-.05,y,H-.075),.009,'Steering',axis='Z')
   p.rod('Wolf lower polished stanchion',(F-.005,y,neck-.10),(F,y,r+.045),.013,p.silver,'Steering')
   p.rod('Wolf fork lower casing',(F,y,r),(F-.005,y,neck-.16),.022,accent if c.get('forkLowerAccent') else p.edge,'Steering')
  for z in [H-.11,neck-.07]:p.cube('Wolf dual crown bridge',(F-.03,0,z),(.10,.21,.027),accent if c.get('crownAccent') else p.edge,'Steering',.007)
  p.cube('Wolf integrated lower headstock',(F-.026,0,neck+.19),(.11,.128,.29),p.paint,'Steering',.012)
  for yy in [-.068,.068]:
   for z in [neck+.10,neck+.18,neck+.26]:p.cube('Wolf headstock cooling rib',(F-.04,yy,z),(.08,.015,.018),p.edge,'Steering',.003)
  for sy in [-1,1]:p.curve('Wolf raised tubular rear kick guard',[(B+.26,sy*.11,dz-.02),(B+.13,sy*.13,dz+.14),(B-.04,sy*.105,dz+.17)],.014,p.edge)
  p.curve('Wolf kick guard rear crossbar',[(B-.04,-.105,dz+.17),(B-.06,0,dz+.17),(B-.04,.105,dz+.17)],.014,p.edge)
  sx=F-.035;topx=sx
  p.rod('Crown handlebar riser',(sx,0,H-.10),(sx,0,H),.021,p.edge,'Steering')
 elif kind=='dualtron-x':
  for sy in [-1,1]:
   p.profile('X massive front trailing arm',[(F-.24,r+.13),(F-.16,r+.11),(F+.04,r+.045),(F+.055,r-.025),(F-.01,r-.035),(F-.235,r+.055)],.032,p.paint,'Steering',sy*.09,b=.006)
  p.shock('X exposed front horizontal coilover',(F-.22,0,r+.205),(F+.015,0,r+.245),.034,p.black)
  p.rod('X front upper shock eye support',(F+.015,0,r+.06),(F+.015,0,r+.245),.015,p.paint,'Steering')
  for sy in [-1,1]:p.rod('X front coilover mounting pin',(F-.22,sy*.015,r+.205),(F-.22,sy*.10,r+.205),.014,p.silver,'Steering')
 elif c.get('fork')=='rigid':
  for sy in [-1,1]:p.curve('Rigid fork blade',[(sx+.06,sy*.05,neck-.10),(F-.04,sy*.054,r+.12),(F,sy*.054,r)],.014,p.paint,'Steering')
 elif c.get('fork')=='telescopic':
  for sy in [-1,1]:
   y=sy*.06;p.rod('Front fork polished stanchion',(sx+.065,y,neck-.08),(F-.02,y,r+.035),.012,p.silver,'Steering');p.rod('Front fork lower leg',(F-.015,y,r+.15),(F,y,r),.020,accent if c.get('forkAccent') else p.paint,'Steering')
 else:
  sides=[-1] if c.get('singleArm') else [-1,1]
  for sy in sides:
   y=sy*.071
   if kind in ['dualtron','inokim']:
    p.profile('C front cartridge swingarm',[(F-.18,r+.13),(F-.14,r+.15),(F+.012,r+.035),(F+.025,r-.017),(F-.026,r-.025),(F-.19,r+.075)],.024,accent if kind=='inokim' else p.paint,'Steering',y)
    p.rod('Elastomer front suspension cartridge',(F-.17,y-.015,r+.11),(F-.17,y+.015,r+.11),.041,p.black,'Steering')
   else:p.window_arm('Leading cast front arm',(F-.19,r+.16),(F,r),.024,accent if c.get('coloredArms') else p.paint,y)
  if kind not in ['dualtron','inokim']:p.shock('Front suspension',(F-.175,0,r+.08),(sx+.08,0,neck-.045),.019,accent)
 if kind=='dualtron-x':
  for sy in [-1,1]:p.profile('X long cast rear swingarm',[(B-.03,r-.025),(B+.04,r-.035),(B+.245,dz-.025),(B+.21,dz+.025),(B+.015,r+.055)],.032,p.paint,y=sy*.09,b=.006)
  p.rod('X rear upper shock eye support',(B-.015,0,r+.055),(B-.015,0,r+.265),.015,p.paint)
  p.shock('X exposed rear horizontal coilover',(B+.23,0,r+.19),(B-.015,0,r+.265),.034,p.black)
 elif c.get('suspension',True):
  sides=[-1] if c.get('singleArm') else [-1,1]
  for sy in sides:
   y=sy*.071
   if kind in ['dualtron','inokim']:
    p.profile('Rear cartridge swingarm',[(B-.018,r-.02),(B+.04,r-.03),(B+.20,r+.12),(B+.16,r+.16),(B+.025,r+.045)],.024,accent if kind=='inokim' else p.paint,y=y)
    p.rod('Rear elastomer suspension cartridge',(B+.17,y-.015,r+.13),(B+.17,y+.015,r+.13),.037,p.black)
   else:p.window_arm('Rear cast swingarm',(B,r),(B+.20,dz-.015),.025,accent if c.get('coloredArms') else p.paint,y)
  if kind not in ['dualtron','inokim']:
   p.shock('Rear suspension',(B+.04,0,r+.045),(B+.25,0,dz+.02),.020,accent)
 else:
  for sy in [-1,1]:p.rod('Rigid rear dropout',(B+.20,sy*.06,dz-.03),(B,sy*.06,r),.014,p.paint)
 # Fenders follow tyre curvature, supported by metal rods.
 p.fender('Front mudguard',F,r+.014,.107,c.get('angular',False),False);p.fender('Rear mudguard',B,r+.014,.111,c.get('angular',False),True)
 if kind=='dualtron-x':
  p.profile('X auxiliary stem battery column',[(sx+.02,neck),(topx-.045,H-.04),(topx+.055,H-.04),(sx+.12,neck)],.115,p.paint,'Steering',b=.012)
  for sy in [-1,1]:p.curve('X stem LED edge',[(sx+.04,sy*.06,neck+.08),(topx,sy*.06,H-.09)],.004,led,'Steering')
 if kind!='wolf' and kind!='seated' and not c.get('frontFamily'):
  if c.get('telescopicStem'):
   mid=(neck+H)*.57;mx=sx+.055+(topx-sx-.055)*(mid-neck)/(H-neck)
   p.rod('Lower telescopic stem barrel',(sx+.055,0,neck),(mx,0,mid),.027,p.paint,'Steering',32)
   p.rod('Upper black telescopic stem',(mx,0,mid),(topx,0,H),.019,p.black,'Steering',32)
   p.rod('Telescopic locking collar',(mx,0,mid-.012),(mx,0,mid+.012),.031,p.edge,'Steering',32)
  elif kind=='rs':
   for sy in [-1,1]:p.rod('RS parallel structural steering beam',(sx+.055,sy*.034,neck),(topx,sy*.034,H),.018,p.edge,'Steering',32)
   for z in [neck+.08,H-.11]:
    x=sx+.055+(topx-sx-.055)*(z-neck)/(H-neck);p.cube('RS paired steering bridge',(x,0,z),(.064,.108,.025),p.paint,'Steering',.005)
  elif kind=='osprey':
   p.window_arm('Osprey tall open cast lower stem',(sx+.05,neck),(topx+.025,H-.30),.055,p.paint,0)
   p.rod('Osprey upper telescopic stem',(topx+.025,0,H-.30),(topx,0,H),.023,p.paint,'Steering')
  else:p.rod('Steering main stem',(sx+.055,0,neck),(topx,0,H),c.get('stemr',.026),p.paint,'Steering',32)
  p.cube('Fold hinge clamp',(sx+.05,0,neck+.035),(.077,.077,.062),p.edge,'Steering',.009)
  p.rod('Fold hinge axle',(sx+.05,-.05,neck+.025),(sx+.05,.05,neck+.025),.014,p.silver,'Steering')
  p.rod('Folding quick lock lever',(sx+.087,-.049,neck+.04),(sx+.08,-.049,neck+.135),.009,accent,'Steering')
  if c.get('rgb'):p.curve('Vertical stem illumination',[(sx+.08,-.005,neck+.11),(topx+.026,-.005,H-.12)],.003,led,'Steering')
  p.label('Stem model marking',e['name'].upper(),(sx+.027,-.029,(neck+H)/2),.020,p.white,'Steering',angle=pi/2+.14)
 # Seated EMOVE RoadRunner is a small open-frame moped silhouette, not a stand-up scooter.
 if kind=='seated':
  seatH=c.get('seatH',.69);frameZ=seatH-.07
  for sy in [-1,1]:
   y=sy*.075
   p.curve('RoadRunner welded chassis upper rail',[(B+.10,y,r+.08),(-.23,y,frameZ),(.18,y,frameZ-.01),(F-.10,y,.68)],.018,p.paint)
   p.curve('RoadRunner welded chassis lower rail',[(B+.10,y,r+.08),(-.28,y,.30),(.16,y,.30),(F-.10,y,.68)],.020,p.paint)
   p.rod('RoadRunner frame diagonal',(-.25,y,.30),(.10,y,frameZ-.02),.015,p.paint)
  p.profile('RoadRunner triangular removable battery',[(-.28,frameZ-.015),(.16,frameZ-.015),(.12,.34),(-.20,.34)],.15,p.edge,'BatteryMount',b=.014)
  p.cube('RoadRunner seat base',(-.17,0,seatH),(c.get('benchLength',.40),.21,.09),p.black,b=.035)
  p.rod('RoadRunner steering riser',(F-.10,0,.60),(F-.18,0,H),.025,p.paint,'Steering')
  for sy in [-1,1]:
   p.rod('Seated scooter front fork',(F-.09,sy*.07,.65),(F,sy*.07,r),.019,p.silver,'Steering');p.rod('Rider foot peg',(.05,sy*.075,.28),(.05,sy*.20,.28),.017,p.grip)
  topx=F-.18
 # Handlebars, rubber grips, levers and routed brake cables.
 p.curve('Swept handlebar',[(topx-.015,-bar*.35,H+.02),(topx-.02,-bar*.12,H),(topx,0,H-.025),(topx-.02,bar*.12,H),(topx-.015,bar*.35,H+.02)],.012,p.edge,'Steering')
 for sy in [-1,1]:
  p.rod('Ribbed rubber grip',(topx-.015,sy*bar*.34,H+.02),(topx-.015,sy*bar*.5,H+.02),.019,p.grip,'Steering',32)
  for j in range(12):
   y=sy*(bar*.345+j*bar*.012);p.rod('Grip molding ring',(topx-.015,y-.001,H+.02),(topx-.015,y+.001,H+.02),.0195,p.black,'Steering',16)
  p.cube('Brake lever reservoir',(topx+.02,sy*bar*.30,H+.026),(.05,.032,.028),p.black,'Steering',.005)
  p.curve('Brake lever blade',[(topx+.047,sy*bar*.30,H+.014),(topx+.065,sy*bar*.38,H+.005),(topx+.06,sy*bar*.46,H+.005)],.004,p.silver,'Steering')
  p.curve('Visible hydraulic cable',[(topx+.027,sy*bar*.28,H+.01),(topx+.11,sy*.10,H-.14),(sx+.09,sy*.055,neck+.03),(F-.10,sy*.08,r+.08)],.003,p.black,'Steering')
 p.cube('Rider LCD console',(topx,0,H+.035),(.082,.110,.023),p.black,'Steering',.009);p.cube('LCD glass',(topx,0,H+.048),(.069,.092,.003),p.screen,'Steering',.005)
 p.label('LCD speed digits','00',(topx-.005,-.017,H+.051),.023,p.white,'Steering')
 if c.get('mirrorRise'):
  for sy in [-1,1]:
   yy=sy*bar*.40;p.curve('Osprey mirror stalk',[(topx,sy*bar*.27,H+.025),(topx+.015,yy,H+.10),(topx,yy,H+c['mirrorRise']-.025)],.004,p.black,'Steering')
   p.cube('Osprey rectangular mirror housing',(topx,yy,H+c['mirrorRise']),(.018,.082,.048),p.black,'Steering',.007)
   p.cube('Osprey silver mirror glass',(topx-.010,yy,H+c['mirrorRise']),(.002,.068,.036),p.silver,'Steering',.004)
 # Model-specific lamp placement, twin beam Wolf/X, high module others, no invented high lamps.
 lamp=c.get('lamp','low');lx=(F+.045 if kind=='wolf' else sx+.10);lz=neck-.045
 if lamp=='high':lx=topx+.045;lz=H-.15
 if lamp=='console':lx=topx+.02;lz=H+.012
 if kind=='dualtron-x':lx=sx+.08;lz=neck+(H-neck)*.42
 count=2 if lamp=='twin' or kind=='wolf' else 1
 if kind=='dualtron-x':count=1
 if c.get('largeCenterLamp'):count=1;lz=neck+.24
 lampR=c.get('lampRadius',.031)
 if c.get('frontFamily'):lx=F+.005;lz=c['lampZ']
 for j in range(count):
  y=(j-(count-1)/2)*(.160 if c.get('frontFamily')=='osprey' else .082)
  if c.get('lampShape')=='square':
   p.cube('Osprey square headlight enclosure',(lx,y,lz),(.042,.050,.046),p.black,'Steering',.006)
   p.rod('Osprey square lamp circular optic',(lx+.022,y,lz),(lx+.024,y,lz),.017,p.lens,'Steering',32)
  else:
   p.rod('Headlight housing',(lx-.02,y,lz),(lx+.017,y,lz),lampR,p.black,'Steering',32)
   if c.get('lampShape')=='round-gold':p.rod('Y10 amber metal lamp bezel',(lx+.018,y,lz),(lx+.021,y,lz),lampR*.96,p.gold,'Steering',32)
   p.rod('Headlight optical lens',(lx+.022,y,lz),(lx+.024,y,lz),lampR*.80,p.lens,'Steering',32)
 p.curve('Side stand',[(-.15,-dw*.48,dz-.07),(-.20,-dw*.78,.018),(-.215,-dw*.80,.008)],.006,p.steel);p.cube('Stand rubber foot',(-.215,-dw*.80,.008),(.03,.024,.014),p.black)
 # Convert and merge by assembly/material; transforms are baked for stable Three.js bounds.
 for o in list(p.parts):
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  if o.type!='MESH':bpy.ops.object.convert(target='MESH')
  for mod in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except RuntimeError:pass
 for parent in p.groups.values():
  buckets={}
  for o in list(parent.children):
   if o.type=='MESH':buckets.setdefault(o.data.materials[0].name,[]).append(o)
  for name,obs in buckets.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in obs:o.select_set(True)
   bpy.context.view_layer.objects.active=obs[0]
   if len(obs)>1:bpy.ops.object.join()
   obs[0].name=parent.name+' | '+name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 model=[o for par in p.groups.values() for o in par.children if o.type=='MESH'];tri=0
 for o in model:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 bounds=[o.matrix_world@Vector(v) for o in model for v in o.bound_box];lo=[min(v[i] for v in bounds) for i in range(3)];hi=[max(v[i] for v in bounds) for i in range(3)]
 assert all(math.isfinite(x) for x in lo+hi);assert lo[2]>-.003,(e['name'],lo)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for par in p.groups.values():
  par.select_set(True)
  for o in par.children:o.select_set(True)
 glb=OUT/(e['key']+'.glb');bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 assert glb.stat().st_size<5000000;assert tri<90000;assert len(model)<55
 im=bpy.data.images.load(str(ROOT/'apps/web/public'/e['image'].lstrip('/')));im.pack();photo=bpy.data.objects.new('REFERENCE exact product photograph',None);bpy.context.collection.objects.link(photo);photo.empty_display_type='IMAGE';photo.data=im;photo.hide_render=True;photo.hide_viewport=True;photo['source']=e['source']
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('STUDIO world');scene.world.color=(.12,.12,.12);scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
 gm=p.mat('STUDIO gray',(.7,.73,.77),0,.9);bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.002));bpy.context.object.name='STUDIO floor';bpy.context.object.data.materials.append(gm)
 for n,loc,power,size in [('Key',(1,-3,4),550,3),('Fill',(-2,-1,2),250,2.5),('Rim',(1.5,2,3),450,2.5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO '+n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,H*.5))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(2.6,-4.4,2.0));cam=bpy.context.object;cam.name='STUDIO camera';cam.rotation_euler=(Vector((0,0,(H+c.get('mirrorRise',0))*.49))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(H+c.get('mirrorRise',0)+.32,wb+r*2+.26);scene.camera=cam;scene.render.filepath=str(ART/(e['key']+'.png'));bpy.ops.render.render(write_still=True)
 bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE/(e['key']+'.blend')),compress=True)
 result=dict(key=e['key'],url='/models/expansion/premium/'+e['key']+'.glb',nativeSource='assets/blender/expansion/premium/'+e['key']+'.blend',triangles=tri,meshes=len(model),bytes=glb.stat().st_size,family=c['family']);json.dump(dict(name=e['name'],model=result,bounds=[lo,hi],observed=c['notes'],revision=2),open(ART/(e['key']+'.json'),'w'),indent=2);print('PREMIUM_COMPLETE',e['key'],tri,len(model),glb.stat().st_size,flush=True)
if __name__=='__main__':
 data=json.load(open(ART/'references.json'));configs=json.load(open(Path(__file__).with_name('configs.json')));selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for e in data:
  if selected and '--force' not in selected and e['key'] not in selected:continue
  if (ART/(e['key']+'.json')).exists() and '--force' not in selected:continue
  build(e,configs[e['name']])
