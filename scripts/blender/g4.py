"""Reference-guided KuKirin G4 asset. Run with Blender --background --python.
Real metres; front +X, axle Y, up Z. No measured CAD data is claimed.
"""
import bpy, bmesh, math, json, os
from mathutils import Vector, Matrix
from math import sin, cos, pi
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for dat in bpy.data.materials: bpy.data.materials.remove(dat)

def mat(name,color,metal=0,rough=.4):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 return m
paint=mat('G4 graphite grey satin powder coat',(.085,.112,.112),.38,.42)
edge=mat('Dark anodized aluminium',(.031,.04,.042),.72,.3)
black=mat('Injection moulded black polymer',(.012,.016,.017),.1,.42)
rubber=mat('Tire rubber',(.018,.022,.024),0,.79)
grip=mat('Soft textured grip rubber',(.026,.031,.032),0,.67)
silver=mat('Brushed stainless steel',(.28,.31,.32),.85,.32)
rotormat=mat('Brake rotor steel',(.18,.21,.22),.86,.37)
orange=mat('KuKirin safety orange',(.96,.30,.025),.2,.35)
lens=mat('Headlamp optical diffuser',(.70,.81,.84),.35,.22)
red=mat('Rear red lens',(.46,.009,.006),.25,.26)
screen=mat('Glossy display glass',(.008,.022,.027),.35,.13)
white=mat('Display markings',(.58,.77,.73),.1,.28)
root=bpy.data.objects.new('KuKirin_G4',None); bpy.context.collection.objects.link(root)
root['assetCreator']='Blender'; root['reference']='kukirin-g4.webp'; root['accuracy']='Reference-guided visual reconstruction; not measured CAD'
root['frontAxis']='+X'; root['units']='metres'
groups={}
for n in ['Chassis','Steering','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
 o=bpy.data.objects.new(n,None); bpy.context.collection.objects.link(o); o.parent=root; groups[n]=o
parts=[]
def finish(o,name,material,parent='Chassis',smooth=False):
 o.name=name; o.data.materials.append(material); o.parent=groups[parent]; parts.append(o)
 if smooth and o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o

def bevel(o,w=.003,segments=3):
 mod=o.modifiers.new('Manufactured edge radii','BEVEL'); mod.width=w; mod.segments=segments
 mod2=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL'); mod2.keep_sharp=True
 return o

def cube(name,loc,size,m,parent='Chassis',b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 finish(o,name,m,parent); return bevel(o,b) if b else o

def mesh(name,verts,faces,m,parent='Chassis',smooth=False,b=0):
 d=bpy.data.meshes.new(name); d.from_pydata(verts,[],faces); d.update()
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();d.update()
 o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o); finish(o,name,m,parent,smooth)
 return bevel(o,b) if b else o

def profile(name,pts,width,m,parent='Chassis',y=0,b=.004):
 n=len(pts); v=[(x,y+s*width/2,z) for s in [-1,1] for x,z in pts]; f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,m,parent,b=b)

def rod(name,a,b,r,m,parent='Chassis',vertices=32,r2=None):
 d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return finish(o,name,m,parent,True)

def curve(name,pts,r,m,parent='Chassis',resolution=12):
 d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'; d.resolution_u=resolution; d.bevel_depth=r; d.bevel_resolution=3
 s=d.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
 for b,co in zip(s.bezier_points,pts): b.co=co; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o); return finish(o,name,m,parent)

def bolt(name,x,y,z,r=.005,parent='Chassis',axis='Y'):
 d={'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[axis]; v=Vector(d)*.002
 o=rod(name,Vector((x,y,z))-v,Vector((x,y,z))+v,r,silver,parent,6)
 # small dark hex socket, distinct from the metal head
 rod(name+' recessed hex',Vector((x,y,z))+v,Vector((x,y,z))+v*1.2,r*.43,black,parent,6)
 return o

def ring(name,cx,cy,cz,ro,ri,width,m,parent='Chassis',segments=72):
 v=[]
 for y,r in [(cy-width/2,ro),(cy+width/2,ro),(cy-width/2,ri),(cy+width/2,ri)]:
  v += [(cx+r*cos(i*2*pi/segments),y,cz+r*sin(i*2*pi/segments)) for i in range(segments)]
 f=[]
 for i in range(segments):
  j=(i+1)%segments
  for a,b in [(0,1),(2,0),(1,3),(3,2)]:f.append((a*segments+i,a*segments+j,b*segments+j,b*segments+i))
 return mesh(name,v,f,m,parent,True)

def label(name,text,loc,size,m,parent='Chassis',angle=0):
 d=bpy.data.curves.new(name,'FONT');d.body=text;d.size=size;d.extrude=.00012;d.align_x='CENTER';d.align_y='CENTER'
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc
 # text baseline rotates within the XZ plane, outward face toward -Y
 u=Vector((cos(angle),0,sin(angle)));v=Vector((-sin(angle),0,cos(angle)));n=u.cross(v)
 o.rotation_euler=Matrix((u,v,n)).transposed().to_euler();finish(o,name,m,parent)
 return o

# Broad 11-inch pneumatic street tires with curved shoulders and diagonal grooves.
R=.142; rear=-.515; front=.515; zax=R
for x,g in [(front,'FrontWheel'),(rear,'RearWheel')]:
 v=[]; na=288; nb=48
 for j in range(nb+1):
  t=-pi/2+pi*j/nb; y=.049*sin(t); base=.092+.05*cos(t)
  for i in range(na):
   a=2*pi*i/na
   # alternating diagonal siping on a solid, rounded carcass
   phase=(a/(2*pi)*38 + .85*sin(t)*(-1 if sin(t)<0 else 1))%1
   groove=.006*max(0,1-abs(phase-.5)/.17)*max(0,cos(t))**1.4
   rr=base-groove
   v.append((x+rr*cos(a),y,zax+rr*sin(a)))
 f=[]
 for j in range(nb):
  for i in range(na):f.append(((j+1)*na+i,(j+1)*na+(i+1)%na,j*na+(i+1)%na,j*na+i))
 mesh(g+' pneumatic tire directional tread',v,f,rubber,g,True)
 for sy in [-1,1]:
  ring('Moulded bead',x,sy*.045,zax,.099,.094,.007,rubber,g)
  ring('Alloy rim lip',x,sy*.042,zax,.094,.085,.012,edge,g)
  ring('Machined rim edge',x,sy*.049,zax,.088,.085,.0015,silver,g)
 ring('Hollow alloy rim barrel',x,0,zax,.085,.078,.078,edge,g)
 if x==rear:
  rod('Rear hub motor',(x,-.043,zax),(x,.043,zax),.067,black,'MotorMount',64)
  for sy in [-1,1]:
   ring('Motor end cover',x,sy*.046,zax,.065,.053,.004,edge,'MotorMount')
   for k in range(12):
    a=k*2*pi/12;bolt('Motor cover fastener',x+.056*cos(a),sy*.049,zax+.056*sin(a),.0026,'MotorMount')
 else:
  for k in range(10):
   a=k*2*pi/10;aa=a+.13
   for sy in [-1,1]:rod('Swept alloy spoke',(x+.03*cos(a),sy*.037,zax+.03*sin(a)),(x+.084*cos(aa),sy*.039,zax+.084*sin(aa)),.0065,edge,g,12)
  rod('Front hub',(x,-.052,zax),(x,.052,zax),.027,edge,g)
 # Disc: separate drilled sectors create genuine openings rather than dots.
 sy=-1; dy=-.059
 ring('Rotor braking band',x,dy,zax,.076,.063,.002,rotormat,g,96)
 ring('Rotor inner mount',x,dy,zax,.033,.026,.003,rotormat,g)
 for k in range(6):
  a=k*2*pi/6; b=a+.30
  rod('Rotor spider',(x+.029*cos(a),dy,zax+.029*sin(a)),(x+.065*cos(b),dy,zax+.065*sin(b)),.0033,rotormat,g,8)
  bolt('Rotor T25 screw',x+.029*cos(a),dy-.002,zax+.029*sin(a),.0027,g)
 # Tiny vent slots on steel band as dark inset channels
 for k in range(24):
  a=k*2*pi/24
  rod('Rotor cooling slot',(x+.067*cos(a),dy-.0012,zax+.067*sin(a)),(x+.073*cos(a+.035),dy-.0012,zax+.073*sin(a+.035)),.0012,black,g,6)
 cube('Disc caliper',(x-.048,-.069,zax+.060),(.031,.026,.046),black,g,.004)
 bolt('Caliper screw',x-.047,-.084,zax+.064,.004,g)
 for sy in [-1,1]:
  rod('Axle washer',(x,sy*.061,zax),(x,sy*.076,zax),.014,edge,g)
  bolt('Axle retaining nut',x,sy*.080,zax,.010,g)
 label('Tire sidewall size','11 x 3.5',(x,-.050,zax-.109),.009,grip,g)

# Formed deck body with tapering front/rear and a rounded shoulder.
profile('Sculpted battery deck shell',[(-.405,.19),(.205,.19),(.255,.215),(.245,.264),(.208,.281),(-.38,.281),(-.425,.25)],.238,paint,b=.011)
profile('Lower pan seam',[(-.405,.186),(.207,.186),(.249,.213),(.249,.221),(-.417,.221)],.222,edge,b=.004)
cube('Rubber standing platform',(-.095,0,.287),(.588,.221,.014),grip,b=.012)
# Fine longitudinal moulded deck grooves.
for y in [-.087,-.065,-.043,-.021,0,.021,.043,.065,.087]:
 curve('Anti-slip deck groove',[(-.36,y,.295),(-.08,y,.295),(.165,y,.295)],.0008,black)
for x in [-.365,.176]:
 for y in [-.09,.09]:bolt('Deck countersunk screw',x,y,.296,.0035,axis='Z')
for sy in [-1,1]:
 for x in [-.3,-.25,-.2,-.15,-.1,-.05,0,.05,.1,.15]:
  cube('Deck lower cooling ridge',(x,sy*.119,.210),(.0015,.001,.017),edge,b=0)
label('Deck KuKirin wordmark','KuKirin',(-.10,-.1205,.243),.024,orange)
# Flag/checker graphics faithfully read as small safety-orange accents.
for sx,zz,rows in [(.172,.249,3),(-.34,.246,3),(.422,.194,3),(-.413,.226,2)]:
 for i in range(4):
  for j in range(rows):
   if (i+j)%2==0:
    q=cube('Orange checker graphic',(sx+i*.006,-.122 if abs(sx)<.36 else -.081,zz+j*.006),(.0048,.0008,.0048),orange,b=.0003);q.rotation_euler[1]=-.20
# Battery and controller retained as separate exploded-view assemblies.
cube('60V battery casing',(-.13,0,.239),(.46,.162,.064),black,'BatteryMount',.009)
for x in [-.31,.04]:cube('Battery retaining strap',(x,0,.240),(.021,.168,.068),edge,'BatteryMount',.003)
label('Battery identification','60V 20Ah',(-.12,-.082,.24),.014,white,'BatteryMount')
cube('Controller aluminium housing',(.168,0,.237),(.094,.151,.055),silver,'ControllerMount',.004)
for i in range(9):cube('Controller cooling fin',(.128+i*.009,0,.269),(.004,.145,.009),edge,'ControllerMount',.001)

# Cast lower steering neck: distinct forward-raked, broad sculpted headstock.
profile('Cast G4 steering neck',[(.211,.196),(.267,.200),(.387,.456),(.373,.500),(.322,.508),(.282,.463),(.256,.378),(.219,.282)],.119,paint,b=.010)
profile('Neck inner cast recess',[(.264,.278),(.278,.296),(.346,.455),(.325,.464),(.300,.414)],.003,edge,y=-.061,b=.003)
profile('Neck front nose',[(.342,.461),(.390,.461),(.376,.518),(.342,.533),(.320,.523)],.098,paint,b=.007)
for sy in [-1,1]:
 for x,z in [(.272,.276),(.323,.405),(.354,.467)]:bolt('Headstock casting bolt',x,sy*.065,z,.0055)
# Leading swing links and rear linkage plates with shaped fork ends.
for sy in [-1,1]:
 profile('Front suspension swing arm',[(.271,.228),(.299,.251),(.529,.165),(.542,.142),(.526,.118),(.498,.118),(.285,.199)],.019,paint,y=sy*.078,b=.008)
 profile('Rear suspension swing arm',[(-.300,.253),(-.312,.279),(-.530,.170),(-.542,.141),(-.526,.118),(-.498,.124),(-.304,.226)],.019,paint,y=sy*.078,b=.007)
 for x,z in [(.287,.225),(-.315,.251)]:
  rod('Linkage pivot sleeve',(x,-.09,z),(x,.09,z),.019,edge)
  bolt('Suspension pivot',x,sy*.093,z,.010)
 for sx,sz in [(.346,.209),(-.363,.230)]:
  for k in range(3):cube('Suspension arm orange marks',(sx+k*.008,sy*.089,sz),(.004,.001,.012-k*.0015),orange,b=.001)

def shock(name,a,b,r=.017):
 d=Vector(b)-Vector(a);u=d.normalized(); e=u.cross(Vector((0,1,0))).normalized();w=u.cross(e)
 rod(name+' damper body',a,Vector(a)+d*.62,r,black)
 rod(name+' piston',Vector(a)+d*.45,b,r*.45,silver)
 pts=[]
 for i in range(241):
  t=i/240;v=Vector(a)+d*(.12+.70*t)+r*1.28*(e*cos(t*2*pi*8)+w*sin(t*2*pi*8));pts.append(v)
 # Polyline keeps a regular mechanical spring rather than smoothed spline overshoot.
 vv=[];ff=[];n=8
 for i,p in enumerate(pts):
  for j in range(n):
   an=2*pi*j/n;vv.append(p+.0028*(e*cos(an)+w*sin(an)))
 for i in range(len(pts)-1):
  for j in range(n):ff.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 mesh(name+' helical steel coil',vv,ff,edge,smooth=True)
 for p in [a,b]:rod(name+' eye pin',(p[0],-.033,p[2]),(p[0],.033,p[2]),r*.65,silver)
shock('Front mono shock',(.331,0,.381),(.426,0,.223),.016)
shock('Rear mono shock',(-.300,0,.295),(-.447,0,.204),.017)

# Curved mudguards, actual shell thickness and turned-down rear lips.
def fender(name,x,r,start,end,width):
 v=[];n=50
 for rr in [r,r+.005]:
  for j in range(9):
   y=(j/8-.5)*width
   for i in range(n+1):
    a=start+(end-start)*i/n
    rrr=rr-.008*(abs(y)/(width/2))**3
    v.append((x+rrr*cos(a),y,zax+rrr*sin(a)))
 s=(n+1)*9;f=[]
 for layer in [0,1]:
  for j in range(8):
   for i in range(n):a=layer*s+j*(n+1)+i;f.append((a,a+1,a+n+2,a+n+1))
 for j in [0,8]:
  for i in range(n):a=j*(n+1)+i;f.append((a,a+1,a+1+s,a+s))
 for i in [0,n]:
  for j in range(8):a=j*(n+1)+i;f.append((a,a+n+1,a+n+1+s,a+s))
 mesh(name,v,f,black,smooth=True)
fender('Front short curved mudguard',front,.164,.46*pi,1.05*pi,.115)
fender('Rear wraparound mudguard',rear,.165,-.12*pi,.86*pi,.116)
for sy in [-1,1]:
 curve('Rear fender embossed ridge',[(-.664,sy*.043,.220),(-.615,sy*.043,.279),(-.535,sy*.043,.309)],.0025,edge)
 rod('Rear mudguard stay',(-.515,sy*.052,.143),(-.612,sy*.050,.278),.005,edge)
# Elevated rear foot support, recognisable G4 kick plate.
profile('Rear kick support bracket',[(-.354,.281),(-.382,.282),(-.465,.365),(-.426,.369)],.111,edge,b=.005)
kick=profile('Raised rear footrest',[(-.356,.359),(-.362,.378),(-.530,.407),(-.550,.395),(-.546,.376)],.177,paint,b=.008)
profile('Kick pad textured top',[(-.369,.383),(-.530,.411),(-.540,.401),(-.381,.373)],.158,grip,b=.003)
for x in [-.399,-.445,-.490]:
 for y in [-.068,.068]:bolt('Kick plate bolt',x,y,.389+(-x-.40)*.17,.0032,axis='Z')
cube('Tail lamp housing',(-.660,0,.246),(.027,.086,.035),black,b=.005)
cube('Tail red optical lens',(-.676,0,.248),(.006,.073,.022),red,b=.003)
# Fold hinge with overlapping machined plates, transverse pin, lock lever.
profile('Folding stem heel',[(.305,.507),(.373,.513),(.363,.607),(.294,.603)],.075,black,'Steering',b=.005)
for sy in [-1,1]:
 profile('Folding hinge cheek',[(.299,.513),(.369,.522),(.349,.621),(.286,.612)],.008,edge,'Steering',y=sy*.044,b=.003)
 for x,z in [(.319,.537),(.347,.548),(.307,.577),(.335,.589)]:bolt('Folding plate socket screw',x,sy*.05,z,.0045,'Steering')
rod('Folding hinge axle',(.336,-.058,.530),(.336,.058,.530),.014,silver,'Steering')
curve('Folding quick release lever',[(.297,-.057,.568),(.275,-.059,.615),(.277,-.059,.649)],.007,black,'Steering')
rod('Quick release handle',(.277,-.074,.648),(.277,-.044,.648),.008,edge,'Steering')
# Slight rearward rake and wide flat sided stem, distinct from round tube scooters.
profile('Broad tapered G4 steering stem',[(.291,.597),(.350,.608),(.207,1.174),(.156,1.170)],.057,edge,'Steering',b=.006)
profile('Stem side brushed inset',[(.298,.650),(.329,.657),(.212,1.134),(.182,1.128)],.002,paint,'Steering',y=-.030,b=.0015)
# Stem sections and clamps follow the same rake.
for z in [.678,.825,1.102]:
 x=.326-(z-.605)*.247
 profile('Stem panel seam',[(x-.026,z-.002),(x+.027,z+.011),(x+.026,z+.015),(x-.027,z+.002)],.060,black,'Steering',b=.001)
angle=math.atan2(.46,-.114)
label('Stem KuKirin G4 branding','KuKirin G4',(.251,-.0315,.884),.023,orange,'Steering',angle)
label('Stem lower marking','KuKirin',(.310,-.0315,.705),.010,orange,'Steering',angle)
for i in range(4):
 for j in range(3):
  if (i+j)%2==0:cube('Stem orange checker',(.307+i*.004,-.032,.635+j*.004),(.003,.0007,.003),orange,'Steering',.0003)
# Routed brake loom, strain relief, and rubber cable clips.
for yy in [-.035,.034]:
 curve('Stem routed brake cable',[(.177,yy*2.7,1.210),(.226,yy*1.8,1.115),(.241,yy,.994),(.307,yy,.718),(.341,yy,.535),(.390,yy,.347),(.467,-.077,.208)],.0023,black,'Steering')
for z in [.735,.98,1.12]:
 x=.326-(z-.605)*.247
 cube('Cable retaining clip',(x-.025,-.035,z),(.016,.009,.012),black,'Steering',.002)
# Handlebar yoke, swept handlebars, controls and finely ribbed rubber grips.
rod('Steering yoke',(.182,0,1.14),(.173,0,1.235),.020,edge,'Steering')
curve('Swept handlebar',[(.136,-.337,1.247),(.154,-.2,1.249),(.168,-.10,1.229),(.170,0,1.226),(.168,.10,1.229),(.154,.2,1.249),(.136,.337,1.247)],.0115,edge,'Steering')
for sy in [-1,1]:
 rod('Bar clamp',(.169,sy*.023,1.226),(.169,sy*.043,1.226),.019,black,'Steering')
 for x in [.156,.182]:bolt('Clamp fastener',x,sy*.032,1.243,.003,'Steering',axis='Z')
 rod('Rubber handle grip',(.137,sy*.224,1.247),(.137,sy*.341,1.247),.018,grip,'Steering',40)
 for k in range(24):ring('Fine moulded grip rib',.137,sy*(.228+k*.0046),1.247,.0188,.017,.0012,grip,'Steering',32)
 rod('Grip outer cap',(.137,sy*.342,1.247),(.137,sy*.346,1.247),.019,black,'Steering')
 cube('Brake lever clamp',(.148,sy*.214,1.245),(.032,.020,.034),black,'Steering',.003)
 curve('Cast brake lever',[(.166,sy*.208,1.249),(.192,sy*.237,1.244),(.198,sy*.297,1.237),(.191,sy*.32,1.239)],.004,edge,'Steering')
 bolt('Brake lever pivot',.167,sy*.216,1.264,.003,'Steering',axis='Z')
 curve('Brake hose at controls',[(.175,sy*.204,1.246),(.217,sy*.165,1.215),(.214,sy*.080,1.110)],.0022,black,'Steering')
cube('Thumb throttle housing',(.148,.187,1.246),(.034,.032,.037),black,'Steering',.004)
cube('Throttle thumb paddle',(.116,.188,1.225),(.036,.023,.009),black,'Steering',.004)
cube('Left control switch',(.147,-.182,1.247),(.036,.036,.040),black,'Steering',.004)
cube('Control orange button',(.154,-.183,1.270),(.016,.017,.005),orange,'Steering',.002)
# Angular combined display/headlamp pod, G4's characteristic polygonal silhouette.
profile('Angular console headlamp housing',[(.132,1.209),(.207,1.210),(.246,1.244),(.231,1.271),(.185,1.300),(.146,1.285),(.121,1.245)],.115,black,'Steering',b=.007)
profile('Console side facet',[(.142,1.216),(.205,1.216),(.232,1.242),(.186,1.253),(.129,1.244)],.002,paint,'Steering',y=-.059,b=.001)
# Broad white strip facing front, split into four lens segments.
for y in [-.045,-.015,.015,.045]:
 o=cube('Forward LED lens',(.239,y,1.245),(.006,.027,.020),lens,'Steering',.002);o.rotation_euler[1]=-.20
cube('Console display screen',(.166,0,1.288),(.064,.084,.005),screen,'Steering',.004)
for x in [.148,.157,.166,.175,.184]:cube('Display luminous segments',(x,-.014,1.291),(.004,.021,.0008),white,'Steering',.0005)
# Small folding carry strap hangs next to stem.
curve('Carry strap loop',[(.174,.057,1.184),(.185,.061,1.058),(.212,.063,1.029),(.235,.061,1.070),(.198,.058,1.176)],.006,black,'Steering')
# Side stand folded along underside; charging port on the left flank.
rod('Folded kickstand',(-.230,-.136,.199),(-.389,-.138,.183),.006,edge)
cube('Kickstand foot',(-.39,-.14,.183),(.026,.022,.007),black,b=.003)
rod('Charging port rubber cap',(.116,-.120,.243),(.116,-.126,.243),.010,black)

# Convert everything to meshes, apply edge modifiers, then consolidate by assembly/material.
for o in list(parts):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 if o.type!='MESH':bpy.ops.object.convert(target='MESH')
 for mod in list(o.modifiers):
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except RuntimeError:pass
# Group by material within each named assembly: compact draw calls, preserved service groups.
for parent in groups.values():
 buckets={}
 for o in list(parent.children):
  if o.type=='MESH':buckets.setdefault(o.data.materials[0].name,[]).append(o)
 for mn,objs in buckets.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0]
  if len(objs)>1:bpy.ops.object.join()
  objs[0].name=parent.name+' | '+mn
# Store mount origins sensibly without moving geometry.
for gn,co in [('FrontWheel',(front,0,zax)),('RearWheel',(rear,0,zax)),('BatteryMount',(-.13,0,.239)),('ControllerMount',(.168,0,.237)),('MotorMount',(rear,0,zax))]:
 bpy.context.view_layer.update()
 p=groups[gn]; mats=[(c,c.matrix_world.copy()) for c in p.children];p.location=co
 bpy.context.view_layer.update()
 for c,m in mats:c.matrix_world=m
 bpy.context.view_layer.update()
root['dimensionsApprox']='1.32m long, 0.69m handlebar width, 1.30m high'
# Packed exact reference remains in the authoring file for inspection, excluded from export.
ref=bpy.data.images.load(os.path.join(ROOT,'apps/web/public/assets/vehicles/kukirin-g4.webp'));ref.pack()
refob=bpy.data.objects.new('REFERENCE - user supplied G4',None);bpy.context.collection.objects.link(refob);refob.empty_display_type='IMAGE';refob.data=ref;refob.empty_display_size=1.5;refob.location=(0,1.5,.70);refob.rotation_euler=(pi/2,0,0);refob.hide_render=True;refob.hide_viewport=True
# Selected model export excludes the reference, ground, camera and studio lights.
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for p in groups.values():
 p.select_set(True)
 for c in p.children:c.select_set(True)
export=os.path.join(ROOT,'apps/web/public/models/kukirin-g4.glb')
bpy.ops.export_scene.gltf(filepath=export,export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
tri=sum(len(o.data.loop_triangles) for p in groups.values() for o in p.children if o.type=='MESH')
# loop triangles need explicit calculation on authored mesh data.
tri=0
for p in groups.values():
 for o in p.children:
  if o.type=='MESH':o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Neutral studio for actual visual QA.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world.color=(.5,.5,.5);scene.view_settings.view_transform='AgX'
groundmat=mat('Studio warm grey',(.73,.75,.75),0,.85)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));ground=bpy.context.object;ground.name='STUDIO floor excluded from export';ground.data.materials.append(groundmat)
def area(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large softbox',(.5,-2.5,3.5),420,3);area('Fill softbox',(-2,1,2),320,2.5);area('Edge softbox',(2,2,2.7),450,2)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.66;cam.data.lens=50
for name,loc,target in [('g4-three-quarter.png',(2.5,-4.2,2.0),(0,0,.64)),('g4-side.png',(0,-5,.82),(0,0,.65))]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=os.path.join(ROOT,'artifacts/blender',name);bpy.ops.render.render(write_still=True)
# Authoring scene opens on the hero camera, with only exported vehicle selected.
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'assets/blender/kukirin-g4.blend'))
report={'asset':'kukirin-g4','creator':'Blender','triangles':tri,'meshObjects':sum(len(p.children) for p in groups.values()),'glbBytes':os.path.getsize(export),'reference':'apps/web/public/assets/vehicles/kukirin-g4.webp','limitations':'Visual reconstruction from one supplied three-quarter photograph. Hidden surfaces and internal service assemblies are inferred. Not measured CAD.'}
with open(os.path.join(ROOT,'artifacts/blender/g4-asset-note.json'),'w') as f:json.dump(report,f,indent=2)
print('G4_ASSET_REPORT '+json.dumps(report))
