"""Reference-guided KuKirin G4 for Blender --background --python.

Model axes are +X forward, +Y rider left, and +Z up. Dimensions are in metres.
The owner reference, KuKirin gallery side view, factory specifications, EN17128
report, and original kickstand spare-part photographs guide this exterior.
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
paint=mat('G4 graphite grey satin powder coat',(.072,.086,.093),.40,.46)
edge=mat('Dark anodized aluminium',(.031,.04,.042),.72,.3)
black=mat('Injection moulded black polymer',(.005,.007,.008),.08,.46)
rubber=mat('Tire rubber',(.006,.007,.008),0,.86)
grip=mat('Soft textured grip rubber',(.008,.010,.011),0,.73)
silver=mat('Brushed stainless steel',(.28,.31,.32),.85,.32)
rotormat=mat('Brake rotor steel',(.18,.21,.22),.86,.37)
orange=mat('KuKirin safety orange',(.96,.30,.025),.2,.35)
lens=mat('Headlamp optical diffuser',(.70,.81,.84),.35,.22)
red=mat('Rear red lens',(.46,.009,.006),.25,.26)
screen=mat('Glossy display glass',(.008,.022,.027),.35,.13)
white=mat('Display markings',(.58,.77,.73),.1,.28)
signal=mat('Amber side reflector',(.45,.102,.018),.18,.24)
footpad=mat('Dry-textured G4 standing pad',(.021,.024,.025),0,.78)
root=bpy.data.objects.new('KuKirin_G4',None); bpy.context.collection.objects.link(root)
root['assetCreator']='Blender'; root['reference']='kukirin-g4.webp'; root['accuracy']='Reference-guided visual reconstruction; not measured CAD'
root['frontAxis']='+X'; root['units']='metres'
root['stockHandlebarMm']=660
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

def label(name,text,loc,size,m,parent='Chassis',angle=0,side=-1):
 d=bpy.data.curves.new(name,'FONT');d.body=text;d.size=size;d.extrude=.00012;d.align_x='CENTER';d.align_y='CENTER'
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc
 # text baseline rotates within the XZ plane, outward face toward -Y
 u=Vector((cos(angle),0,sin(angle)));v=Vector((-sin(angle),0,cos(angle)))
 if side > 0:u=-u
 n=u.cross(v)
 o.rotation_euler=Matrix((u,v,n)).transposed().to_euler();finish(o,name,m,parent)
 return o

# Broad 11-inch pneumatic street tires with curved shoulders and diagonal grooves.
R=.142; rear=-.518; front=.518; zax=R
for x,g in [(front,'FrontWheel'),(rear,'RearWheel')]:
 v=[]; na=288; nb=48
 for j in range(nb+1):
  t=-pi/2+pi*j/nb; y=.049*sin(t); base=.092+.05*cos(t)
  for i in range(na):
   a=2*pi*i/na
   # alternating diagonal siping on a solid, rounded carcass
   phase=(a/(2*pi)*38 + .85*sin(t)*(-1 if sin(t)<0 else 1))%1
   groove=.0034*max(0,1-abs(phase-.5)/.17)*max(0,cos(t))**1.4
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

# The G4 has a straight-edged battery enclosure and a separate 510 × 210 mm mat.
profile(
    'G4 rectangular extruded battery enclosure',
    [(-.292,.183),(.231,.183),(.250,.200),(.250,.263),(.232,.276),(-.277,.276),(-.298,.253)],
    .228,paint,b=.006,
)
profile(
    'Recessed lower undertray',
    [(-.283,.179),(.224,.179),(.246,.194),(.246,.203),(-.293,.203)],
    .208,edge,b=.003,
)
cube('Separate upper deck cover',(-.021,0,.278),(.521,.219,.010),edge,b=.006)
cube('510 by 210 mm standing pad',(-.021,0,.285),(.510,.210,.008),footpad,b=.006)

# Shallow chevron tread is oriented down the platform toward the rear wheel.
for index in range(41):
    x = .181-index*.0112
    curve(
        'Moulded chevron deck channel',
        [(x+.028,-.092,.2892),(x,0,.2892),(x+.028,.092,.2892)],
        .0009,black,resolution=3,
    )
for x in [-.255,.207]:
    for y in [-.088,.088]:
        bolt('Deck cover countersunk screw',x,y,.290,.0031,axis='Z')

for side in [-1,1]:
    y = side*.1148
    for x in [-.268,.214]:
        bolt('Undertray flange screw',x,y,.197,.003,axis='Y')
    # Reference model carries checker flags and small chassis graphics near its rocker mounts.
    for x_start in [.166,-.257]:
        for i in range(5):
            for j in range(3):
                if (i+j)%2 == 0:
                    cube('Deck checker graphic',(x_start+i*.005,y,.218+j*.005),
                         (.0043,.0006,.0043),orange,b=.00025)
    cube('Recessed serial plate',(-.242,y,.254),(.072,.0016,.022),black,b=.0015)
    for j in range(3):
        cube('Serial plate print line',(-.242,y+side*.001,.247+j*.005),
             (.053-j*.006,.0006,.0015),white,b=0)
label('Deck chassis designation','K-G4',(-.031,.1155,.226),.012,orange,side=1)
label('Deck KuKirin wordmark','KuKirin',(-.013,-.1155,.226),.016,orange)
# Battery and controller retained as separate exploded-view assemblies.
cube('60V battery casing',(-.092,0,.239),(.370,.162,.064),black,'BatteryMount',.009)
for x in [-.244,.053]:cube('Battery retaining strap',(x,0,.240),(.021,.168,.068),edge,'BatteryMount',.003)
label('Battery identification','60V 20Ah',(-.092,-.082,.24),.014,white,'BatteryMount')
cube('Controller aluminium housing',(.168,0,.237),(.094,.151,.055),silver,'ControllerMount',.004)
for i in range(9):cube('Controller cooling fin',(.128+i*.009,0,.269),(.004,.145,.009),edge,'ControllerMount',.001)

# The lightly rounded outer webs flank an open underside above the front shock.
neck_web = [
    (.212,.185),(.264,.198),(.284,.265),(.419,.452),(.454,.463),
    (.474,.490),(.464,.522),(.421,.531),(.398,.500),(.370,.431),
    (.247,.285),(.220,.261),
]
for side in [-1,1]:
    profile('Forward headstock cheek and continuous deck rail',neck_web,.014,paint,
            y=side*.050,b=.006)
    profile('Inner headstock shock carrier',
            [(.261,.231),(.305,.237),(.343,.318),(.432,.448),(.409,.463),(.373,.420),(.292,.311)],
            .016,edge,y=side*.035,b=.004)
    for x,z in [(.254,.228),(.307,.336),(.429,.470)]:
        bolt('Headstock casting socket',x,side*.059,z,.0045)
profile('Transverse neck-to-battery joint',
        [(.211,.185),(.262,.197),(.289,.260),(.264,.289),(.234,.276)],.103,paint,b=.006)
profile('Crown across front shock opening',
        [(.404,.460),(.474,.469),(.464,.521),(.421,.531),(.397,.500)],.088,paint,b=.006)
dust_shield = cube('Machined front neck shield',(.469,0,.491),(.009,.071,.055),silver,b=.004)
dust_shield.rotation_euler[1] = -.16
# Machined rocker arms with stepped ends and exposed axle bosses.
for sy in [-1,1]:
    profile(
        'Leading front suspension rocker',
        [(.297,.240),(.317,.257),(.354,.236),(.539,.162),(.544,.145),(.528,.121),
         (.505,.117),(.488,.129),(.302,.207),(.291,.222)],
        .019,paint,y=sy*.078,b=.006,
    )
    profile(
        'Rear suspension rocker and motor axle seat',
        [(-.296,.264),(-.322,.272),(-.357,.244),(-.531,.168),(-.548,.150),
         (-.540,.124),(-.516,.117),(-.490,.128),(-.308,.214),(-.287,.239)],
        .020,paint,y=sy*.078,b=.006,
    )
    for x,z in [(.313,.231),(-.310,.241)]:
        rod('Machined pivot boss',(x,sy*.081,z),(x,sy*.092,z),.017,edge)
        bolt('Rocker pivot shoulder bolt',x,sy*.094,z,.008)
    for x,z in [(front,zax),(rear,zax)]:
        rod('Open axle counterbore rim',(x,sy*.087,z),(x,sy*.091,z),.013,edge)
        bolt('External axle hardware',x,sy*.095,z,.008)
    for x,z in [(.364,.205),(-.365,.222),(-.470,.161)]:
        for index in range(3):
            mark = cube('Orange rocker-arm marks',
                        (x+index*.006,sy*.0888,z-index*.003),
                        (.004,.001,.011-index*.0015),orange,b=.0006)
            mark.rotation_euler[1] = -.30 if x > 0 else .30
    cube('Front amber side reflector',(.391,sy*.0907,.199),(.021,.004,.008),signal,b=.001)

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
shock('Front mono shock',(.423,0,.424),(.369,0,.249),.014)
shock('Rear mono shock',(-.304,0,.361),(-.398,0,.237),.017)

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
fender('Compact inner front splash guard',front,.158,.67*pi,.96*pi,.102)
profile('Short flat front splash deflector',
        [(.350,.344),(.426,.351),(.482,.358),(.478,.352),(.391,.335)],.100,black,b=.002)
fender('Split-facet wraparound rear fender',rear,.167,.47*pi,1.06*pi,.119)
for sy in [-1,1]:
    curve('Rear fender embossed ridge',
          [(-.681,sy*.044,.187),(-.652,sy*.044,.241),(-.602,sy*.044,.288),(-.536,sy*.044,.315)],
          .0019,edge)
    profile('Reinforced rear mudguard stay',
            [(-.553,.145),(-.571,.150),(-.635,.255),(-.617,.276),(-.601,.270)],
            .009,edge,y=sy*.052,b=.002)
    bolt('Rear fender hardware',-.620,sy*.062,.265,.004)

# The raised platform leaves a visible opening between its side brackets.
for sy in [-1,1]:
    profile('Rear footrest cheek',
            [(-.269,.266),(-.310,.265),(-.388,.344),(-.356,.353),(-.320,.316)],
            .012,paint,y=sy*.078,b=.004)
    bolt('Footrest mount socket',-.302,sy*.085,.278,.0032)
    bolt('Upper footrest bracket socket',-.350,sy*.085,.331,.003)
profile('Raised rear footrest plate',
        [(-.269,.327),(-.283,.347),(-.429,.393),(-.454,.388),(-.444,.371),(-.291,.326)],
        .183,paint,b=.006)
profile('Moulded rear footrest mat',
        [(-.280,.347),(-.423,.393),(-.445,.394),(-.451,.388),(-.290,.339)],
        .167,footpad,b=.004)
for index in range(12):
    x = -.298-index*.011
    z = .348+(-x-.298)*.32
    curve('Moulded rear footrest chevrons',[(x+.009,-.071,z-.003),(x,0,z),(x+.009,.071,z-.003)],
          .0011,black,resolution=4)
# Integral tail lamp sits just below the rear footrest, with separate fender reflector.
profile('Rear footrest tail lamp housing',
        [(-.431,.367),(-.451,.375),(-.447,.386),(-.431,.381)],.132,black,b=.003)
cube('Under-footrest red tail light',(-.449,0,.372),(.010,.115,.014),red,b=.0025)
cube('Fender inset red reflector',(-.681,0,.180),(.008,.040,.023),red,b=.003)

# Fold hinge with overlapping machined plates, transverse pin, lock lever.
profile('Folding stem heel',[(.409,.509),(.470,.519),(.442,.602),(.389,.586)],.069,black,'Steering',b=.005)
for sy in [-1,1]:
    profile('Overlapping folding hinge cheek',
            [(.410,.518),(.463,.528),(.432,.617),(.382,.603)],.008,edge,'Steering',
            y=sy*.038,b=.003)
    for x,z in [(.426,.540),(.451,.551),(.414,.576),(.434,.589)]:
        bolt('Folding plate socket screw',x,sy*.044,z,.0041,'Steering')
rod('Folding hinge axle',(.438,-.050,.534),(.438,.050,.534),.012,silver,'Steering')
curve('Forged folding quick release lever',
      [(.403,-.047,.566),(.389,-.051,.602),(.383,-.053,.647)],.006,black,'Steering')
rod('Quick release grip',(.383,-.068,.647),(.383,-.041,.647),.007,edge,'Steering')

# Broad flat sided aluminium stem and a contrasting machined panel.
profile('Rearward-raked G4 steering stem',
        [(.386,.592),(.436,.605),(.257,1.196),(.207,1.182)],.057,edge,'Steering',b=.005)
profile('Stem brushed side panel',
        [(.398,.644),(.426,.652),(.263,1.166),(.231,1.153)],.002,paint,'Steering',y=.029,b=.001)

def stem_center(z):
    return .415-(z-.602)*.298

for z in [.674,.837,1.109]:
    x = stem_center(z)
    profile('Machined stem seam',[(x-.024,z-.002),(x+.027,z+.010),
            (x+.026,z+.014),(x-.025,z+.002)],.058,black,'Steering',b=.0008)
angle = math.atan2(.50,-.149)
label('Stem KuKirin G4 branding','KuKirin G4',(stem_center(.940),.0305,.940),
      .022,orange,'Steering',angle,side=1)
label('Stem right-hand KuKirin G4 mark','KuKirin G4',(stem_center(.940),-.0305,.940),
      .022,orange,'Steering',angle)
for y in [-.031,.031]:
    for i in range(5):
        for j in range(3):
            if (i+j)%2 == 0:
                cube('Stem orange checker',(stem_center(.645)+i*.004-.010,y,.638+j*.004),
                     (.003,.0007,.003),orange,'Steering',.0003)
# OEM 660 mm swept cockpit. Part metadata preserves the original hardware as
# independent meshes when the workbench previews a new bar or pair of grips.
bar_center = (.230,0,1.230)
grip_x, grip_z = .199,1.247
grip_start, grip_end = .212,.325

def cockpit_anchor(name, xyz):
    anchor = bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(anchor)
    anchor.parent = groups['Steering']
    anchor.location = xyz

def tag_cockpit_parts(start, tag):
    for part in parts[start:]:
        part['vfCockpit'] = tag

# The upper brake runs detach for replacement bars. The lower loom stays on the stem.
for side,slot in [(-1,'A'),(1,'B')]:
    y = side*.035
    junction = (stem_center(.992)+.030,y,.992)
    cockpit_anchor('VF_Cockpit_Cable'+slot,junction)
    curve('Repositionable upper brake hose',
          [(.234,side*.173,1.251),(.251,side*.153,1.227),(.247,side*.090,1.198),
           (.254,side*.055,1.106),junction],.0021,black,'Steering')['vfCockpit'] = 'cable'
    curve('Stem routed lower brake cable',[junction,(stem_center(.717)+.023,y,.717),
          (.471,y,.541),(.436,y,.377),(.455,y*2.2,.229)],.0021,black,'Steering')
    for z in [.735,.992]:
        cube('Cable retaining clip',(stem_center(z)+.027,y,z),(.016,.009,.012),black,'Steering',.002)

def stock_grip(side):
    # A single molded sleeve preserves the fine diamond pattern at close range.
    vertices, faces = [],[]
    axial_steps, around = 96,64
    for row in range(axial_steps+1):
        t = row/axial_steps
        y = side*(grip_start+(grip_end-grip_start)*t)
        for column in range(around):
            angle = 2*pi*column/around
            diamond = .00065*max(0, cos(angle*16+2*pi*t*22)*cos(angle*16-2*pi*t*22))
            profile_radius = .0164 + .0006*sin(pi*t)
            if .06<t<.94:
                profile_radius += diamond
            vertices.append((grip_x+profile_radius*cos(angle),y,grip_z+profile_radius*sin(angle)))
    for row in range(axial_steps):
        for column in range(around):
            here = row*around+column
            following = row*around+(column+1)%around
            faces.append((here,following,following+around,here+around))
    faces.extend([tuple(range(around-1,-1,-1)),
                  tuple(range(axial_steps*around,(axial_steps+1)*around))])
    mesh('Moulded diamond-pattern rubber grip',vertices,faces,grip,'Steering',smooth=True)

cockpit_anchor('VF_Cockpit_Center',bar_center)
rod('Steering yoke',(.233,0,1.165),bar_center,.020,edge,'Steering')
bar = curve('Tapered swept handlebar',
            [(grip_x,-.330,grip_z),(grip_x,-.215,grip_z),(.222,-.115,1.235),bar_center,
             (.222,.115,1.235),(grip_x,.215,grip_z),(grip_x,.330,grip_z)],
            .011,edge,'Steering',16)
for point,radius in zip(bar.data.splines[0].bezier_points,[1,1,1.08,1.36,1.08,1,1]):
    point.radius = radius
bar['vfCockpit'] = 'bar'

for side,slot in [(-1,'A'),(1,'B')]:
    cockpit_anchor('VF_Cockpit_Grip'+slot,(grip_x,side*(grip_start+grip_end)/2,grip_z))
    rod('Split steel bar clamp',(.231,side*.017,1.230),(.231,side*.042,1.230),.020,black,'Steering')
    for x in [.214,.246]:
        bolt('Clamp fastener',x,side*.031,1.248,.003,'Steering',axis='Z')

    first = len(parts)
    stock_grip(side)
    ring('Moulded inner grip collar',grip_x,side*.213,grip_z,.0188,.0125,.006,grip,'Steering',48)
    rod('Rounded end plug',(grip_x,side*.325,grip_z),(grip_x,side*.330,grip_z),
        .0173,black,'Steering',40,r2=.016)
    ring('Fine outer plug detail',grip_x,side*.328,grip_z,.0168,.0141,.0017,grip,'Steering',48)
    tag_cockpit_parts(first,'grip'+slot)

    first = len(parts)
    ring('Two-piece brake lever bar clamp',.202,side*.202,1.246,.0163,.0115,.013,black,'Steering',40)
    body = cube('Cast brake master housing',(.217,side*.199,1.247),(.033,.029,.027),black,'Steering',.004)
    body.rotation_euler[2] = side*.14
    lever = curve('Forged tapered two-finger brake lever',
                  [(.233,side*.199,1.247),(.252,side*.218,1.245),(.269,side*.270,1.237),
                   (.264,side*.311,1.234)],
                  .0038,edge,'Steering',14)
    for point,radius in zip(lever.data.splines[0].bezier_points,[1.3,1.08,.84,1.03]):
        point.radius=radius
    bolt('Brake lever pivot',.232,side*.205,1.261,.0031,'Steering',axis='Z')
    rod('Knurled brake cable locknut',(.232,side*.179,1.251),(.236,side*.170,1.251),
        .0045,silver,'Steering',12)
    if slot == 'A':
        cube('Thumb throttle housing',(.207,-.176,1.243),(.034,.030,.029),black,'Steering',.004)
        cube('Thumb throttle paddle',(.181,-.181,1.226),(.035,.022,.008),black,'Steering',.003)
        for index in range(3):
            cube('Throttle paddle texture',(.171+index*.006,-.181,1.230),
                 (.0011,.017,.0009),grip,'Steering',.0003)
    else:
        cube('Rider-left lighting switch pod',(.211,.176,1.243),(.034,.032,.034),black,'Steering',.004)
        cube('Orange switch button',(.213,.176,1.261),(.012,.013,.004),orange,'Steering',.001)
        rod('Bell dome',(.210,.188,1.256),(.210,.188,1.271),.012,edge,'Steering',40,r2=.007)
    tag_cockpit_parts(first,'control'+slot)

# The tapered integrated LED console narrows to a dark cap above its light strip.
console_outline = [
    (.190,1.217),(.266,1.211),(.298,1.231),(.309,1.249),(.293,1.267),
    (.259,1.285),(.225,1.295),(.205,1.290),(.181,1.258),
]
console_vertices = []
for y,scale in [(-.0775,.59),(-.057,.92),(-.031,1),(.031,1),(.057,.92),(.0775,.59)]:
    for x,z in console_outline:
        console_vertices.append((.243+(x-.243)*scale,y,1.244+(z-1.244)*scale))
n = len(console_outline)
console_faces = [tuple(range(n-1,-1,-1)),tuple(range(5*n,6*n))]
for row in range(5):
    for j in range(n):
        console_faces.append((row*n+j,row*n+(j+1)%n,(row+1)*n+(j+1)%n,(row+1)*n+j))
mesh('Angular LED display and headlamp housing',console_vertices,console_faces,black,'Steering',b=.002)
for index in range(5):
    y = (index-2)*.024
    front_x = .303-abs(y)*.21
    bezel = cube('Continuous metallic lamp brow',(front_x,y,1.242),(.008,.024,.017),silver,
                 'Steering',.0016)
    bezel.rotation_euler[1] = -.18
    led = cube('Individual recessed forward LED lens',(front_x+.004,y,1.243),(.004,.016,.011),
               lens,'Steering',.0015)
    led.rotation_euler[1] = -.18
lcd = cube('Smoke-tinted console display',(.218,0,1.281),(.054,.076,.004),screen,'Steering',.003)
lcd.rotation_euler[1] = -.30
curve('Woven carrying strap loop',[(.220,.050,1.187),(.237,.063,1.090),(.261,.061,1.049),
      (.282,.059,1.085),(.262,.050,1.182)],.0044,black,'Steering')

# Left-mounted original folding stand, tucked rearward beneath the deck flange.
# The plated twin-screw bracket and bent round tip follow the spare-part photo.
stand_first = len(parts)
cube('Kickstand underside mounting flange',(-.151,.103,.181),(.053,.025,.008),black,b=.0028)
cube('Kickstand left pivot lug',(-.152,.114,.169),(.025,.020,.021),edge,b=.003)
for x in [-.168,-.136]:
    bolt('Kickstand mounting screw',x,.105,.177,.0031,axis='Z')
rod('Kickstand pivot axle',(-.152,.104,.167),(-.152,.129,.167),.008,black)
bolt('Kickstand recessed pivot screw',-.152,.129,.167,.0045)
curve('Rearward folded round kickstand leg',
      [(-.154,.120,.166),(-.181,.119,.165),(-.237,.116,.164),
       (-.292,.115,.163),(-.307,.114,.160),(-.318,.110,.150)],.0063,edge,resolution=6)
rod('Kickstand hinge sleeve',(-.165,.120,.166),(-.199,.118,.164),.0084,black)
rod('Short bent kickstand toe',(-.303,.114,.160),(-.318,.110,.150),.0075,black,r2=.008)
for part in parts[stand_first:]:
    part['vfDetail'] = 'kickstand'
rod('Left flank charging port rubber cap',(.116,.113,.239),(.116,.120,.239),.009,black)

# Convert everything to meshes, apply edge modifiers, then consolidate by assembly/material.
for o in list(parts):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 if o.type!='MESH':bpy.ops.object.convert(target='MESH')
 for mod in list(o.modifiers):
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except RuntimeError:pass
# Keep replaceable cockpit and kickstand parts isolated when batching by material.
for parent in groups.values():
    buckets = {}
    for obj in list(parent.children):
        if obj.type == 'MESH':
            key = (obj.data.materials[0].name,obj.get('vfCockpit',''),obj.get('vfDetail',''))
            buckets.setdefault(key,[]).append(obj)
    for (material,cockpit_part,detail),objects in buckets.items():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        if len(objects)>1:
            bpy.ops.object.join()
        suffix = f' | {cockpit_part or detail}' if cockpit_part or detail else ''
        objects[0].name = parent.name+' | '+material+suffix
# Store mount origins sensibly without moving geometry.
for gn,co in [('FrontWheel',(front,0,zax)),('RearWheel',(rear,0,zax)),('BatteryMount',(-.092,0,.239)),('ControllerMount',(.168,0,.237)),('MotorMount',(rear,0,zax))]:
 bpy.context.view_layer.update()
 p=groups[gn]; mats=[(c,c.matrix_world.copy()) for c in p.children];p.location=co
 bpy.context.view_layer.update()
 for c,m in mats:c.matrix_world=m
 bpy.context.view_layer.update()
root['dimensionsApprox']='1.34m long, 660mm handlebar width, 1.30m high'
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
# loop triangles need explicit calculation on authored mesh data.
tri=0
for p in groups.values():
 for o in p.children:
  if o.type=='MESH':o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Neutral studio for actual visual QA.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world.color=(.5,.5,.5);scene.view_settings.view_transform='AgX'
groundmat=mat('Studio warm grey',(.73,.75,.75),0,.85)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));ground=bpy.context.object;ground.name='STUDIO floor excluded from export';ground.data.materials.append(groundmat)
def area(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large softbox',(.5,-2.5,3.5),420,3);area('Fill softbox',(-2,1,2),320,2.5);area('Edge softbox',(2,2,2.7),450,2)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.lens=50

def aim_camera(location, target, scale):
    cam.location = location
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale = scale

hero_position,hero_target = (2.05,4.8,1.87),(.020,0,.652)
qa_dir = os.environ.get('G4_QA_DIR',os.path.join(ROOT,'artifacts/blender'))
if os.environ.get('G4_SKIP_QA') != '1':
    os.makedirs(qa_dir,exist_ok=True)
    for name,location,target,scale in [
        ('g4-three-quarter.png',hero_position,hero_target,1.59),
        ('g4-side.png',(0,5,.653),(0,0,.653),1.52),
        ('g4-kickstand-close.png',(-.42,2.5,.31),(-.198,.041,.224),.42),
        ('g4-cockpit-close.png',(-.56,1.41,1.74),(.221,0,1.247),.75),
    ]:
        aim_camera(location,target,scale)
        scene.render.filepath=os.path.join(qa_dir,name)
        bpy.ops.render.render(write_still=True)

# The operator-owned original .blend has separate edits; export this revision separately.
aim_camera(hero_position,hero_target,1.59)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'assets/blender/kukirin-g4-revised.blend'),compress=True)
report = {
    'asset':'kukirin-g4',
    'creator':'Blender',
    'triangles':tri,
    'meshObjects':sum(o.type=='MESH' for p in groups.values() for o in p.children),
    'glbBytes':os.path.getsize(export),
    'reference':'apps/web/public/assets/vehicles/kukirin-g4.webp',
    'sources':[
        'https://www.kukirinfactory.com/kukirin-g4-specification',
        'https://www.kukirinfactory.com/uploads/43829/page/p20260420150032639c4.jpg',
        'https://www.kukirinfactory.com/uploads/43829/files/G4-EN17128--REPORT.pdf',
        'https://kukirinofficial.com/products/g4-kickstand-footer',
    ],
    'stockHandlebarMm':660,
    'kickstandPose':'Rider-left underside bracket and rearward-folding tubular leg.',
    'limitations':'Photo-guided exterior. Part geometry, clearances and internal service assemblies are approximations.',
}
with open(os.path.join(ROOT,'artifacts/blender/g4-asset-note.json'),'w') as f:json.dump(report,f,indent=2)
print('G4_ASSET_REPORT '+json.dumps(report))
