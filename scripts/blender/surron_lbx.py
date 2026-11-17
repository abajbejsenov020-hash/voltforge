"""Photo-derived Sur-Ron Light Bee X. Run with Blender --background --python this_file.
Reference: public/assets/vehicles/surron-light-bee-x.webp (MXWraps green/yellow livery).
Dimensions are a visual reconstruction, not manufacturer CAD. X front, Z up, metres.
"""
import bpy, math, json, os
from mathutils import Vector
from math import sin, cos, pi

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)

def mat(name, color, metallic=0, rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=rough
    return m
frame=mat('Cast graphite aluminium',(.022,.028,.026),.62,.39)
black=mat('Satin black polymer',(.016,.020,.018),.08,.39)
rubber=mat('Knobby tyre rubber',(.013,.016,.015),0,.88)
seatmat=mat('Textured charcoal seat',(.038,.042,.04),0,.92)
silver=mat('Brushed steel',(.46,.50,.49),.92,.28)
darkmetal=mat('Machined gunmetal',(.095,.113,.108),.88,.26)
gold=mat('Anodized gold stanchions',(.64,.38,.07),.84,.22)
lime=mat('Fluorescent yellow green wrap',(.73,.94,.012),.12,.32)
chainmat=mat('Gold chain',(.37,.30,.11),.86,.36)
white=mat('White printed graphics',(.8,.84,.79),.02,.4)
red=mat('Rear red lamp',(.65,.008,.004),.1,.24)
lens=mat('Headlight lens',(.65,.78,.85),.4,.13)
root=bpy.data.objects.new('SurRonLBX',None); bpy.context.collection.objects.link(root)
root['source']='Photo reconstruction: supplied MXWraps Sur-Ron Light Bee X photograph'
root['units']='metres'; root['wheelbase_m']=1.25
groups={}
for name in ['Chassis','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount','Fork','Cockpit','Bodywork','RearSuspension','Drive']:
    e=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(e); e.parent=root; groups[name]=e

def finish(o,name,m,g='Chassis',smooth=True,bevel=0):
    o.name=name; o.data.materials.append(m); o.parent=groups[g]
    if hasattr(o.data,'polygons'):
        for p in o.data.polygons:p.use_smooth=smooth
    if bevel:
        mod=o.modifiers.new('Manufactured edge radii','BEVEL'); mod.width=bevel; mod.segments=1 if ('tread' in name or 'chain side' in name) else 3
        mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def mesh(name,verts,faces,m,g='Chassis',bevel=0,smooth=False):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o)
    return finish(o,name,m,g,smooth,bevel)
def box(name,loc,size,m,g='Chassis',bevel=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m,g,False,bevel)
def cyl(name,a,b,r,m,g='Chassis',vertices=24,r2=None):
    a,b=Vector(a),Vector(b); v=b-a
    if r2 is None:bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=v.length,location=(a+b)/2)
    else:bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r2,depth=v.length,location=(a+b)/2)
    o=bpy.context.object; o.rotation_mode='QUATERNION';o.rotation_quaternion=v.to_track_quat('Z','Y')
    o=finish(o,name,m,g,True)
    for p in o.data.polygons:
        if len(p.vertices)>4:p.use_smooth=False
    return o
def path(name,points,r,m,g='Chassis',resolution=3):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D';c.resolution_u=resolution
    c.bevel_depth=r;c.bevel_resolution=2
    sp=c.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(m);o.parent=groups[g];return o
def plate(name,poly,y,depth,m,g='Chassis',bevel=.006):
    n=len(poly);vs=[(x,y+d,z) for d in [-depth/2,depth/2] for x,z in poly]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,m,g,bevel)
def hollow(name,outer,inner,y,depth,m):
    def rounded(loop):
        out=[]
        for i in range(len(loop)):
            p0,p1,p2,p3=[Vector(loop[j%len(loop)]) for j in [i-1,i,i+1,i+2]]
            for j in range(4):
                t=j/4;v=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
                out.append(tuple(v))
        return out
    outer,inner=rounded(outer),rounded(inner)
    n=len(outer);vs=[(x,y+d,z) for d in [-depth/2,depth/2] for loop in [outer,inner] for x,z in loop];fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return mesh(name,vs,fs,m,bevel=.009)
def ring(name,x,y,z,R,r,m,g,depth=.007,N=96):
    vs=[(x+rad*cos(t*2*pi/N),y+d,z+rad*sin(t*2*pi/N)) for d in [-depth/2,depth/2] for rad in [R,r] for t in range(N)]
    fs=[]
    for i in range(N):
        j=(i+1)%N;fs += [(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)]
    return mesh(name,vs,fs,m,g,smooth=True)

# Wheel construction: cross-section rubber carcass, individual staggered tread blocks, spoked alloy rims.
def wheel(x,g):
    z=.313; N=96
    profile=[(.252,-.031),(.268,-.043),(.289,-.039),(.298,-.024),(.302,0),(.298,.024),(.289,.039),(.268,.043),(.252,.031)]
    vs=[(x+r*cos(a*2*pi/N),y,z+r*sin(a*2*pi/N)) for r,y in profile for a in range(N)]
    fs=[(j*N+i,j*N+(i+1)%N,((j+1)%len(profile))*N+(i+1)%N,((j+1)%len(profile))*N+i) for j in range(len(profile)) for i in range(N)]
    mesh('Moulded 19 inch offroad tyre',vs,fs,rubber,g,smooth=True)
    vs=[];fs=[]
    for i in range(54):
        for j in range(5):
            a=(i+(j%2)*.48)*2*pi/54;y=(j-2)*.017;rad=.305-abs(j-2)*.005
            radial=Vector((cos(a),0,sin(a)));tangent=Vector((-sin(a),0,cos(a)))
            center=Vector((x+rad*cos(a),y,z+rad*sin(a))); k=len(vs)
            for u,v,w in [(-1,-1,-1),(-1,1,-1),(1,1,-1),(1,-1,-1),(-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)]:
                vs.append(tuple(center+tangent*(u*.010)+Vector((0,v*.0065,0))+radial*(w*.007)))
            fs += [tuple(k+a for a in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
    mesh('Staggered knobby tread blocks',vs,fs,rubber,g,bevel=.0012)
    for y in [-.026,.026]:ring('Black anodized rim lip',x,y,z,.253,.239,darkmetal,g,.007)
    ring('Rim inner well',x,0,z,.245,.238,black,g,.048)
    cyl('Axle hub',(x,-.06,z),(x,.06,z),.030,darkmetal,g)
    for y in [-.043,.043]:
        cyl('Spoke flange',(x,y-.004,z),(x,y+.004,z),.039,silver,g)
        for i in range(18):
            a=i*2*pi/18+(0 if y<0 else pi/18);b=a+.24*(1 if i%2 else -1)
            cyl('Tensioned spoke',(x+.037*cos(a),y,z+.037*sin(a)),(x+.24*cos(b),y*.50,z+.24*sin(b)),.00135,silver,g,8)
    # Perforated steel rotor: open drill slots formed directly in annular mesh.
    yy=.061;N=120;rs=[.074,.080,.084,.092,.097,.101];vs=[];fs=[]
    for y in [yy-.0012,yy+.0012]:
        for r in rs:
            for i in range(N):
                a=i*2*pi/N;rr=r+(0.0018*sin(a*12) if r==rs[-1] else 0)
                vs.append((x+rr*cos(a),y,z+rr*sin(a)))
    count=N*len(rs)
    for j in range(len(rs)-1):
        for i in range(N):
            if j in [1,2] and i%10 in [2,3,4,5]:continue
            a=j*N+i;b=j*N+(i+1)%N;c=(j+1)*N+(i+1)%N;d=(j+1)*N+i
            fs.extend([(a,b,c,d),(a+count,d+count,c+count,b+count)])
    mesh('Drilled floating brake rotor',vs,fs,silver,g)
    for i in range(6):
        a=i*pi/3
        cyl('Rotor swept spider',(x+.029*cos(a),yy,z+.029*sin(a)),(x+.077*cos(a+.3),yy,z+.077*sin(a+.3)),.007,darkmetal,g,8)
        cyl('Rotor bolt',(x+.033*cos(a),yy-.003,z+.033*sin(a)),(x+.033*cos(a),yy-.006,z+.033*sin(a)),.004,silver,g,6)
    cal=box('Hydraulic brake caliper',(x-.071,yy+.016,z+.061),(.051,.032,.040),frame,g,.008)
    for dz in [-.010,.010]:cyl('Caliper piston plug',(x-.071,yy+.036,z+.061+dz),(x-.071,yy+.039,z+.061+dz),.006,lime,g,12)
    cyl('Axle nut',(x,-.086,z),(x,-.098,z),.012,silver,g,6)
wheel(.625,'FrontWheel');wheel(-.625,'RearWheel')

# Hollow cast perimeter spars, joining around a real battery aperture.
outer=[(.315,.855),(.207,.858),(-.075,.751),(-.241,.414),(-.206,.337),(-.065,.325),(.058,.392),(.167,.625)]
inner=[(.250,.789),(.197,.797),(-.029,.707),(-.174,.428),(-.146,.400),(-.076,.394),(.004,.440),(.112,.632)]
for s in [-1,1]:
    hollow('Hollow cast aluminium perimeter spar',outer,inner,s*.111,.037,frame)
    # Gusset and frame pivot plates, machining bosses and through bolts.
    plate('Cast pivot gusset',[(-.22,.43),(-.255,.37),(-.18,.30),(-.065,.325),(-.048,.39)],s*.13,.019,frame)
    for x,z,r in [(-.185,.374,.026),(.285,.816,.015),(-.074,.365,.013),(-.107,.739,.01)]:
        cyl('Cast mounting boss',(x,s*.117,z),(x,s*.15,z),r,frame)
        cyl('Hex frame bolt',(x,s*.15,z),(x,s*.156,z),r*.43,silver,vertices=6)
cyl('Steering head tube',(.282,0,.784),(.243,0,.908),.036,frame)
path('Lower cradle',[(.10,-.06,.44),(.073,-.10,.33),(-.07,-.10,.295),(-.21,-.07,.34)],.017,frame)
path('Lower cradle',[(.10,.06,.44),(.073,.10,.33),(-.07,.10,.295),(-.21,.07,.34)],.017,frame)

# Removable dark battery pack occupies opening; separate node for configurator.
plate('Battery enclosure',[(-.139,.425),(-.103,.648),(.145,.807),(.219,.763),(.099,.455),(.004,.391)],0,.177,black,'BatteryMount',.012)
plate('Battery side cover',[(-.109,.438),(-.08,.635),(.139,.778),(.181,.747),(.068,.468),(-.001,.419)],-.092,.006,darkmetal,'BatteryMount',.007)
path('Battery lid seam',[(.185,-.083,.797),(.105,-.094,.815),(-.075,-.085,.749)],.003,black,'BatteryMount')
box('Battery lift handle',(.065,0,.809),(.092,.105,.014),black,'BatteryMount',.006)
plate('Finned controller shell',[(.198,.726),(.225,.714),(.128,.509),(.086,.488),(.081,.54)],0,.144,frame,'ControllerMount',.005)
for i in range(10):
    z=.52+i*.017;x=.11+(z-.52)*.45
    cyl('Controller cooling fin',(x,-.079,z),(x,.079,z),.0045,darkmetal,'ControllerMount',8)
for s in [-1,1]:
    # Angular fluorescent MX wrap strips conform to each side spar and pack.
    y=s*.135
    for idx,p in enumerate([
        [(.105,.761),(.051,.738),(-.107,.432),(-.063,.416)],
        [(.146,.707),(.125,.663),(-.027,.727),(-.047,.766)],
        [(.047,.563),(.027,.514),(-.154,.601),(-.135,.645)],
        [(-.16,.696),(-.129,.749),(-.035,.717),(-.061,.675)]
    ]):plate('Lime MXWrap angular graphic',p,y,.001,lime,'Bodywork',.0002)
    plate('Black break in wrap',[(-.105,.596),(-.087,.62),(.064,.557),(.049,.53)],s*.137,.001,black,'Bodywork',.0001)

# Mid drive motor: finned cylindrical case, reduction cover, bolts and skid plate.
cyl('Mid mounted electric motor',(-.126,-.158,.365),(-.126,.158,.365),.090,frame,'MotorMount',64)
for y in [-.160,.160]:
    cyl('Motor end cover',(-.126,y-.004,.365),(-.126,y+.004,.365),.081,black,'MotorMount',64)
    ring('Machined motor cover ring',-.126,y,.365,.060,.055,darkmetal,'MotorMount',.004,64)
    cyl('Motor rotor centre',(-.126,y-.005,.365),(-.126,y+.005,.365),.038,frame,'MotorMount',48)
    for i in range(8):
        a=i*pi/4;xx=-.126+.071*cos(a);zz=.365+.071*sin(a)
        cyl('Motor case screw',(xx,y,zz),(xx,y+(0.007 if y>0 else -.007),zz),.004,silver,'MotorMount',6)
    for i in range(3):
        a=(i*.5+.2)*pi
        path('Lime motor ring accent',[(-.126+.048*cos(a+j*.06),y*1.06,.365+.048*sin(a+j*.06)) for j in range(5)],.0025,lime,'MotorMount')
plate('Formed motor bash guard',[(.07,.37),(.054,.297),(-.076,.273),(-.21,.294),(-.234,.328)],0,.19,black,'MotorMount',.007)

# Forged swingarm and open rear trellis.
for s in [-1,1]:
    y=s*.097
    plate('Forged tapered swingarm',[(-.20,.409),(-.32,.395),(-.65,.343),(-.665,.302),(-.60,.294),(-.29,.335),(-.18,.361)],y,.033,frame,'RearSuspension',.009)
    path('Swingarm raised rib',[(-.228,y+s*.019,.382),(-.43,y+s*.019,.346),(-.616,y+s*.019,.325)],.007,darkmetal,'RearSuspension')
    for a,b,r in [((-.145,y,.699),(-.45,y,.812),.016),((-.45,y,.812),(-.31,y,.529),.017),((-.31,y,.529),(-.145,y,.699),.012)]:cyl('Open rear seat trellis',a,b,r,frame,'RearSuspension')
    cyl('Passenger mounting boss',(-.319,y,.535),(-.319,y+s*.018,.535),.017,silver,'RearSuspension')
    cyl('Footpeg bracket',(-.19,y,.35),(-.24,s*.16,.315),.013,frame)
    peg=box('Serrated footpeg',(-.245,s*.193,.318),(.076,.074,.015),silver,bevel=.003)
    for i in range(5):box('Footpeg traction tooth',(-.275+i*.015,s*.218,.330),(.006,.008,.010),silver,bevel=.0005)
    cyl('Rear axle adjuster',(-.66,y,.317),(-.605,y,.317),.008,silver,'RearSuspension',12)
# Coil-over with clearly visible wound spring.
a=Vector((-.337,0,.487));b=Vector((-.184,0,.710));v=b-a;axis=v.normalized();u=Vector((0,1,0));w=axis.cross(u)
cyl('Shock body',a,b,.021,darkmetal,'RearSuspension');cyl('Shock piston',a-axis*.025,b,.008,silver,'RearSuspension')
points=[]
for i in range(241):
    t=i/240;co=a+v*(.08+.84*t)+(u*cos(t*9*2*pi)+w*sin(t*9*2*pi))*.032;points.append(tuple(co))
path('Nine turn rear shock coil',points,.0052,black,'RearSuspension',1)
for p in [a,b]:cyl('Shock collar',(p.x,-.036,p.z),(p.x,.036,p.z),.024,gold,'RearSuspension')

# Rear sprocket and individual chain links around the driven and output sprockets.
ring('Rear chain sprocket',-.625,.074,.313,.091,.066,darkmetal,'Drive',.006,72)
for i in range(10):
    a=i*2*pi/10;cyl('Sprocket spoke',(-.625+.03*cos(a),.074,.313+.03*sin(a)),(-.625+.07*cos(a+.15),.074,.313+.07*sin(a+.15)),.0065,darkmetal,'Drive',8)
for i in range(44):
    a=i*2*pi/44;o=box('Rear sprocket tooth',(-.625+.094*cos(a),.074,.313+.094*sin(a)),(.008,.008,.008),silver,'Drive',.001);o.rotation_euler.y=-a
ring('Jackshaft sprocket',-.22,.079,.392,.037,.019,silver,'Drive',.008,40)
chainpoints=[]
for i in range(24):
    t=i/24;chainpoints.append((-.625+(.405)*t,.313+.09+(.392+.036-(.313+.09))*t))
for i in range(14):
    a=pi/2-i*pi/14;chainpoints.append((-.22+.036*cos(a),.392+.036*sin(a)))
for i in range(24):
    t=i/24;chainpoints.append((-.22-.405*t,.392-.036+(.313-.09-(.392-.036))*t))
for i in range(27):
    a=-pi/2-i*pi/27;chainpoints.append((-.625+.09*cos(a),.313+.09*sin(a)))
for i,(x,z) in enumerate(chainpoints):
    nx,nz=chainpoints[(i+1)%len(chainpoints)];angle=math.atan2(nz-z,nx-x)
    for yy in [.068,.084]:
        o=box('Roller chain side plate',(x,yy,z),(.012,.0025,.006),chainmat,'Drive',.0018);o.rotation_euler.y=-angle
    cyl('Chain roller',(x,.068,z),(x,.084,z),.0025,silver,'Drive',8)
path('Rear hydraulic brake hose',[(-.62,-.105,.38),(-.48,-.12,.39),(-.32,-.13,.43),(-.2,-.11,.48)],.003,black,'Drive')

# Gold USD fork, triple clamps and swept handlebar.
for s in [-1,1]:
    y=s*.083
    A=Vector((.625,y,.313));B=Vector((.296,y,.938));D=(B-A).normalized()
    cyl('Gold USD fork stanchion',A+D*.21,B,.019,gold,'Fork',40)
    cyl('Black fork lower',A-D*.01,A+D*.225,.022,black,'Fork',32)
    cyl('Fork lower seal',A+D*.205,A+D*.23,.025,darkmetal,'Fork',32)
    cyl('Front axle lug',(.625,y-.025,.313),(.625,y+.025,.313),.028,frame,'Fork',32)
    plate('Fork lime stripe',[(.526,.486),(.539,.462),(.615,.324),(.598,.325)],y+s*.024,.001,lime,'Fork',.0001)
    for t in [.77,.88]:
        p=A+(B-A)*t;cyl('Triple clamp collar',(p.x,y-.03,p.z),(p.x,y+.03,p.z),.026,darkmetal,'Fork')
    cyl('Fork top adjuster',B,B+D*.012,.013,gold,'Fork',16)
for x,z in [(.365,.808),(.329,.876)]:box('Forged triple clamp',(x,0,z),(.063,.222,.021),darkmetal,'Fork',.009)
path('Swept riser handlebar',[(.284,-.363,1.041),(.267,-.23,1.018),(.281,-.13,.985),(.298,0,.982),(.281,.13,.985),(.267,.23,1.018),(.284,.363,1.041)],.011,darkmetal,'Cockpit')
for s in [-1,1]:
    y=s*.312
    cyl('Ribbed rubber grip',(.28,s*.260,1.034),(.288,s*.378,1.047),.017,rubber,'Cockpit',32)
    for i in range(11):cyl('Grip raised ring',(.28,s*(.269+i*.009),1.035),(.28,s*(.272+i*.009),1.035),.0185,rubber,'Cockpit',24)
    cyl('Bar end plug',(.288,s*.376,1.047),(.288,s*.387,1.047),.018,black,'Cockpit')
    box('Brake master cylinder',(.301,s*.221,1.038),(.052,.039,.024),black,'Cockpit',.005)
    path('Curved brake lever',[(.325,s*.23,1.033),(.352,s*.27,1.028),(.358,s*.328,1.034)],.005,silver,'Cockpit')
    path('Brake cable',[(.323,s*.222,1.033),(.401,s*.182,1.035),(.435,s*.10,.92),(.487,s*.10,.62),(.589,s*.105,.39)],.003,black,'Cockpit')
    box('Handlebar clamp',(.294,s*.049,.993),(.039,.027,.043),frame,'Cockpit',.005)
box('Compact digital dash',(.343,0,1.002),(.046,.075,.017),black,'Cockpit',.005)
box('LCD surface',(.345,0,1.012),(.037,.058,.001),lens,'Cockpit',.001)
box('Red kill switch',(.290,-.246,1.060),(.015,.017,.009),red,'Cockpit',.003)
# Round central LED light faces +X, translucent-style PBR lens and machined bezel.
cyl('Round LED headlamp housing',(.367,0,.925),(.420,0,.925),.038,black,'Cockpit',48)
cyl('Headlamp black bezel',(.421,0,.925),(.426,0,.925),.034,black,'Cockpit',48)
cyl('Headlamp glass lens',(.427,0,.925),(.429,0,.925),.028,lens,'Cockpit',48)
cyl('LED projector',(.429,0,.925),(.431,0,.925),.014,white,'Cockpit',32)

# Curved, thin seat and fenders, using varying width section lofts.
def loft(name,sections,m,g,bevel=.003):
    if name=='Contoured narrow saddle':
        vs=[];fs=[];N=9
        for x,w,z,t in sections:
            edge=min(.012,t*.35)
            vs.extend([(x,y,zz) for y,zz in [(-w*.72,z),(-w*.95,z-edge),(-w,z-t*.52),(-w*.82,z-t),(w*.82,z-t),(w,z-t*.52),(w*.95,z-edge),(w*.72,z),(0,z+.007)]])
        fs=[tuple(range(N-1,-1,-1)),tuple(range(len(vs)-N,len(vs)))]
        for i in range(len(sections)-1):
            for j in range(N):fs.append((N*i+j,N*i+(j+1)%N,N*(i+1)+(j+1)%N,N*(i+1)+j))
        return mesh(name,vs,fs,m,g,.003,True)
    vs=[]
    for x,width,z,thick in sections:vs += [(x,-width,z),(x,width,z),(x,width,z-thick),(x,-width,z-thick)]
    fs=[(0,3,2,1),(len(vs)-4,len(vs)-3,len(vs)-2,len(vs)-1)]
    for i in range(len(sections)-1):
        for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    return mesh(name,vs,fs,m,g,bevel,True)
loft('Contoured narrow saddle',[(-.60,.027,.876,.014),(-.55,.055,.873,.028),(-.47,.070,.861,.042),(-.36,.080,.844,.048),(-.24,.077,.827,.045),(-.16,.060,.818,.032),(-.105,.033,.815,.024)],seatmat,'Bodywork',.012)
loft('Seat underside pan',[(-.635,.022,.886,.008),(-.52,.065,.838,.013),(-.30,.067,.786,.014),(-.105,.031,.787,.015)],black,'Bodywork')
loft('Sculpted battery top and saddle nose fairing',[(.19,.062,.831,.022),(.10,.091,.831,.037),(.008,.102,.817,.042),(-.075,.087,.807,.038),(-.135,.052,.802,.027)],black,'Bodywork',.012)
path('Saddle stitched seam',[(-.584,-.039,.874),(-.50,-.066,.864),(-.37,-.078,.843),(-.22,-.072,.825),(-.14,-.047,.820)],.001,frame,'Bodywork')
loft('Front offroad fender',[(.29,.025,.741,.007),(.41,.051,.752,.009),(.58,.061,.768,.009),(.76,.048,.757,.007),(.87,.006,.738,.005)],black,'Bodywork')
path('Front fender embossed ridge',[(.33,0,.753),(.51,0,.779),(.70,0,.778),(.84,0,.748)],.0035,darkmetal,'Bodywork')
loft('Rear wheel mudguard',[(-.25,.029,.48,.008),(-.35,.046,.57,.008),(-.46,.050,.658,.008),(-.55,.043,.693,.008),(-.61,.018,.674,.006)],black,'Bodywork')
plate('Front number panel',[(.339,.892),(.397,.869),(.458,.753),(.409,.741),(.354,.824)],0,.103,black,'Bodywork',.007)
plate('Number panel fluorescent edge',[(.409,.859),(.417,.839),(.459,.754),(.443,.755)],-.054,.001,lime,'Bodywork',.001)
box('Rear tail lamp',(-.438,0,.826),(.018,.044,.018),red,'Bodywork',.003)
# Routing and minor fasteners visible in close-up.
path('Motor power loom',[(.14,.092,.58),(.098,.12,.46),(-.03,.126,.40),(-.11,.114,.40)],.009,black,'MotorMount')
path('Battery loom',[(.16,-.07,.78),(.22,-.10,.76),(.19,-.10,.66)],.006,black,'BatteryMount')
for y in [-.154,.154]:
    cyl('Pivot cap',(-.185,y,.374),(-.185,y*1.035,.374),.015,darkmetal)
    cyl('Pivot hex screw',(-.185,y*1.035,.374),(-.185,y*1.06,.374),.008,silver,vertices=6)

# Bake modifiers and combine surfaces per material inside semantic groups for web draw calls.
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.context.scene.objects):
    if o.type in {'MESH','CURVE'}:
        bpy.context.view_layer.objects.active=o;o.select_set(True)
        bpy.ops.object.convert(target='MESH');o.select_set(False)
for g,parent in groups.items():
    buckets={}
    for o in list(parent.children):
        if o.type=='MESH':buckets.setdefault(o.data.materials[0].name,[]).append(o)
    for material,obs in buckets.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in obs:o.select_set(True)
        bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join()
        obs[0].name=f'{g} | {material}';obs[0]['part_group']=g

os.makedirs(os.path.join(BASE,'assets/blender'),exist_ok=True)
os.makedirs(os.path.join(BASE,'apps/web/public/models'),exist_ok=True)
os.makedirs(os.path.join(BASE,'artifacts/blender'),exist_ok=True)
# Embed the visual reference as an image datablock for future Blender inspection.
ref=bpy.data.images.load(os.path.join(BASE,'apps/web/public/assets/vehicles/surron-light-bee-x.webp'));ref.pack()
bpy.ops.object.select_all(action='DESELECT')
for o in [root]+list(groups.values())+[o for o in bpy.context.scene.objects if o.type=='MESH']:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(BASE,'apps/web/public/models/surron-lbx.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in root.children_recursive if o.type=='MESH')
coords=[o.matrix_world @ Vector(c) for o in root.children_recursive if o.type=='MESH' for c in o.bound_box]
dimensions=[round(max(c[i] for c in coords)-min(c[i] for c in coords),4) for i in range(3)]
print('LBX_GEOMETRY',json.dumps({'triangles':triangles,'meshes':sum(o.type=='MESH' for o in root.children_recursive),'dimensions_m':dimensions}))

# Studio rig is stored in the .blend only; excluded from GLB selection above.
groundmat=mat('Studio warm light grey',(.67,.69,.68),0,.86)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.004));ground=bpy.context.object;ground.name='Studio floor (render only)';ground.data.materials.append(groundmat)
world=bpy.data.worlds.new('Neutral studio');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.60,.65,.70,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
def area(name,loc,power,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large key',(1.4,-2.2,3.1),450,3);area('Rear rim',(-1.5,1.1,2.2),400,2);area('Front fill',(2,1,1.4),180,2)
bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='LBX studio camera';bpy.context.scene.camera=camera
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
def render(name,loc,ortho):
    camera.location=loc;camera.rotation_euler=(Vector((0,0,.535))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=ortho
    scene.render.filepath=os.path.join(BASE,'artifacts/blender/'+name+'.png');bpy.ops.render.render(write_still=True)
render('lbx-three-quarter',(2.3,4,1.60),2.24)
render('lbx-side',(0,12,1.24),2.22)
camera.location=(2.3,4,1.60);camera.rotation_euler=(Vector((0,0,.535))-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'assets/blender/surron-lbx.blend'))
