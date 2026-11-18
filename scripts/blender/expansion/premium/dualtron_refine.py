"""Dualtron-only photographic exterior refinement. Dimensions are approximate unless cited.
No shared non-Dualtron geometry or materials are changed by these helpers.
"""
import bpy,math
from pathlib import Path
from mathutils import Vector,Matrix
from math import pi,sin,cos
ROOT=Path(__file__).resolve().parents[4]

def xy_shell(p,name,poly,z0,z1,m,parent='Chassis',bevel=.003):
 n=len(poly);v=[(x,y,z) for z in [z0,z1] for x,y in poly]
 return p.mesh(name,v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m,parent,b=bevel)

def outline(c,scale=1):
 style=c['deckStyle'];L=c['dl']*scale;W=c['dw']*scale
 if style=='thunder3':q=[(-.51,-.36),(-.47,-.48),(-.37,-.5),(.36,-.5),(.46,-.46),(.51,-.33),(.53,-.21),(.53,.21),(.51,.33),(.46,.46),(.36,.5),(-.37,.5),(-.47,.48),(-.51,.36),(-.505,.20),(-.46,.17),(-.455,.09),(-.405,.08),(-.405,-.08),(-.455,-.09),(-.46,-.17),(-.505,-.20)]
 elif style=='x':q=[(-.50,-.40),(-.44,-.5),(.42,-.5),(.51,-.37),(.52,-.24),(.52,.24),(.51,.37),(.42,.5),(-.44,.5),(-.5,.40)]
 elif style=='storm':q=[(-.51,-.32),(-.46,-.48),(-.34,-.5),(.38,-.5),(.51,-.36),(.53,-.18),(.53,.18),(.51,.36),(.38,.5),(-.34,.5),(-.46,.48),(-.51,.32)]
 elif style=='mini':q=[(-.5,-.39),(-.46,-.5),(.44,-.5),(.50,-.38),(.51,.38),(.44,.5),(-.46,.5),(-.50,.39)]
 elif style=='spider':q=[(-.5,-.40),(-.47,-.5),(.47,-.5),(.51,-.40),(.51,.40),(.47,.5),(-.47,.5),(-.5,.40)]
 else:q=[(-.5,-.38),(-.46,-.5),(.43,-.5),(.51,-.38),(.51,.38),(.43,.5),(-.46,.5),(-.5,.38)]
 return [(x*L,y*W) for x,y in q]

def texture_material(p,e):
 path=ROOT/'apps/web/public/assets/vehicles/expansion/premium/dualtron-details'/(e['key']+'-grip.png')
 m=p.mat('Exact-model printed rubber deck',(.04,.04,.04),0,.83)
 im=bpy.data.images.load(str(path));im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
 return m

def top_surface(p,e,c,poly,z):
 # Continuous clipped top plane uses explicit UVs; no projecting image/alpha cards.
 m=texture_material(p,e);o=p.mesh('Model-specific molded grip and printed graphics',[(x,y,z) for x,y in poly],[tuple(range(len(poly)))],m)
 uv=o.data.uv_layers.new(name='Deck UV');L=c['dl'];W=c['dw']
 for f in o.data.polygons:
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/L+.5,v.y/W+.5)
 return o

def deck(p,e,c):
 L,W,Z=c['dl'],c['dw'],c['dz'];th=c.get('deckDepth',.080)
 xy_shell(p,'Dualtron bevel-cut aluminum battery case',outline(c),Z-th,Z+.003,p.paint,bevel=.006)
 xy_shell(p,'Replaceable recessed molded standing pad',outline(c,.973),Z+.004,Z+.012,p.grip,bevel=.002)
 top_surface(p,e,c,outline(c,.968),Z+.014)
 p.cube('Battery sealed lower tray',(-.01,0,Z-th-.003),(L*.91,W*.86,.012),p.black,'BatteryMount',.004)
 p.cube('Controller heat spreader under forward deck',(L*.31,0,Z-.035),(L*.19,W*.72,.045),p.edge,'ControllerMount',.004)
 for sy in [-1,1]:
  yy=sy*(W*.5-.004)
  p.cube('Recessed black flank service panel',(0,yy,Z-th*.50),(L*.80,.010,th*.59),p.black,b=.006)
  p.cube('Upper aluminum seam rail',(0,yy,Z-.006),(L*.80,.006,.006),p.edge,b=.002)
  if c.get('rgb'):
   p.curve('Inset flank light diffuser',[(-L*.40,yy+sy*.006,Z-th*.54),(L*.39,yy+sy*.006,Z-th*.54)],.002,p.dual_led)
  for x in [-L*.41,-L*.26,0,L*.26,L*.41]:p.bolt('Case side service screw',(x,yy+sy*.005,Z-th*.25),.0024)
  for x in [-L*.42,L*.42]:
   p.rod('Deck corner integrated running light',(x,sy*W*.47,Z-.036),(x,sy*(W*.5+.003),Z-.036),.009,p.lens,n=20)
  p.label('Side Dualtron cutout marking','DUALTRON',(0,yy+sy*.008,Z-th*.63),.018,p.white)
  if c['deckStyle'] in ['storm','x']:
   for j in range(6):p.cube('Side chassis heat sink rib',(-L*.32+j*.027,yy,Z-th*.64),(.007,.012,th*.42),p.edge,b=.001)
  # Flush perimeter screws with inset black washers, eight on Thunder3 as source.
  xs=[-L*.43,-L*.18,L*.18,L*.43] if c['deckStyle']=='thunder3' else [-L*.43,-L*.22,0,L*.22,L*.43]
  for x in xs:
   p.rod('Grip countersunk screw recess',(x,sy*W*.415,Z+.012),(x,sy*W*.415,Z+.015),.006,p.black,n=24)
   p.bolt('Deck flush stainless hex screw',(x,sy*W*.415,Z+.0155),.0032,axis='Z')
  # Covered charging connectors in forward side wall.
  for j in range(2):
   x=L*.24+j*.038;p.rod('Charging port rubber dust cap',(x,yy+sy*.008,Z-.045),(x,yy+sy*.013,Z-.045),.009,p.black,n=24)
 if c['deckStyle']=='storm':
  p.cube('Storm removable pack latch',(-L*.34,0,Z+.022),(.060,.082,.014),p.edge,b=.003)
  for sy in [-1,1]:p.curve('Removable battery lid red edge',[(-L*.43,sy*W*.44,Z+.005),(L*.43,sy*W*.44,Z+.005)],.0016,p.red)

def neck(p,e,c,sx,neck):
 L,W,Z=c['dl'],c['dw'],c['dz'];family=c['deckStyle']
 if family=='x':
  outer=[(L*.28,Z-.065),(sx+.12,neck-.11),(sx+.13,neck+.03),(sx+.07,neck+.09),(sx-.035,neck+.06),(sx-.105,Z+.03)];center=sum((Vector(v) for v in outer),Vector((0,0)))/len(outer);inner=[center+(Vector(v)-center)*.67 for v in outer];N=len(outer);verts=[(v[0],y,v[1]) for y in [-.054,.054] for cont in [outer,inner] for v in cont];faces=[]
  for i in range(N):
   j=(i+1)%N;faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
  p.mesh('X cast neck arch with genuine central relief',verts,faces,p.paint,b=.004)
  for sy in [-1,1]:
   p.profile('X stepped outer frame reinforcement',[(L*.33,Z-.045),(sx+.11,neck-.14),(sx+.09,neck-.065),(sx-.07,Z+.06)],.018,p.edge,y=sy*.067)
   for j in range(3):p.rod('X diagonally ribbed frame web',(sx-.07+j*.027,sy*.06,Z+.045+j*.04),(sx+.09,sy*.06,Z+.11+j*.045),.006,p.paint)
  return
 if c.get('frontStyle')=='commuter':
  for sy in [-1,1]:
   o=p.profile('Commuter tall molded folding tower',[(L*.30,Z-.025),(sx+.105,neck+.11),(sx+.010,neck+.12),(L*.19,Z+.035)],.027,p.paint,y=sy*.039);p.bevel(o,.004)
   if c.get('yellowCowl'):
    p.profile('Togo yellow tower side chevron',[(L*.31,Z+.035),(sx+.084,neck+.060),(sx+.067,neck+.072),(L*.29,Z+.060)],.004,p.gold,y=sy*.055)
  p.cube('Commuter lower headlight cowl',(sx+.10,0,neck-.055),(.055,.078,.090),p.black,'Steering',.008)
 elif family=='mini':
  for sy in [-1,1]:
   p.profile('Mini triangular folding tower cheek',[(L*.28,Z-.035),(sx+.085,neck+.07),(sx+.025,neck+.07),(L*.20,Z+.025)],.020,p.paint,y=sy*.040)
   p.window_arm('Mini relief-window tower side',(L*.37,Z+.045),(sx+.04,neck+.04),.017,p.edge,sy*.050)
 else:
  # Paired cast cheeks meet in a narrow bearing throat. No generic tube cage.
  pts=[(L*.27,Z-.025),(L*.43,Z-.035),(sx+.105,neck-.015),(sx+.085,neck+.07),(sx+.025,neck+.07),(L*.36,Z+.045)]
  for sy in [-1,1]:
   p.profile('Cast folding neck structural cheek',pts,.020,p.paint,y=sy*.052)
   p.profile('Cast neck machined diagonal inset',[(L*.36,Z+.005),(sx+.070,neck+.02),(sx+.044,neck+.025),(L*.31,Z+.022)],.004,p.edge,y=sy*.064)
  p.cube('Neck central bridge',(sx+.032,0,neck-.055),(.086,.115,.045),p.paint,b=.008)
 p.rod('Folding neck pivot through axle',(sx+.045,-.080,neck-.014),(sx+.045,.080,neck-.014),.017,p.edge,'Steering',32)
 for sy in [-1,1]:
  p.bolt('Machined folding neck pivot bolt',(sx+.045,sy*.082,neck-.014),.011,'Steering')
  for z in [neck-.003,neck+.036]:p.bolt('Folding cheek visible mounting screw',(sx+.010,sy*.065,z),.0045,'Steering')
 p.rod('Short central steering headset',(sx+.055,0,neck-.024),(sx+.055,0,neck+.075),.031,p.black,'Steering',40)

def suspension(p,e,c,F,B):
 r,Z=c['r'],c['dz'];wide=c.get('wide',.045);family=c['deckStyle'];mini=family=='mini';commuter=c.get('frontStyle')=='commuter'
 for front,x in [(True,F),(False,B)]:
  par='Steering' if front else 'Chassis';sign=-1 if front else 1;pivot=(x+sign*(.145 if mini else .155),r+(.12 if mini else .13));pY=max(wide+.023,.063)
  for sy in [-1,1]:
   yy=sy*pY
   q=[(x-sign*.012,r-.024),(x+sign*.035,r-.027),(pivot[0]+sign*.025,pivot[1]-.035),(pivot[0]+sign*.030,pivot[1]+.024),(pivot[0]-sign*.023,pivot[1]+.039),(x+sign*.017,r+.034)]
   p.profile(('Front' if front else 'Rear')+' curved forged trailing cartridge arm',q,.021,p.dual_arm,par,yy)
   if commuter:
    if front:a=(x-.17,yy,r+.15);b=(x-.035,yy,r+.15)
    else:a=(x+.025,yy,r+.04);b=(x+.13,yy,Z+.03)
    before=len(p.parts);p.shock('Compact commuter exposed coil',a,b,.011,p.black)
    for o in p.parts[before:]:o.parent=p.groups[par]
   elif not mini:
    p.rod('C arm elastomer cartridge housing',(pivot[0],yy-.022,pivot[1]),(pivot[0],yy+.022,pivot[1]),.034,p.black,par,40)
    p.rod('Cartridge silver end cap',(pivot[0],yy+sy*.022,pivot[1]),(pivot[0],yy+sy*.024,pivot[1]),.027,p.edge,par,32)
    p.bolt('Suspension cartridge preload nut',(pivot[0],yy+sy*.026,pivot[1]),.010,par)
   else:
    # Mini models have real paired exposed coil-over modules, unlike the elastomer family.
    a=(x+sign*.105,yy,r+.045);b=(x+sign*.145,yy,Z+.13 if front else Z+.045)
    before=len(p.parts);p.shock('Mini exposed paired coil suspension',a,b,.014,p.black)
    for o in p.parts[before:]:o.parent=p.groups[par]
    p.rod('Mini yellow suspension adjuster',Vector(b)-Vector((0,0,.009)),Vector(b)+Vector((0,0,.009)),.017,p.gold,par,24)
   p.bolt('Outer forged axle arm fastener',(x,yy+sy*.014,r),.010,par)

def kick(p,e,c):
 L,W,Z=c['dl'],c['dw'],c['dz'];sty=c.get('rearStyle','none')
 if sty=='none':return
 if sty=='thunder3':
  def plate(name,poly,material):
   n=len(poly);v=[(x,y,Z+.012+(-x/L-.43)*.30+zz) for zz in [0,.014] for x,y in poly];return p.mesh(name,v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],material,b=.004)
  for sy in [-1,1]:
   q=[(-L*.46,sy*W*.40),(-L*.57,sy*W*.46),(-L*.74,sy*W*.31),(-L*.76,sy*W*.20),(-L*.66,sy*W*.15),(-L*.57,sy*W*.16),(-L*.54,sy*W*.23),(-L*.47,sy*W*.22)];plate('Thunder3 sculpted rear footrest outer cheek',q,p.paint)
   p.curve('Thunder3 rear plate perimeter red trim',[(-L*.57,sy*W*.46,Z+.012+.14*.30),(-L*.74,sy*W*.31,Z+.012+.31*.30),(-L*.76,sy*W*.20,Z+.012+.33*.30)],.0016,p.red)
   p.rod('Thunder3 latch brushed pivot pin',(-L*.55,sy*W*.10,Z+.050),(-L*.55,sy*W*.20,Z+.050),.006,p.silver)
  plate('Thunder3 broad molded rear palm foot pad',[(-L*.64,-W*.32),(-L*.75,-W*.25),(-L*.78,-W*.15),(-L*.78,W*.15),(-L*.75,W*.25),(-L*.64,W*.32)],p.grip)
  z=Z+.012+(.70-.43)*.30+.016
  logo=p.label('Thunder3 rear white Dualtron emblem','D',(-L*.704,0,z),.052,p.white);u=Vector((0,1,0));ang=math.atan(.30/L);v=Vector((-cos(ang),0,sin(ang)));logo.rotation_euler=Matrix((u,v,u.cross(v))).transposed().to_euler()
  p.cube('Thunder3 central folding latch block',(-L*.485,0,Z+.026),(.068,W*.22,.025),p.black,b=.004)
  p.cube('Thunder3 central folding latch thumb tab',(-L*.52,0,Z+.046),(.028,W*.16,.013),p.edge,b=.003)
  for sy in [-1,1]:p.bolt('Rear latch perimeter mounting screw',(-L*.43,sy*W*.11,Z+.016),.0032,axis='Z')
 elif sty=='open':
  for sy in [-1,1]:
   # Real through-window tail carry/foot rest, broader than two cylindrical rods.
   p.window_arm('Skeletal rear spoiler footrest',(-L*.42,Z+.025),(-L*.63,Z+.14),.028,p.paint,sy*W*.26)
  p.rod('Rear footrest cross rail',(-L*.63,-W*.30,Z+.14),(-L*.63,W*.30,Z+.14),.015,p.paint)
  p.cube('Rear spoiler brake lamp',(-L*.64,0,Z+.13),(.012,W*.51,.018),p.red,b=.004)
 else:
  p.profile('Raised molded rear controller spoiler',[(-L*.40,Z+.012),(-L*.64,Z+.12),(-L*.67,Z+.09),(-L*.46,Z-.025)],W*.68,p.paint)
  for sy in [-1,1]:p.curve('Rear spoiler sculpted edge',[(-L*.43,sy*W*.32,Z+.03),(-L*.62,sy*W*.32,Z+.125)],.004,p.edge)
  p.cube('Integrated spoiler rear stop light',(-L*.64,0,Z+.115),(.013,W*.66,.024),p.red,b=.004)
  for j in range(5):p.rod('Molded rear footplate traction ridge',(-L*.47-j*.018,-W*.26,Z+.045+j*.009),(-L*.47-j*.018,W*.26,Z+.045+j*.009),.0025,p.grip,n=8)

def stem(p,e,c,sx,topx,neck,H):
 if c['deckStyle']=='x':return False
 a=Vector((sx+.055,0,neck+.04));b=Vector((topx,0,H-.05));d=b-a
 # Extruded steering tube, with discrete double collars rather than one block.
 if e['name']=='Dualtron Popular':
  mid=a+d*.27;p.rod('Popular thick lower telescopic sleeve',a,mid,.031,p.paint,'Steering',32);p.rod('Popular cylindrical upper telescopic post',mid,b,.023,p.paint,'Steering',32);p.rod('Popular upper telescopic joint',mid-Vector((0,0,.010)),mid+Vector((0,0,.010)),.034,p.black,'Steering',32)
 elif c.get('flatStem'):
  o=p.profile('Flat sided Dualtron steering extrusion',[(a.x-.017,a.z),(b.x-.017,b.z),(b.x+.017,b.z),(a.x+.017,a.z)],.050,p.paint,'Steering');p.bevel(o,.003)
 else:p.rod('Dualtron aluminum steering extrusion',a,b,c.get('stemr',.023),p.paint,'Steering',32)
 for t in [.035,.12]:
  z=a+d*t;p.rod('Double collar machined folding clamp',z-d.normalized()*.015,z+d.normalized()*.015,.034,p.edge,'Steering',32)
  for sy in [-1,1]:
   p.cube('Stem collar split clamp ear',(z.x+.021,sy*.020,z.z),(.033,.018,.024),p.black,'Steering',.003)
   p.bolt('Stem clamp twin socket screw',(z.x+.024,sy*.033,z.z),.0045,'Steering')
 p.curve('Dualtron folding latch lever',[(a.x+.032,-.042,a.z+.013),(a.x+.058,-.046,a.z+.07),(a.x+.047,-.046,a.z+.105)],.006,p.edge,'Steering')
 if c.get('rgb'):
  for sy in [-1,1]:p.curve('Inset vertical stem diffuser',[(a.x+.021,sy*.010,a.z+.12),(b.x+.022,sy*.010,b.z-.10)],.0023,p.dual_led,'Steering')
 p.label('Vertical stem DUALTRON print','DUALTRON',((a.x+b.x)/2,-.024,(a.z+b.z)/2),.018,p.white,'Steering',angle=pi/2+.13)
 p.rod('Upper stem bar mount riser',(topx,0,H-.06),(topx,0,H-.01),.021,p.edge,'Steering',32)
 return True

def cockpit(p,e,c,topx,H,bar,sx,neck,F):
 modern=c.get('console')=='ey4';riser=.020
 # Distinct central folding handlebar clamp and Y-shaped handle mount.
 if e['name']=='Dualtron Togo':
  for sy in [-1,1]:p.curve('Togo BMX raised handlebar',[(topx,0,H-.15),(topx,sy*.09,H-.115),(topx-.01,sy*.16,H+.012),(topx-.01,sy*bar*.49,H+.012)],.012,p.black,'Steering')
  p.rod('Togo handlebar cross brace',(topx,-.11,H-.055),(topx,.11,H-.055),.008,p.black,'Steering',24)
 for sy in [-1,1]:
  if e['name']!='Dualtron Togo':
   p.rod('Dualtron handle mount diagonal',(topx,sy*.023,H-.065),(topx,sy*.115,H+.012),.011,p.edge,'Steering',20)
   p.rod('Folding handlebar half',(topx,sy*.035,H+.012),(topx-.008,sy*bar*.49,H+.012),.0115,p.black,'Steering',32)
   for yy in [sy*.045,sy*.084]:
    p.rod('Handlebar folding clamp collar',(topx,yy-.011,H+.012),(topx,yy+.011,H+.012),.019,p.edge,'Steering',24)
    p.bolt('Bar hinge exposed stainless fastener',(topx,yy,H+.033),.0038,'Steering',axis='Z')
   p.curve('Folding bar metal latch',[(topx-.023,sy*.042,H+.025),(topx-.034,sy*.079,H+.030),(topx-.024,sy*.118,H+.022)],.004,p.edge,'Steering')
  # Sculpted ergonomic grip has a palm wing and tapered curved main barrel.
  p.rod('Ergonomic grip inner collar',(topx-.009,sy*bar*.318,H+.012),(topx-.009,sy*bar*.342,H+.012),.020,p.edge,'Steering',32)
  p.rod('Ergonomic rubber hand grip',(topx-.009,sy*bar*.34,H+.012),(topx-.015,sy*bar*.49,H+.012),.021,p.grip,'Steering',40,r2=.0185)
  if modern:
   poly=[(topx-.026,sy*bar*.34),(topx+.021,sy*bar*.35),(topx+.036,sy*bar*.43),(topx+.022,sy*bar*.49),(topx-.025,sy*bar*.49)]
   xy_shell(p,'Sculpted grip palm support wing',poly,H-.002,H+.013,p.grip,'Steering',.008)
  for j in range(10):
   yy=sy*bar*(.35+j*.013);p.rod('Grip raised angled texture rib',(topx-.010,yy-.0009,H+.012),(topx-.010,yy+.0009,H+.012),.0212,p.black,'Steering',16)
  p.cube('Hydraulic brake master cylinder',(topx+.025,sy*bar*.285,H+.035),(.055,.031,.024),p.black,'Steering',.005)
  for k in [-1,1]:p.bolt('Brake reservoir lid screw',(topx+.025+k*.017,sy*bar*.285,H+.049),.0025,'Steering',axis='Z')
  p.curve('Curved black brake lever',[(topx+.047,sy*bar*.27,H+.028),(topx+.075,sy*bar*.34,H+.027),(topx+.085,sy*bar*.44,H+.018),(topx+.076,sy*bar*.47,H+.023)],.0045,p.black,'Steering')
  p.curve('Hydraulic brake cable loop',[(topx+.047,sy*bar*.27,H+.030),(topx+.14,sy*.16,H-.08),(sx+.12,sy*.065,neck+.12),(F-.10,sy*.08,c['r']+.075)],.0025,p.black,'Steering')
 if modern:
  x=topx+.047
  p.cube('EY4 sculpted broad display housing',(x,0,H+.075),(.074,.153,.026),p.black,'Steering',.012)
  p.cube('EY4 inset LCD lens',(x-.002,0,H+.089),(.050,.118,.003),p.screen,'Steering',.004)
  # Fine dashboard graphics are embedded texture, not unrelated interface objects.
  im=bpy.data.images.load(str(ROOT/'apps/web/public/assets/vehicles/expansion/premium/dualtron-details/ey4-screen.png'));im.pack();m=p.mat('EY4 color instrument glass',(.02,.02,.02),.1,.21);t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;bs=m.node_tree.nodes.get('Principled BSDF');m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(t.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.35
  o=p.mesh('EY4 detailed dashboard pixels',[(x-.024,-.057,H+.091),(x+.024,-.057,H+.091),(x+.024,.057,H+.091),(x-.024,.057,H+.091)],[(0,1,2,3)],m,'Steering');uv=o.data.uv_layers.new(name='Screen UV')
  for li,co in zip(o.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
  for yy in [-.029,0,.029]:p.cube('EY4 lower tactile control key',(x-.032,yy,H+.090),(.005,.013,.003),p.edge,'Steering',.001)
  p.cube('Left handlebar light and horn switchpod',(topx-.030,-bar*.28,H+.004),(.054,.045,.037),p.black,'Steering',.006)
  for j in range(3):p.rod('Switchpod round button',(topx-.031,-bar*.31+j*.014,H+.024),(topx-.031,-bar*.31+j*.014,H+.026),.005,p.silver,'Steering',20)
 else:
  x=topx+.013;yy=bar*.28
  p.rod('EY3 round trigger LCD housing',(x,yy,H+.029),(x,yy,H+.051),.035,p.black,'Steering',40)
  p.rod('EY3 green LCD glass',(x,yy,H+.051),(x,yy,H+.053),.029,p.dual_screen,'Steering',40)
  p.curve('EY3 throttle trigger',[(x-.012,yy+.027,H+.036),(x-.028,yy+.058,H+.025),(x-.041,yy+.060,H+.017)],.005,p.black,'Steering')
  p.label('EY3 LCD digits','00',(x,yy,H+.055),.023,p.white,'Steering').rotation_euler=(0,0,pi/2)
  p.cube('Dual single eco turbo switch bank',(topx-.018,-bar*.27,H+.010),(.045,.042,.030),p.black,'Steering',.004)
  for j in range(2):p.cube('Eco turbo switch rocker',(topx-.018,-bar*.28+j*.018,H+.028),(.024,.012,.005),p.red if j else p.gold,'Steering',.002)
 if modern:
  yy=bar*.285;x=topx-.018
  p.rod('Right round thumb trigger body',(x,yy,H+.028),(x,yy,H+.048),.025,p.black,'Steering',40)
  p.rod('Thumb trigger blue inset ring',(x,yy,H+.049),(x,yy,H+.051),.021,p.dual_led,'Steering',40)
  p.rod('Thumb trigger center cap',(x,yy,H+.052),(x,yy,H+.054),.018,p.black,'Steering',40)
  p.curve('Thumb accelerator curved paddle',[(x,yy+.02,H+.03),(x-.025,yy+.048,H+.02),(x-.032,yy+.049,H+.012)],.005,p.black,'Steering')
