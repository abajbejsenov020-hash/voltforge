"""Photo-reference exterior reconstructions. Run Blender -b -t 2 --python this_file [-- key ...]."""
import bpy,math,json,os,sys,pathlib
from mathutils import Vector,Matrix
REPO=pathlib.Path(__file__).resolve().parents[4];BASE=str(REPO);HERE=REPO/'scripts/blender/expansion/bikes';OUT=pathlib.Path(BASE)/'artifacts/blender/expansion/bikes'
sys.path.insert(0,str(HERE));from specs import S
# Reuse accepted geometry primitives while leaving their source files and outputs unchanged.
legacy=pathlib.Path(BASE)/'scripts/blender/batches/moto-bicycle/build.py'
primitive_source=legacy.read_text().split('\ndef finish_build')[0].replace("],.012,'black',g)","],.021,'black',g)");primitive_source=primitive_source.replace('for i in range(6):\n    a=i*pi/3;aa=a+.11;', 'for i in range(cast if type(cast)==int else 6):\n    a=i*2*pi/(cast if type(cast)==int else 6);aa=a+.11;');primitive_source=primitive_source.replace('for s in [-1,1]:\n  if cast:', 'for s in [-1,1]:\n  if type(cast)==int and s>0:continue\n  if cast:').replace('s*w*.22','0 if type(cast)==int else s*w*.22').replace('s*w*.21','0 if type(cast)==int else s*w*.21');exec(compile(primitive_source,str(legacy),'exec'))
BASE=str(REPO);OUT=REPO/'artifacts/blender/expansion/bikes'
PALETTE={'blue':(.015,.10,.55),'navy':(.035,.09,.16),'olive':(.23,.28,.12),'green':(.02,.24,.12),'sage':(.30,.43,.36),'grey':(.31,.35,.37),'slate':(.09,.20,.25),'forest':(.045,.09,.065),'yellow':(.7,.74,.02),'orange':(.94,.12,.015),'mint':(.15,.72,.52),'salmon':(.85,.16,.07),'maroon':(.24,.035,.045),'powderblue':(.18,.27,.31)}

def bicycle_photo(e,c):
 family,rad,w,wb,col,motor,susp,rack=c;F=wb/2;R=-F
 fold=family in ['fold','fullfold','thinFold','foldstep'];step=family in ['stepfat','stepcurve','cargo','longtail','foldstep'];moped=family.startswith('moped');full=family in ['fullfold','fullmtb','mopedfull'];road=family in ['road','commuter','cruiser'];cargo=family in ['cargo','longtail'];small=rad<.32
 tan=any(s in e['name'] for s in ['Talon E+','Fiido Air','Aventon Sinch'])
 cast=e['name'].startswith('Engwe') and e['name'] in ['Engwe EP-2 Pro','Engwe Engine Pro','Engwe Engine Pro 2.0','Engwe M20','Engwe L20','Engwe L20 2.0','Engwe X20','Engwe X26'] or e['name'] in ['Fiido T1','Fiido T2','Fiido Titan','Himiway Big Dog','Arctic Leopard E-16Z','Arctic Leopard E-20Y']
 wheel(F,rad,w,not road and e['name'] not in ['Super73 S2','Super73 ZX','Super73 Z Miami'],'FrontWheel',tan=tan,cast=cast);wheel(R,rad,w,not road and e['name'] not in ['Super73 S2','Super73 ZX','Super73 Z Miami'],'RearWheel',tan=tan,cast=cast,hubmotor=motor=='hub')
 bb=(-.12 if not cargo else R+.48,rad+(.045 if small else -.04));sx=bb[0]-.14;sz=.72 if small else .78;hx=F-.18;hz=.81 if small else .90;headbot=(hx+.045,0,hz-.14);headtop=(hx,0,hz)
 if family in ['hardtail','hardtailfat','fullmtb']:sz=.68
 if family=='thinFold':hz=.68;headbot=(hx+.035,0,hz-.14);headtop=(hx,0,hz)
 if family=='fullmtb':hz+=.02;headtop=(hx-.02,0,hz);headbot=(hx+.06,0,hz-.16)
 if family=='cruiser':headtop=(hx-.025,0,hz+.03);hz+=.03
 seatTop=(sx,0,sz)
 # Two lateral rear triangles, leaving an open centre for the chain, tyre and crank.
 for sign in [-1,1]:
  tube('Chain stay',[(bb[0],sign*.042,bb[1]),(R+.12,sign*(w*.65),rad),(R,sign*(w*.65),rad)],.014,col)
  tube('Seat stay',[(R,sign*(w*.65),rad),(R+.13,sign*.05,rad+.18),(sx,sign*.025,sz-.08 if not full else sz-.18)],.012,col,'RearSuspension' if full else 'Chassis')
 cyl('Seat tube',(bb[0],0,bb[1]),seatTop,.025,col)
 if moped:
  # Bench-seat mini-moped chassis. Long seat rails, not a tall bicycle diamond.
  sz=.70;hz=.86;headtop=(hx-.025,0,hz);headbot=(hx+.035,0,hz-.16)
  for sign in [-1,1]:
   tube('Moped perimeter frame',[(R-.03,sign*.07,.73),(R+.26,sign*.065,.72),(hx-.08,sign*.05,.73),(hx-.025,sign*.035,hz)],.019,col)
   tube('Lower cradle',[(R+.16,sign*.07,.58),(bb[0],sign*.07,bb[1]),(hx+.035,sign*.035,hz-.16)],.021,col)
   cyl('Seat rail support',(R+.08,sign*.065,rad+.04),(R+.02,sign*.07,.73),.016,col)
  loft('Long ribbed moped bench',[(R-.16,.775,.055,.04),(R-.07,.785,.115,.065),(R+.36,.785,.12,.067),(R+.48,.78,.065,.05)],'seat')
  if e['name'] in ['Super73 R','Super73 RX'] or e['name']=='Engwe M20':
   loft('Top mounted traction battery',[(-.13,.77,.065,.08),(.03,.77,.09,.13),(.27,.77,.06,.10)],'black','BatteryMount')
  elif e['name']=='Super73 S2':
   plate('S2 diagonal front battery',[(bb[0]+.02,.35),(bb[0]+.13,.36),(.31,.72),(.22,.76)],0,.13,'black','BatteryMount')
  else:plate('Under-seat battery',[(-.31,.57),(.20,.57),(.24,.72),(-.35,.72)],0,.10,'graphite','BatteryMount')
 elif fold and not step:
  # Main hollow hinge beam and tall folding handlepost.
  z=.57 if family!='thinFold' else .62
  if family!='thinFold':
   plate('Angular sloping battery beam',[(sx-.025,z-.055),(sx-.05,z+.055),(hx-.05,hz+.005),(hx+.02,hz-.115)],0,.102,col,'BatteryMount')
   for yy in [-.054,.054]:
    tube('Battery lid seam',[(sx-.015,yy,z+.04),(hx-.06,yy,hz-.005)],.0025,'black','BatteryMount')
    for xx,zz in [(sx+.02,z+.03),(hx-.09,hz-.025)]:cyl('Battery enclosure bolt',(xx,yy,zz),(xx,yy*1.07,zz),.004,'steel','BatteryMount',12)
   tube('Front frame diagonal brace',[(bb[0],0,bb[1]),(hx+.025,0,hz-.14)],.022,col)
   text('Main beam brand',e['name'].split()[0].upper(),((sx+hx)/2+.09,-.059,(z+hz-.075)/2+.012),.046,'white',-1)
   brand=bpy.context.scene.objects.get('Main beam brand');brand.rotation_euler.y=-math.atan2(hz-.075-z,hx-.02-sx)
  else:
   tube('Slim folding beam',[(sx,0,z),(sx+.18,0,z+.025),(hx-.02,0,hz-.075)],.029,col,'Chassis');tube('Fiido lower triangle',[(bb[0],0,bb[1]),(hx+.035,0,hz-.14)],.019,col)
  box('Main folding hinge',((sx+hx)/2,0,(z+hz-.075)/2),(.035,.112,.10),'graphite')
  box('Hinge release lever',((sx+hx)/2+.035,-.066,(z+hz-.075)/2),(.09,.018,.022),'steel')
  if family=='thinFold':
   # Fiido D11/D21 battery is in the oversized removable seatpost.
   cyl('Battery seatpost',(sx,0,.47),(sx-.065,0,.91),.024,'graphite','BatteryMount')
 elif step:
  tube('Curved low-entry frame',[(sx,0,sz),(-.22,0,.38),(bb[0],0,bb[1]),(.22 if family=='cargo' else .02,0,bb[1]+.02),(hx+.035,0,hz-.14),(hx,0,hz)],.028,col)
  if family!='cargo':tube('Low battery beam',[(bb[0],0,bb[1]),(.02,0,bb[1]+.035),headbot],.045 if motor!='pedal' else .025,col,'BatteryMount')
  if e['name']=='Fiido T2':
   tube('T2 upper step-through frame edge',[(bb[0],0,bb[1]+.06),(hx-.01,0,hz-.045)],.023,col)
  if e['name']=='Rad Power RadWagon 4':tube('RadWagon sloping upper triangle',[(sx,0,sz-.10),headtop],.020,col)
  if cargo:
   plate('External seat-tube battery',[(sx-.08,.38),(sx+.01,.38),(sx-.035,.69),(sx-.13,.69)],0,.11,'black','BatteryMount')
  if e['name'] in ['Fiido Titan','Aventon Aventure','Aventon Level','Aventon Level.2']:
   tube('Dipped upper entry frame',[seatTop,(sx+.20,0,sz-.10),headtop],.021,col)
  if motor!='pedal' and not cargo:
   aa=Vector((.01,bb[1]+.035));bb2=Vector((headbot[0],headbot[2]));v=(bb2-aa).normalized();per=Vector((-v.y,v.x));a1=aa-per*.045;a2=aa+per*.045;b1=bb2-per*.038;b2=bb2+per*.038
   plate('Angular integrated step-through pack',[tuple(a1),tuple(b1),tuple(b2),tuple(a2)],0,.085,col,'BatteryMount')
  if family=='foldstep':
   box('Low folding hinge',(.08,0,.46),(.055,.115,.10),'graphite');box('Hinge lock lever',(.10,-.07,.47),(.09,.017,.02),'steel')
 else:
  # Different top tube slopes maintain open frame triangles on road, hardtail and commuter bikes.
  tube('Top tube',[seatTop,((sx+headtop[0])/2,0,sz-.10 if e['name'] in ['Aventon Aventure','Aventon Level','Aventon Level.2','Cube Touring Hybrid'] else (sz+headtop[2])/2),headtop],.022 if family=='road' else .027,col)
  tube('Down tube core',[(bb[0],0,bb[1]),(.08,0,bb[1]+.15),headbot],.025,col,'BatteryMount' if motor!='pedal' else 'Chassis')
  if motor!='pedal':
   aa=Vector((bb[0],bb[1]));bb2=Vector((headbot[0],headbot[2]));v=(bb2-aa).normalized();per=Vector((-v.y,v.x));a1=aa-per*.065;a2=aa+per*.065;b1=bb2-per*.037;b2=bb2+per*.037
   plate('Tapered integrated down-tube battery',[tuple(a1),tuple(b1),tuple(b2),tuple(a2)],0,.084,col,'BatteryMount')
  if motor!='pedal':
   tube('Integrated battery cover seam',[(.04,-.042,bb[1]+.15),(hx+.02,-.042,hz-.17)],.004,'black','BatteryMount')
  if full:
   # Visible pivot, linkage and shock connecting the front frame to rear swingarm.
   shock_a=(sx+.015,0,sz-.075);shock_b=(.10,0,sz+.005)
   if e['name'] in ['Giant Trance X E+','Giant Reign E+','Himiway Cobra']:shock_a=(sx+.055,0,.47);shock_b=(sx+.07,0,.73)
   if e['name'] in ['Trek Rail','Haibike AllMtn']:shock_a=(sx+.065,0,.49);shock_b=(sx+.15,0,.77)
   if e['name']=='Specialized Turbo Kenevo':coil(shock_a,shock_b,.025,'graphite')
   else:
    cyl('Air shock body',shock_a,shock_b,.025,'black','RearSuspension',24);cyl('Air shock piston',shock_a,Vector(shock_a).lerp(Vector(shock_b),.45),.012,'steel','RearSuspension',20)
    for p in [shock_a,shock_b]:cyl('Air shock eyelet',(p[0],-.04,p[2]),(p[0],.04,p[2]),.017,'steel','RearSuspension',16)
   for sign in [-1,1]:cyl('Rocker link',(sx-.08,sign*.05,sz-.17),(sx+.05,sign*.05,sz-.07),.018,'graphite','RearSuspension')
 if full and family!='fullmtb':coil((R+.23,0,rad+.19),(sx+.03,0,sz-.11),.023,'red')
 cyl('Head tube',headbot,headtop,.027,col,'Chassis')
 for sign in [-1,1]:
  a=Vector(headbot)+Vector((0,sign*.055,0));b=Vector((F,sign*(w*.64+.014),rad));mid=a.lerp(b,.48)
  cyl('Fork upper stanchion',a,mid,.016,'steel' if susp else col,'Fork')
  cyl('Fork lower leg',mid+Vector((0,0,.04)),b,.023 if susp else .014,'black' if susp else col,'Fork')
 if e['name'] in ['Engwe X20','Engwe X24','Engwe X26']:
  for sign in [-1,1]:cyl('Dual-crown upper fork tube',(headbot[0],sign*.055,headbot[2]),(headtop[0]-.015,sign*.055,hz+.065),.017,'black','Fork')
  cyl('Upper triple clamp',(headtop[0]-.015,-.075,hz+.025),(headtop[0]-.015,.075,hz+.025),.021,'graphite','Fork')
 cyl('Fork crown',(headbot[0],-.078,headbot[2]),(headbot[0],.078,headbot[2]),.027,'black','Fork')
 if not moped:
  postz=.97 if small else 1.04
  cyl('Telescoping seatpost',(sx,0,sz-.03),(sx-.06,0,postz-.035),.016,'graphite')
  loft('Bicycle saddle',[(sx-.18,postz-.02,.045,.025),(sx-.12,postz,.082,.04),(sx-.02,postz,.065,.035),(sx+.075,postz-.01,.025,.024)],'seat')
 # Stem and grips at reference-appropriate height. Folding bikes have a long lockable handlepost.
 barz=1.10 if fold or cargo else 1.04 if family=='cruiser' or moped else hz+.11
 barx=headtop[0]-.035 if fold or cargo else headtop[0]+.04
 cyl('Handlepost',headtop,(barx,0,barz),.020,'graphite','Cockpit')
 if fold:box('Handlepost hinge',(headtop[0],0,hz+.035),(.052,.045,.045),'black','Cockpit')
 if not e['name'].startswith('Super73'):cockpit(barx,barz,.33 if not moped else .36,True)
 else:
  barz+=.065
  tube('Super73 BMX riser handlebar',[(barx,-.36,barz+.065),(barx,-.24,barz+.065),(barx-.035,-.12,barz-.09),(barx-.035,.12,barz-.09),(barx,.24,barz+.065),(barx,.36,barz+.065)],.013,'black','Cockpit')
  for sy in [-1,1]:
   cyl('Super73 rubber grip',(barx,sy*.25,barz+.065),(barx,sy*.37,barz+.065),.018,'rubber','Cockpit',24);tube('Super73 brake lever',[(barx+.035,sy*.24,barz+.06),(barx+.08,sy*.29,barz+.06),(barx+.08,sy*.35,barz+.055)],.004,'steel','Cockpit');tube('Super73 brake hose',[(barx+.04,sy*.24,barz+.04),(barx+.14,sy*.15,barz-.1),(F-.06,sy*.06,rad+.10)],.003,'black','Cockpit')
 # Real pedals, cranks, chainring, cassette and derailleur remain distinct from electric equipment.
 cyl('Crank spindle',(bb[0],-.14,bb[1]),(bb[0],.14,bb[1]),.017,'steel','Drive')
 for sign in [-1,1]:
  pedal=(bb[0]+sign*.16,sign*.14,bb[1]+sign*.035);cyl('Crank arm',(bb[0],sign*.13,bb[1]),pedal,.013,'graphite','Drive');box('Platform pedal',(pedal[0],sign*.195,pedal[2]),(.10,.10,.025),'black','Drive')
 chain((R,rad),.060,bb,.095,-max(.105,w*.82))
 for i in range(1 if e['name'].startswith('Super73') or e['name'] in ['Fiido Air','Engwe P275 Pro','Lectric XP Lite'] else 7):annulus('Gear cassette',R,-w*.53-i*.004,rad,.065-i*.004,.023,'steel','Drive',.003,N=36)
 if not e['name'].startswith('Super73') and e['name'] not in ['Fiido Air','Engwe P275 Pro','Lectric XP Lite']:
  tube('Derailleur cage',[(R+.05,-.115,rad),(R+.10,-.12,rad-.09),(R+.07,-.12,rad-.14)],.008,'graphite','Drive')
  for z in [rad-.07,rad-.14]:cyl('Jockey wheel',(R+.08,-.13,z),(R+.08,-.115,z),.018,'black','Drive')
 if motor=='hub':cyl('Rear hub motor',(R,-.065,rad),(R,.065,rad),.072,'black','MotorMount',36)
 elif motor=='mid':
  loft('Mid drive housing',[(bb[0]-.15,bb[1]+.035,.045,.14),(bb[0]-.075,bb[1]+.015,.105,.21),(bb[0]+.05,bb[1]+.025,.10,.18),(bb[0]+.13,bb[1]+.06,.055,.10)],'black','MotorMount')
 else:
  cyl('Nonmotorized crank bearing service group',(bb[0],-.04,bb[1]),(bb[0],.04,bb[1]),.028,'graphite','MotorMount');
  for z in [.50,.57]:cyl('Bottle cage boss inferred service group',(.09,-.034,z),(.09,-.042,z),.004,'steel','BatteryMount',10)
 box('Cable junction' if motor=='pedal' else 'Controller service enclosure',(headtop[0]+.02,0,hz-.03),(.05,.045,.028),'black','ControllerMount')
 if rack:
  rackz=rad*2+.075;start=R-.25;end=(sx+.04 if not cargo else R+.38 if family!='longtail' else sx+.18)
  for sign in [-1,1]:
   tube('Rear cargo platform rail',[(start,sign*.11,rackz),(end,sign*.11,rackz)],.009,'graphite','Bodywork');tube('Rack stay',[(R,sign*(w*.65),rad),(start+.06,sign*.11,rackz)],.007,'graphite','Bodywork')
  for i in range(7):cyl('Cargo platform crossbar',(start+(end-start)*i/6,-.11,rackz),(start+(end-start)*i/6,.11,rackz),.006,'graphite','Bodywork')
  if e['name']=='Rad Power RadRunner Plus':loft('Passenger pillion',[(start+.02,rackz+.035,.08,.04),(end-.02,rackz+.035,.12,.065)],'seat')
  if family=='longtail':
   for sign in [-1,1]:tube('Longtail upper cargo frame',[(R-.23,sign*.105,rackz),(sx+.17,sign*.105,rackz),(sx+.12,sign*.055,bb[1]+.08)],.016,col,'Bodywork')
   for sign in [-1,1]:
    tube('Longtail running board',[(R-.25,sign*.17,rad+.12),(R+.36,sign*.17,rad+.12)],.015,'black','Bodywork');tube('Longtail support triangle',[(R-.20,sign*.11,rackz),(R+.40,sign*.11,rackz),(R+.18,sign*.08,rad+.12)],.012,col,'Bodywork')
 if e['name']=='Cannondale Adventure Neo':
  M['seat'].diffuse_color=(.28,.14,.065,1);M['seat'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.28,.14,.065,1)
 if e['name']=='Lectric XPeak':
  for sy in [-1,1]:plate('XPeak visible black removable pack insert',[(.005,.40),(.067,.39),(.36,.72),(.31,.76)],sy*.049,.004,'black','BatteryMount')
  cyl('XPeak stock headlamp',(headtop[0]+.05,0,hz-.04),(headtop[0]+.095,0,hz-.04),.027,'black','Bodywork',24);cyl('XPeak lamp lens',(headtop[0]+.096,0,hz-.04),(headtop[0]+.100,0,hz-.04),.022,'lens','Bodywork',24)
 if e['name']=='Lectric XPedition':
  plate('XPedition second behind-seat battery',[(sx-.21,.38),(sx-.12,.38),(sx-.12,.70),(sx-.21,.70)],0,.11,'black','BatteryMount')
  aa=Vector((bb[0],bb[1]));bb2=Vector((headbot[0],headbot[2]));v=(bb2-aa).normalized();per=Vector((-v.y,v.x));a1=aa-per*.045;a2=aa+per*.045;b1=bb2-per*.042;b2=bb2+per*.042
  plate('XPedition broad structural front tube',[tuple(a1),tuple(b1),tuple(b2),tuple(a2)],0,.08,'white','Chassis')
 if e['name']=='Lectric XP 2.0':
  for xx,zz,L,W in [(R-.03,rad*2+.09,.44,.29),(F-.04,hz-.02,.35,.26)]:
   for yy in [-W/2,W/2]:
    tube('XP2 cargo basket rectangle',[(xx-L/2,yy,zz),(xx+L/2,yy,zz),(xx+L/2,yy,zz+.16),(xx-L/2,yy,zz+.16),(xx-L/2,yy,zz)],.006,'black','Bodywork')
    for k in range(5):cyl('XP2 basket vertical wire',(xx-L/2+k*L/4,yy,zz),(xx-L/2+k*L/4,yy,zz+.16),.004,'black','Bodywork')
   for dz in [0,.08,.16]:
    for xp in [xx-L/2,xx+L/2]:cyl('XP2 basket cross wire',(xp,-W/2,zz+dz),(xp,W/2,zz+dz),.005,'black','Bodywork')
 if e['name']=='Engwe M20':
  M['seat'].diffuse_color=(.32,.17,.08,1);M['seat'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.32,.17,.08,1)
  for zz in [hz-.025,hz+.085]:
   cyl('M20 dual stacked headlight',(headtop[0]+.08,0,zz),(headtop[0]+.145,0,zz),.045,'black','Bodywork',24);cyl('M20 dual lens',(headtop[0]+.146,0,zz),(headtop[0]+.15,0,zz),.037,'lens','Bodywork',24)
 if e['name'].startswith('Super73'):
  text('Moped battery brand','SUPER73',(.04,-.097,.77 if e['name'] in ['Super73 R','Super73 RX'] else .67),.026,'white',-1)
 if rack or e['name'] in ['Super73 S2','Super73 RX','Super73 ZX','Super73 Z Miami','Engwe M20']:
  for x in [R,F]:
   tube('Full mudguard',[(x+(rad+.022)*cos(a),0,rad+(rad+.022)*sin(a)) for a in [i*pi/36 for i in (range(10,27) if e['name'].startswith('Super73') and x==F else range(5,35) if e['name'].startswith('Super73') else range(-3,40))]],w*.42,'black','Bodywork',8)
  if fold:
   box('Rectangular fork headlamp',(F+.02,0,rad+.38),(.05,.045,.065),'black','Bodywork');box('Rectangular headlamp lens',(F+.048,0,rad+.38),(.004,.035,.052),'lens','Bodywork');tube('Headlight bracket',[(headbot[0],0,headbot[2]),(F-.07,0,rad+.30)],.006,'graphite','Bodywork')
  else:
   cyl('Headlamp body',(headtop[0]+.055,0,hz-.055),(headtop[0]+.095,0,hz-.055),.030 if moped else .025,'black','Bodywork',24);cyl('Headlamp lens',(headtop[0]+.096,0,hz-.055),(headtop[0]+.099,0,hz-.055),.024,'lens','Bodywork',24)
  box('Rear red lamp',(R-.20,0,rad*2+.05),(.022,.05,.026),'red','Bodywork')
 if e['name']=='Engwe L20':
  for sy in [-1,1]:tube('L20 flat front cargo rail',[(hx,sy*.10,hz-.02),(F+.18,sy*.10,hz-.02)],.008,'black','Bodywork')
  for xx in [hx,F+.06,F+.18]:cyl('L20 front cargo crossbar',(xx,-.10,hz-.02),(xx,.10,hz-.02),.006,'black','Bodywork')
 if e['name']=='Fiido T1':
  z=.72;xx=F-.05
  for sign in [-1,1]:tube('Front basket perimeter',[(xx-.20,sign*.17,z),(xx+.15,sign*.17,z),(xx+.15,sign*.17,z+.20),(xx-.20,sign*.17,z+.20),(xx-.20,sign*.17,z)],.006,'black','Bodywork')
  for i in range(7):
   x=xx-.20+i*.35/6
   for sign in [-1,1]:cyl('Basket wire',(x,sign*.17,z),(x,sign*.17,z+.20),.003,'black','Bodywork')
 if e['name']=='Fiido T2':
  z=hz-.07
  for yy in [-.11,.11]:tube('T2 front cargo plate rail',[(hx-.015,yy,z),(F+.20,yy,z)],.009,'black','Bodywork')
  for xx in [hx+.02,F+.06,F+.20]:cyl('T2 front cargo crossbar',(xx,-.11,z),(xx,.11,z),.007,'black','Bodywork')
  cyl('T2 front cargo headlamp',(F+.18,0,z-.05),(F+.23,0,z-.05),.033,'black','Bodywork',24);cyl('T2 front lamp lens',(F+.231,0,z-.05),(F+.235,0,z-.05),.027,'lens','Bodywork',24)
 if motor=='mid' and (family in ['commuter','stepcurve']):
  annulus('Enclosed chainring guard',bb[0],-.125,bb[1],.115,.015,'black','Drive',.012)
  plate('Commuter upper chain guard',[(R+.02,rad+.07),(bb[0]+.08,bb[1]+.11),(bb[0]+.09,bb[1]+.06),(R+.025,rad+.035)],-.125,.014,'black','Drive')
 if e['name'] in ['Aventon Abound','Fiido T2']:
  for sign in [-1,1]:plate('Rear wheel cargo skirt',[(R-.23,.43),(R+.25,.43),(R+.36,.66),(R-.25,.66)],sign*.11,.01,'black','Bodywork')
 # Amber wheel reflectors and cable clamps visible on the reference bicycles.
 if e['name'].startswith(('Engwe','Fiido','Rad Power','Lectric')):
  for x,g in [(R,'RearWheel'),(F,'FrontWheel')]:box('Amber wheel reflector',(x+.10,-w*.34,rad+.11),(.065,.008,.018),'orange',g,rot=-.7)
 # Modest model brand mark, reconstructed typography rather than licensed decals.
 if not step and not fold and not moped:
  text('Frame brand',e['name'].split(' ')[0].upper(),(.05,-.049,bb[1]+(hz-.14-bb[1])*.39),.034,'white',-1);brand=bpy.context.scene.objects.get('Frame brand');brand.rotation_euler.y=-math.atan2(hz-.14-bb[1],hx+.045-bb[0])
 rootnote='Nonmotorized pedal bicycle; BatteryMount=bottle service group, ControllerMount=cable junction, MotorMount=crank bearing. These names are viewer service anchors, not electric component claims.' if motor=='pedal' else 'Battery/controller locations are approximate service envelopes based on the exterior reference.'
 return rootnote
def photo_minimoto(e):
 n=e['name'];kid='16Z' in n or '20Y' in n;small='16Z' in n;X=.90 if small else 1.06 if kid else 1.02 if n=='KuKirin X1' else 1.16;rf=.22 if small else .27 if kid else .255;rr=rf if kid else .23;R=-X/2;F=X/2;seat=.59 if small else .71 if kid else .76;head=.76 if small else .89 if kid else .94;col='blue' if small else 'white' if kid else 'silvergrey';w=.055 if kid else .068
 wheel(F,rf,w,True,'FrontWheel',cast=(3 if small else 5) if kid else False);wheel(R,rr,w,True,'RearWheel',cast=(3 if small else 5) if kid else False,hubmotor=False)
 pivot=(-.10,0,.29 if small else .33);top=(F-.20,0,head);bot=(F-.14,0,head-.17)
 for sy in [-1,1]:
  tube('Mini perimeter upper rail',[(R-.02,sy*.05,seat),(R+.16,sy*.06,seat-.04),(F-.21,sy*.045,head-.04)],.018,col)
  tube('Mini lower cradle',[(R+.12,sy*.06,seat-.15),(pivot[0],sy*.06,pivot[2]),(F-.16,sy*.05,head-.17)],.018,col)
  tube('Triangulated swingarm',[(R,sy*.045,rr),(R+.10,sy*.06,rr+.08),(pivot[0],sy*.065,pivot[2]+.10),(R,sy*.045,rr)],.016,col,'RearSuspension')
  cyl('Fork stanchion',(bot[0],sy*.052,bot[2]),(F-.04,sy*.052,rf+.10),.014,'blue' if kid else 'gold','Fork');cyl('Fork lower leg',(F-.06,sy*.052,rf+.16),(F,sy*.052,rf),.020,'black','Fork')
 cyl('Steering head',top,bot,.025,col)
 poly=[(-.23,.30),(.08,.30),(.23,head-.13),(-.07,seat-.05)]
 if small:poly=[(-.30,.28),(.01,.27),(.15,.54),(-.11,.56)]
 plate('Model-specific battery housing',poly,0,.10,'blue' if small else 'black','BatteryMount')
 for sy in [-1,1]:
  plate('Battery side cover',[(x,z+.009) for x,z in poly],sy*.058,.005,'blue' if small else 'black','BatteryMount')
  for x,z in poly[:3]:cyl('Battery cover bolt',(x,sy*.061,z+.016),(x,sy*.066,z+.016),.004,'steel','BatteryMount',10)
 if not kid:
  for sy in [-1,1]:
   plate('Angular side shroud',[(F-.20,head-.04),(.04,seat+.01),(-.14,seat-.03),(.04,seat-.10),(.25,head-.15)],sy*.072,.009,'silvergrey' if 'E-ZPRO' in n else 'white','Bodywork')
   plate('Orange race inset',[(-.06,seat-.015),(.15,seat-.02),(.18,seat-.06),(-.03,seat-.055)],sy*.080,.001,'yellow' if 'E-ZPRO' in n else 'orange','Bodywork')
 # Narrow sculpted bench and extended MX rear fender.
 loft('Mini moto saddle',[(R-.11,seat+.04,.035,.022),(R+.01,seat+.04,.078,.04),(R+.29,seat+.025,.075,.045),(.08,seat+.045,.04,.025)],'seat')
 if not kid:
  loft('Angular rear fender',[(R-.25,seat+.04,.007,.009),(R-.12,seat+.015,.07,.017),(R+.14,seat-.03,.075,.02)],'white' if n=='KuKirin X1' else 'graphite')
  loft('Mini MX front mudguard',[(F-.22,head-.18,.025,.015),(F,head-.17,.06,.022),(F+.25,head-.14,.022,.008)],'white' if n=='KuKirin X1' else 'graphite')
  coil((R+.19,0,rr+.14),(-.17,0,seat-.13),.024,'white')
 else:
  plate('Kids side number field',[(-.17,seat-.12),(.07,seat-.13),(.08,seat-.035),(-.13,seat-.025)],-.064,.001,'yellow' if small else 'white','Bodywork')
 cockpit(top[0]-.025,head+.065,.27 if small else .31)
 cyl('Motor housing',(-.07,-.065,pivot[2]),(-.07,.065,pivot[2]),.061,'black','MotorMount',32)
 box('Controller service envelope',(.15,0,head-.25),(.10,.08,.045),'black','ControllerMount')
 chain((R,rr),.068,(-.07,pivot[2]),.046,-.09)
 for sy in [-1,1]:
  cyl('Folding foot peg',(-.12,sy*.065,pivot[2]-.02),(-.12,sy*.14,pivot[2]-.02),.014,'steel','Drive',12)
 if kid and not small:tube('Rear trainer handle',[(R-.08,-.03,rr+.10),(R-.17,-.03,seat+.22),(R-.17,.03,seat+.22),(R-.08,.03,rr+.10)],.014,'black','Bodywork')
 return 'arctic-kids-trials' if kid else 'compact-mx'

def photo_xxx(e):
 F=.60;R=-.60;rad=.304;rr=.292;w=.074;seat=.79
 wheel(F,rad,w,True,'FrontWheel');wheel(R,rr,w,True,'RearWheel')
 for sy in [-1,1]:
  tube('XXX main diagonal backbone',[(.31,sy*.045,.86),(.25,sy*.055,.75),(-.10,sy*.055,.36)],.027,'black')
  tube('XXX open rear subframe',[(-.49,sy*.046,.72),(-.23,sy*.046,.69),(-.11,sy*.05,.36)],.016,'black')
  tube('XXX rear swingarm',[(R,sy*.05,rr),(-.12,sy*.06,.36),(-.31,sy*.055,.46),(R,sy*.05,rr)],.017,'graphite','RearSuspension')
  cyl('XXX black USD fork',(.34,sy*.068,.88),(F-.03,sy*.068,rad+.07),.021,'black','Fork');cyl('XXX fork slider',(F-.06,sy*.068,rad+.21),(F,sy*.068,rad),.016,'steel','Fork')
 plate('XXX long under-seat battery',[(-.52,.68),(-.51,.76),(.19,.82),(.23,.76),(-.10,.66)],0,.13,'black','BatteryMount')
 plate('XXX slim diagonal front casing',[(-.10,.35),(-.02,.37),(.28,.76),(.23,.80)],0,.105,'graphite','Bodywork')
 box('XXX controller',(-.15,0,.52),(.10,.10,.06),'black','ControllerMount')
 cyl('XXX mid-motor',(-.09,-.075,.35),(-.09,.075,.35),.077,'black','MotorMount',40)
 coil((-.32,0,.43),(-.18,0,.69),.025,'graphite')
 loft('XXX narrow bench',[(-.70,.80,.025,.015),(-.58,.80,.073,.03),(-.34,.79,.08,.045),(-.06,.80,.04,.025)],'seat')
 loft('XXX rear fender',[(-.82,.80,.008,.005),(-.66,.78,.05,.012),(-.36,.73,.07,.014)],'black')
 loft('XXX front mudguard',[(.30,.70,.025,.010),(.52,.72,.06,.012),(.78,.70,.015,.004)],'black')
 chain((R,rr),.075,(-.09,.35),.045,-.095)
 for sy in [-1,1]:cyl('XXX foot peg',(-.11,sy*.075,.32),(-.11,sy*.16,.32),.014,'steel','Drive',16)
 cyl('XXX head tube',(.32,0,.88),(.36,0,.74),.028,'black');cockpit(.29,1.025,.36)
 box('XXX front light',(.43,0,.86),(.042,.11,.065),'black','Bodywork');box('XXX front light lens',(.455,0,.86),(.004,.08,.042),'lens','Bodywork')
 if 'L1E' in e['name']:
  for sy in [-1,1]:
   tube('XXX road mirror stem',[(.29,sy*.25,1.06),(.25,sy*.29,1.22)],.005,'black','Cockpit');box('XXX road mirror',(.25,sy*.30,1.24),(.025,.07,.052),'graphite','Cockpit')
  tube('XXX registration bracket',[(R-.07,0,.74),(R-.24,0,.57)],.009,'black','Bodywork');box('XXX registration plate',(R-.25,0,.57),(.009,.15,.09),'white','Bodywork')
 return 'talaria-xxx-horizontal-pack'


def build(e):
 global M,buckets,groups
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for img in bpy.data.images:img.use_fake_user=False
 for d in [bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.images,bpy.data.cameras,bpy.data.lights,bpy.data.worlds]:
  for x in list(d):
   if x.users==0:d.remove(x)
 M={};buckets={};groups={}
 for n,c,mt,r in [('black',(.014,.017,.019),.1,.39),('graphite',(.055,.067,.072),.65,.35),('silvergrey',(.4,.43,.44),.72,.4),('packmetal',(.11,.14,.15),.68,.43),('rubber',(.015,.018,.02),0,.9),('tread',(.032,.037,.04),0,.85),('seat',(.025,.027,.030),0,.91),('steel',(.58,.63,.66),.9,.24),('gold',(.59,.39,.11),.8,.28),('red',(.63,.004,.012),.12,.32),('white',(.85,.87,.88),.05,.35),('lime',(.12,.87,.001),.1,.35),('pink',(.95,.09,.49),.1,.35),('teal',(.002,.15,.145),.58,.33),('tan',(.45,.31,.18),0,.9),('chain',(.44,.38,.20),.8,.37),('lens',(.60,.78,.84),.3,.17)]:material(n,c,mt,r)
 for n,c in PALETTE.items():material(n,c,.15,.45)
 root=bpy.data.objects.new(e['name'],None);bpy.context.collection.objects.link(root)
 for n in GROUPS:
  o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.parent=root;groups[n]=o
 if e['name'] in S:
  cfg=S[e['name']];note=bicycle_photo(e,cfg);family=cfg[0]
 else:
  # For e-motos, use accepted model-specific frame families with dimensions adjusted to their reference.
  if e['name'] in ['Talaria X3','Talaria XXX L1E']:
   family=photo_xxx(e);note='XXX/X3 low horizontal under-seat battery, slender diagonal casing and narrow bench.'
  elif e['name'] in ['KuKirin X1','Arctic Leopard E-16Z','Arctic Leopard E-20Y','Arctic Leopard E-ZPRO']:
   family=photo_minimoto(e);note='Reference-specific compact motorcycle frame, battery casing and wheel proportions.'
  elif e['name']=='Stark Varg':
   M['red'].diffuse_color=(.84,.85,.85,1);M['red'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.84,.85,.85,1);moto('stark-varg-mx');family='stark-varg';note='White Varg MX 1.2 reference trim.'
  elif e['name'].startswith('Arctic Leopard XE'):
   M['gold'].diffuse_color=(.025,.028,.03,1);M['gold'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.025,.028,.03,1)
   moto('arctic-leopard-xe-pro-s-super');family='arctic-xe-super';note='Compact road/supermoto exterior.'
  else:
   root2,gr2,family=emoto(e)
   root=root2;groups=gr2;note='Photo-derived lightweight electric motorcycle exterior.'
   if e['name']=='Altis Delta':
    material('redbody',(.70,.012,.018),.15,.4)
    for sign in [-1,1]:
     plate('Reference red upper fairing',[(-.20,.80),(.17,.99),(.30,.92),(.17,.73),(-.08,.70)],sign*.13,.01,'redbody','Bodywork')
     plate('Delta red rear quarter',[(-.58,.84),(-.31,.78),(-.14,.72),(-.28,.62),(-.46,.74)],sign*.13,.009,'redbody','Bodywork')
     plate('Delta lower fork guard',[(.53,.39),(.57,.40),(.49,.64),(.45,.63)],sign*.085,.012,'redbody','Fork')
    box('Delta red front number plate',(.35,0,.94),(.025,.16,.17),'redbody','Bodywork')
    loft('Delta red front fender',[(.30,.80,.025,.012),(.52,.82,.065,.018),(.80,.80,.02,.009)],'redbody','Bodywork')
 for (g,m,smooth),(vs,fs) in buckets.items():
  d=bpy.data.meshes.new(g+' '+m);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(g+' | '+m,d);bpy.context.collection.objects.link(o);o.parent=groups[g];o.data.materials.append(M[m]);o['part_group']=g
  for p in d.polygons:p.use_smooth=smooth and len(p.vertices)==4
 # Merge small fabricated parts by semantic group and material to keep browser draw calls bounded.
 for o in list(root.children_recursive):
  if o.type in ['FONT','CURVE']:
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 for g,parent in groups.items():
  mb={}
  for o in list(parent.children):
   if o.type=='MESH':mb.setdefault(o.data.materials[0].name if len(o.data.materials) else 'none',[]).append(o)
  for matname,obs in mb.items():
   if len(obs)>1:
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=g+' | '+matname
 # Bake all part geometry into metric world coordinates and reset transforms before export.
 for o in list(root.children_recursive):
  if o.type in ['FONT','CURVE']:
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 bpy.context.view_layer.update();meshes=[o for o in root.children_recursive if o.type=='MESH']
 for o in meshes:
  mw=o.matrix_world.copy();o.data.transform(mw);o.matrix_basis=Matrix.Identity(4)
 for g in groups.values():g.matrix_basis=Matrix.Identity(4)
 root.matrix_basis=Matrix.Identity(4)
 coords=[v.co for o in meshes for v in o.data.vertices];floor=min(p.z for p in coords)
 for o in meshes:
  for v in o.data.vertices:v.co.z-=floor
  o.data.update()
 bpy.context.view_layer.update();coords=[v.co for o in meshes for v in o.data.vertices];dims=[max(p[i] for p in coords)-min(p[i] for p in coords) for i in range(3)]
 root['source']=e['source'];root['reference_image']=e['image'];root['reconstruction']='Photo-based approximate exterior; not manufacturer CAD or fitment geometry';root['units']='metres';root['front_axis']='+X';root['service_groups']=note
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 key=e['model']['key'];glb=BASE+'/apps/web/public'+e['model']['url'];bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True)
 triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes);e['model'].update(triangles=triangles,meshes=len(meshes),bytes=os.path.getsize(glb),family=family)
 ref=bpy.data.images.load(BASE+'/apps/web/public'+e['image'],check_existing=True);ref.pack();ref.use_fake_user=True
 # Neutral studio is deliberately excluded from GLB selection.
 material('floor',(.65,.68,.70),0,.8);bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));bpy.context.object.name='Studio floor';bpy.context.object.data.materials.append(M['floor'])
 world=bpy.data.worlds.new('Neutral studio');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.7,.75,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
 target=Vector((0,0,dims[2]*.49))
 for n,loc,power,size in [('Key',(2,-3,4),550,4),('Rim',(-2,2,3),450,3),('Fill',(3,3,2),240,3)]:
  d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(2.1,-4.6,1.8));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(dims[0]*1.12,dims[2]*1.45)
 scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(key+'.png'))
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=BASE+'/'+e['model']['nativeSource'],compress=True);bpy.ops.render.render(write_still=True)
 proof={'name':e['name'],'key':key,'dimensions_m':[round(x,4) for x in dims],'triangles':triangles,'meshes':len(meshes),'bytes':e['model']['bytes'],'semanticNodes':GROUPS,'packedReference':ref.name,'floor_min_z':min(v.co.z for o in meshes for v in o.data.vertices),'transformsBaked':True,'note':note}
 json.dump(proof,open(OUT/(key+'-validation.json'),'w'),indent=2);json.dump(e,open(OUT/(key+'-entry.json'),'w'),indent=2)
 print('BIKE_COMPLETE',key,triangles,len(meshes),flush=True)

EM=None
def emoto(e):
 global EM
 if EM is None:
  path=pathlib.Path(BASE)/'scripts/blender/batches/lightmoto/build.py';EM={'__file__':str(path),'__name__':'expansion_geometry'};exec(compile(path.read_text().split('\nonly=None')[0],str(path),'exec'),EM)
 name=e['name'];f='sting';wb=1.25;rf=.326;rr=.326;seat=.84;bar=1.06;paint='graphite';fork='black';width=.105
 if 'XXX' in name or 'X3' in name:f='xxx';wb=1.20;rf=.304;rr=.292;seat=.79;bar=1.04;width=.095
 if 'Light Bee' in name:f='erides';wb=1.25;rf=.326;rr=.326;seat=.83;bar=1.05;paint='silver'
 if name.endswith('Bee S'):wb=1.17;rf=.292;rr=.292;seat=.76;bar=.96;paint='silver'
 if name.startswith('E Ride'):f='eride';wb=1.27;width=.112
 if name=='Altis Sigma':f='sigma';wb=1.28;rf=.339;rr=.308;seat=.85;bar=1.10;paint='black';fork='gold';width=.12
 if name=='Altis Delta':f='delta';wb=1.24;rf=.32;rr=.285;seat=.82;bar=1.08;paint='black';fork='bronze';width=.119
 if name=='KuKirin X1':f='hyper';wb=.98;rf=.245;rr=.223;seat=.68;bar=.88;paint='white';fork='gold';width=.095
 if name.startswith('Arctic Leopard E-'):
  f='hyper';wb=.90 if '16Z' in name else 1.06 if '20Y' in name else 1.12;rf=.23 if '16Z' in name else .27;rr=rf;seat=.60 if '16Z' in name else .72;bar=seat+.20;paint='black';width=.075
 c=(f,wb,rf,rr,seat,bar,paint,fork,width);row={**e,**e['model']};EM['setup'](row,c)
 if 'Light Bee' in name:
  EM['paint']=EM['mat']('Reference frame coating',(.38,.52,.03) if name=='Sur-Ron Light Bee' else (.015,.13,.65),.35,.38)
 if name in ['Talaria Sting','Talaria Sting MX3','E Ride Pro SS']:
  EM['paint']=EM['mat']('Reference dark graphite frame',(.018,.022,.025),.32,.42)
 EM['body'](row,c)
 if 'Light Bee' in name:
  for ob in list(EM['root'].children_recursive):
   if ob.type=='FONT' and ob.data.body=='ERIDE':bpy.data.objects.remove(ob,do_unlink=True)
 return EM['root'],EM['groups'],f

refs=json.load(open(OUT/'ready-references.json'));chosen=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for e in refs:
 key=e['name'].lower().replace('+','-plus');import re;key=re.sub('[^a-z0-9]+','-',key).strip('-');e['model']={'key':key,'url':'/models/expansion/bikes/'+key+'.glb','nativeSource':'assets/blender/expansion/bikes/'+key+'.blend','triangles':0,'meshes':0,'bytes':0,'family':''}
 if chosen and key not in chosen:continue
 if not chosen and (OUT/(key+'-validation.json')).exists():continue
 build(e)
