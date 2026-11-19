"""Photo-guided KuKirin / Ausom catalog build, Blender 4.5 LTS.
Run: Blender --background --threads 2 --python scripts/blender/batches/scooters/build.py
Optional after --: canonical key(s). No measured CAD accuracy is claimed.
All geometry is authored here; family parameters encode observed structural differences.
"""
import bpy, bmesh, math, os, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin,cos,pi
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'apps/web/public/models/catalog/scooters'
BLENDS=ROOT/'assets/blender/catalog/scooters'
PROOF=ROOT/'artifacts/blender/catalog/scooters'
MANIFEST=ROOT/'apps/web/src/data/blender-scooters.json'
for d in [OUT,BLENDS,PROOF]: d.mkdir(parents=True,exist_ok=True)
# dimensions are approximate photographic proportions in metres: wheelbase, tire radius,
# deck length/width/height, total height, bar width. No factory dimensional claim.
C={
'kukirin-g2-max':dict(family='G2 Max single motor', kind='max', wb=1.006, r=.127, dl=.583, dw=.211, dz=.243, depth=.056, h=1.262, bar=.605, tire_half=.041, dual=False, tread='block', neck=.476, lamp='low-round', stem='telescopic', kick=.082, stand=(.138, -.018, .027), notes='Black telescopic mast, tubular low headlamp, sculpted orange solid arms, open front rim, rear hub, and split X-pattern grip tape.'),
'kukirin-g2-master':dict(family='G2 Master dual motor', kind='master', wb=1.006, r=.127, dl=.597, dw=.218, dz=.231, depth=.056, h=1.279, bar=.595, tire_half=.041, dual=True, tread='block', neck=.491, lamp='low-round', stem='telescopic', kick=.078, stand=(.120, -.012, .025), notes='Compact low deck, low four-optic round lamp, sculpted black castings with orange inserts, exposed orange coils and twin hub motors.'),
'kukirin-g2':dict(family='G2 open-neck chassis', kind='g2', wb=1.004, r=.127, dl=.563, dw=.201, dz=.233, depth=.050, h=1.231, bar=.660, tire_half=.037, dual=False, tread='block', neck=.435, lamp='console', stem='square', kick=.089, stand=(.139, -.144, .004), notes='Sweep-back gray open headstock, orange checkered side markings, compact rear kickplate, cast open front wheel and folded stand.'),
'kukirin-g4-ultra':dict(family='G4 Ultra dual motor', kind='ultra', wb=1.061, r=.1397, dl=.639, dw=.263, dz=.247, depth=.053, h=1.242, bar=.650, tire_half=.047, dual=True, tread='street', neck=.484, lamp='console', stem='square', kick=.095, stand=(.153, -.147, .005), notes='Wide graphite deck, two enclosed hubs in 11-inch road tires, open triangular neck, geometric orange graphics and folded stand.'),
'kukirin-m4-max':dict(family='M4 Max telescopic fork',kind='m4',wb=1.02,r=.130,dl=.61,dw=.225,dz=.262,h=1.27,bar=.65,dual=False,tread='block',neck=.46,lamp='low-square',stem='telescopic',kick=.105,notes='Silver sculpted deck extrusion, conventional twin telescopic front fork, red rear damper and red stem clamp.'),
'kukirin-t4':dict(family='T4 long low deck',kind='t4',wb=1.06,r=.128,dl=.65,dw=.22,dz=.247,h=1.23,bar=.64,dual=False,tread='block',neck=.46,lamp='console',stem='square',kick=.09,notes='Low long sculpted deck, gray triangular windowed arms, orange thin arm insets; short angular fenders.'),
'kukirin-g2-pro-abe':dict(family='G2 Pro regional', kind='pro', wb=.941, r=.1143, dl=.554, dw=.192, dz=.214, depth=.047, h=1.261, bar=.590, tire_half=.037, dual=False, tread='block', neck=.424, lamp='low-square', stem='telescopic', kick=.093, abe=True, stand=(.116, -.140, .004), notes='Seatless photographed ABE with smoke-gray mast, upright rear plate holder, road reflectors, rectangular light and tucked stand.'),
'kukirin-g3-pro':dict(family='G3 Pro removable battery chassis', kind='g3', wb=1.041, r=.127, dl=.564, dw=.213, dz=.241, depth=.054, h=1.323, bar=.630, tire_half=.041, dual=True, tread='block', neck=.465, lamp='twin-low', stem='square', kick=.080, stand=(.111, -.010, .022), notes='Through-cut orange truss arms, twin low headlamps in a shared cage, orange mast extrusion, twin-motor wheels and bolted removable deck rails.'),
'kukirin-g2-pro-vmp':dict(family='G2 Pro regional', kind='pro', wb=.941, r=.1143, dl=.554, dw=.192, dz=.214, depth=.047, h=1.261, bar=.590, tire_half=.037, dual=False, tread='block', neck=.424, lamp='low-square', stem='telescopic', kick=.091, vmp=True, stand=(.112, -.021, .025), notes='Seatless photographed VMP, with a square front light, front steering side reflector, slim mast, slotted rear support and rear permit mount.'),
'kukirin-g2-pro':dict(family='G2 Pro seated', kind='pro', wb=.941, r=.1143, dl=.554, dw=.192, dz=.214, depth=.047, h=1.262, bar=.590, tire_half=.037, dual=False, tread='block', neck=.424, lamp='low-round', stem='telescopic', kick=.097, seat=True, stand=(.112, -.021, .025), notes='Photographed seated variant with braced pedestal, sprung seat post, orange clamp, contoured saddle, open front rim and slim orange arms.'),
'ausom-dt2-pro':dict(family='Ausom DT2 Pro',kind='dt2',wb=1.08,r=.145,dl=.67,dw=.265,dz=.295,h=1.35,bar=.70,dual=True,tread='street',neck=.54,lamp='console',stem='square',kick=.12,notes='Wide angular faceted deck, long swept neck, dark cast suspension arms, rectangular clipped fenders and two hub motors.'),
'ausom-l2-max-dual':dict(family='Ausom L2 Max',kind='l2',wb=1.03,r=.132,dl=.64,dw=.23,dz=.266,h=1.30,bar=.68,dual=True,tread='street',neck=.50,lamp='fender',stem='square',kick=.105,notes='Slimmer deep gray deck with pointed side caps, angular shallow-V arms, two hub motors, front fender light and slotted stem panel.'),
'ausom-gosoul-2-pro-dual-motor':dict(family='Ausom Gosoul 2 Pro ShocFree',kind='gosoulpro',wb=1.04,r=.136,dl=.63,dw=.25,dz=.273,h=1.31,bar=.68,dual=True,tread='block',neck=.49,lamp='high-square',stem='square',kick=.105,notes='ShocFree leading swingarm front suspension, dual black hub motors, faceted wide deck and purple illuminated flank strip.'),
'ausom-k20-pro-dual-motor':dict(family='Ausom K20 / Laluz 2 Pro',kind='k20',wb=1.015,r=.133,dl=.62,dw=.24,dz=.268,h=1.29,bar=.68,dual=True,tread='block',neck=.46,lamp='high-square',stem='square',kick=.10,notes='Conventional telescopic front fork, gold rim stripes, purple deck LED strip and rear adjustable spring; swallow handlebar.'),
'ausom-laluz-2-pro-dual-motor':dict(family='Ausom K20 / Laluz 2 Pro',kind='k20',wb=1.015,r=.133,dl=.62,dw=.24,dz=.268,h=1.29,bar=.68,dual=True,tread='block',neck=.46,lamp='high-square',stem='square',kick=.10,notes='Manufacturer-confirmed alias of K20 Pro (Laluz 2 Pro), intentionally same physical geometry; full-size primary reference replaces corrupted thumbnail.'),
'ausom-f1-max':dict(family='Ausom F1 Max dual spring',kind='f1',wb=1.10,r=.142,dl=.67,dw=.26,dz=.29,h=1.34,bar=.72,dual=True,tread='block',neck=.49,lamp='twin-low',stem='square',kick=.13,notes='Two exposed front coil dampers, sculpted carbon-pattern-looking arms, ribbed long deck, twin round low headlamps and tall gold fold lever; manufacturer clean photo supplements action reference.'),
'ausom-gosoul-2':dict(family='Ausom Gosoul 2 single motor',kind='gosoul',wb=1.00,r=.132,dl=.62,dw=.24,dz=.265,h=1.29,bar=.66,dual=False,tread='street',neck=.47,lamp='high-square',stem='square',kick=.105,notes='Single rear hub motor, open-spoked front wheel, solid angular fork side plates and diagonal ribbed deck flank; no purple strip.'),
}

KUKIRIN_SOURCE = {
    "kukirin-g2-max": "kukirin-g2-max-electric-scooter-adults",
    "kukirin-g2-master": "kukirin-g2-master-electric-scooter-for-adults",
    "kukirin-g2": "kukirinkugoo-kirin-2024-g2-electric-scooter",
    "kukirin-g4-ultra": "kukirin-g4-ultra-electric-scooter",
    "kukirin-g2-pro-abe": "kukirin-g2-pro-electric-scooter-abe-certified",
    "kukirin-g3-pro": "kukirin-g3-pro-off-road-electric-scooter",
    "kukirin-g2-pro-vmp": "kukirin-kugoo-kirin-g2-pro-electric-scooter-dgt",
    "kukirin-g2-pro": "kukirin-g2-pro-electric-scooter-with-seat",
}


def mat(name,col,metal=0,rough=.4,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emit
 return m

def finish(o,name,m,parent='Chassis',smooth=False):
 o.name=name;o.data.materials.append(m);o.parent=groups[parent];parts.append(o)
 if smooth and o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o

def bevel(o,w=.003):
 if w:
  q=o.modifiers.new('Manufactured edge radius','BEVEL');q.width=w;q.segments=2
  q=o.modifiers.new('Weighted machined normals','WEIGHTED_NORMAL');q.keep_sharp=True
 return o

def cube(name,loc,size,m,parent='Chassis',b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return bevel(finish(o,name,m,parent),b)

def mesh(name,v,f,m,parent='Chassis',smooth=False,b=0):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);return bevel(finish(o,name,m,parent,smooth),b)

def profile(name,pts,width,m,parent='Chassis',y=0,b=.003):
 n=len(pts);v=[(x,y+s*width/2,z) for s in [-1,1] for x,z in pts];f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,v,f,m,parent,b=b)

def rod(name,a,b,r,m,parent='Chassis',n=24,r2=None):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,name,m,parent,True)

def curve(name,pts,r,m,parent='Chassis'):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=8;d.bevel_depth=r;d.bevel_resolution=2;s=d.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);return finish(o,name,m,parent)

def bolt(name,p,r=.005,parent='Chassis',axis='Y'):
 d=Vector({'Y':(0,1,0),'X':(1,0,0),'Z':(0,0,1)}[axis])*.002;p=Vector(p);rod(name,p-d,p+d,r,silver,parent,6);rod(name+' hex socket',p+d,p+d*1.06,r*.44,black,parent,6)

def ring(name,x,y,z,ro,ri,width,m,parent='Chassis',n=48):
 v=[]
 for yy,r in [(y-width/2,ro),(y+width/2,ro),(y-width/2,ri),(y+width/2,ri)]:v += [(x+r*cos(i*2*pi/n),yy,z+r*sin(i*2*pi/n)) for i in range(n)]
 f=[]
 for i in range(n):
  j=(i+1)%n
  for a,b in [(0,1),(2,0),(1,3),(3,2)]:f.append((a*n+i,a*n+j,b*n+j,b*n+i))
 return mesh(name,v,f,m,parent,True)

def label(name,text,loc,size,m,parent='Chassis',angle=0):
 d=bpy.data.curves.new(name,'FONT');d.body=text;d.size=size;d.extrude=.00008;d.align_x='CENTER';d.align_y='CENTER';o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;u=Vector((cos(angle),0,sin(angle)));v=Vector((-sin(angle),0,cos(angle)));o.rotation_euler=Matrix((u,v,u.cross(v))).transposed().to_euler();return finish(o,name,m,parent)

def shock(name,a,b,r=.018,coil=None):
 a=Vector(a);b=Vector(b);d=b-a;u=d.normalized();e=u.cross(Vector((0,1,0))).normalized();w=u.cross(e);rod(name+' damper',a,a+d*.63,r,black);rod(name+' exposed piston',a+d*.45,b,r*.43,silver)
 v=[];f=[];N=112;nn=7
 for i in range(N+1):
  t=i/N;aa=t*2*pi*7;p=a+d*(.12+.74*t)+r*1.25*(e*cos(aa)+w*sin(aa))
  for j in range(nn):v.append(p+.0026*(e*cos(j*2*pi/nn)+w*sin(j*2*pi/nn)))
 for i in range(N):
  for j in range(nn):f.append((i*nn+j,i*nn+(j+1)%nn,(i+1)*nn+(j+1)%nn,(i+1)*nn+j))
 mesh(name+' regular helical coil',v,f,coil or steel,smooth=True)
 for p in [a,b]:rod(name+' spring end cap',p-u*.004,p+u*.004,r*1.35,steel)

def fender(name,x,r,w,angular=False,rear=False,compact=False):
 if angular:
  # Real faceted raised canopy: flat top and sloping quarter panels.
  pts=[(x-r*.86,R+r*.66),(x-r*.57,R+r*1.02),(x+r*.42,R+r*1.04),(x+r*.91,R+r*.62),(x+r*.83,R+r*.56),(x+r*.37,R+r*.96),(x-r*.53,R+r*.95),(x-r*.80,R+r*.60)]
  profile(name,pts,w,black,b=.002)
 else:
  v=[];f=[];n=38;nw=6
  start=(.12 if compact and rear else -.09 if rear else .23)*pi;end=(.89 if rear else .97)*pi
  for rr in [r,r+.004]:
   for j in range(nw+1):
    y=(j/nw-.5)*w;rad=rr-.006*(2*abs(y)/w)**3
    for i in range(n+1):a=start+(end-start)*i/n;v.append((x+rad*cos(a),y,R+rad*sin(a)))
  S=(n+1)*(nw+1)
  for layer in [0,1]:
   for j in range(nw):
    for i in range(n):a=layer*S+j*(n+1)+i;f.append((a,a+1,a+n+2,a+n+1))
  for j in [0,nw]:
   for i in range(n):a=j*(n+1)+i;f.append((a,a+1,a+1+S,a+S))
  for i in [0,n]:
   for j in range(nw):a=j*(n+1)+i;f.append((a,a+n+1,a+n+1+S,a+S))
  mesh(name,v,f,black,smooth=True)
 if rear:
  for sy in [-1,1]:rod('Rear fender metal support',(x,sy*(w/2-.005),R),(x-r*.6,sy*(w/2-.005),R+r*.86),.0045,steel)
  if not compact:
   profile('Rear descending license and spray flap',[(x-r*.88,R+r*.72),(x-r*1.05,R+r*.20),(x-r*.98,R+r*.19),(x-r*.79,R+r*.73)],w*.73,black,b=.002)
   cube('Rear red tail optical lens',(x-r*.89,0,R+r*.72),(.009,w*.67,.024),red,b=.002)

def tire(x,parent,c):
 rr=c['r'];wide=c.get('tire_half',.044 if rr<.14 else .052);na=192;nb=28;v=[];f=[]
 for j in range(nb+1):
  t=-pi/2+pi*j/nb;y=wide*sin(t);base=rr-.038+.038*cos(t)
  for i in range(na):
   a=i*2*pi/na
   if c['tread']=='block':
    phase=(i/na*40+.16*(j%2))%1;cross=(j/nb*5)%1;cut=.0048*(max(0,1-abs(phase-.5)/.13)+.65*max(0,1-abs(cross-.5)/.15))*max(0,cos(t))
   else:
    phase=(i/na*35+.7*abs(sin(t)))%1;cut=.0055*max(0,1-abs(phase-.5)/.16)*cos(t)**1.3
   r=base-cut;v.append((x+r*cos(a),y,rr+r*sin(a)))
 for j in range(nb):
  for i in range(na):f.append((j*na+i,j*na+(i+1)%na,(j+1)*na+(i+1)%na,(j+1)*na+i))
 mesh(parent+' sculpted tire tread',v,f,rubber,parent,True)
 hub=c['dual'] or parent=='RearWheel';rim=rr-.043
 for sy in [-1,1]:
  ring('Tire bead ridge',x,sy*wide*.92,rr,rim+.004,rim-.001,.005,rubber,parent)
  ring('Alloy rim lip',x,sy*wide*.94,rr,rim,rim-.009,.007,steel,parent)
  if c['kind'] in ['max','pro','k20']:ring('Colored rim pinstripe',x,sy*(wide+.001),rr,rim-.002,rim-.004,.001,gold if c['kind']=='k20' else orange,parent)
 if hub:
  rod('Enclosed brushless hub motor',(x,-wide*.91,rr),(x,wide*.91,rr),rim*.84,black,'MotorMount',48)
  for sy in [-1,1]:
   ring('Hub end cover circular seam',x,sy*(wide+.001),rr,rim*.80,rim*.74,.003,steel if c['kind']=='g3' else edge,'MotorMount')
   for k in range(10):
    a=k*2*pi/10;bolt('Hub perimeter cover bolt',(x+rim*.71*cos(a),sy*(wide+.005),rr+rim*.71*sin(a)),.0023,'MotorMount')
   if c['kind']=='f1':
    for k in range(24):
     a=k*2*pi/24;rod('F1 radial motor face rib',(x+.022*cos(a),sy*(wide+.003),rr+.022*sin(a)),(x+rim*.73*cos(a+.1),sy*(wide+.003),rr+rim*.73*sin(a+.1)),.0018,silver,'MotorMount',6)
 else:
  rod('Front wheel hub',(x,-wide,rr),(x,wide,rr),.022,edge,parent)
  for k in range(10):
   a=k*2*pi/10
   for sy in [-1,1]:rod('Cast swept wheel spoke',(x+.022*cos(a),sy*wide*.66,rr+.022*sin(a)),(x+(rim-.009)*cos(a+.18),sy*wide*.85,rr+(rim-.009)*sin(a+.18)),.0052,steel,parent,10)
 # Open brake rotor with real ventilation voids between steel bridges.
 dy=(wide+.014) if c['dual'] and parent=='FrontWheel' else (-wide-.014);ro=rr*.59;ri=ro*.81
 ring('Disc steel braking band',x,dy,rr,ro,ri,.002,rotor,parent,72)
 ring('Disc inner bolt mounting ring',x,dy,rr,ro*.43,ro*.33,.002,rotor,parent)
 for k in range(8):
  a=k*2*pi/8;rod('Brake rotor spider',(x+ro*.39*cos(a),dy,rr+ro*.39*sin(a)),(x+ri*cos(a+.25),dy,rr+ri*sin(a+.25)),.0027,rotor,parent,8)
  bolt('Rotor mounting screw',(x+ro*.38*cos(a),dy-.002,rr+ro*.38*sin(a)),.0022,parent)
 for k in range(24):
  a=k*2*pi/24;rod('Rotor ventilation slot',(x+ro*.87*cos(a),dy-.0015,rr+ro*.87*sin(a)),(x+ro*.96*cos(a+.025),dy-.0015,rr+ro*.96*sin(a+.025)),.0010,black,parent,6)
 cube('Hydraulic disc caliper',(x-.043,dy-.008,rr+.050),(.03,.023,.041),black,parent,.004)
 for sy in [-1,1]:
  rod('Axle washer',(x,sy*(wide+.012),rr),(x,sy*(wide+.029),rr),.014,steel,parent,24);bolt('Axle socket nut',(x,sy*(wide+.030),rr),.010,parent)

# Rectangular slotted planar shapes retain actual holes, rather than painted black fake holes.
def window_arm(name,a,b,width,material,y):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();n=Vector((-d[1],d[0]));A=a+n*.024;B=b+n*.023;CC=b-n*.022;D=a-n*.035
 # Extruded cast perimeter with a genuine through-opening and flat machined faces.
 outer=[A,B,CC,D];center=sum(outer,Vector((0,0)))/4
 inner=[center+d*(p-center).dot(d)*.64+n*(p-center).dot(n)*.42 for p in outer]
 v=[(p[0],yy,p[1]) for yy in [y-width/2,y+width/2] for contour in [outer,inner] for p in contour];f=[]
 for i in range(4):
  j=(i+1)%4
  f.extend([(i,j,4+j,4+i),(8+i,12+i,12+j,8+j),(i,8+i,8+j,j),(4+i,4+j,12+j,12+i)])
 mesh(name+' flat cast plate with through window',v,f,material,b=.003)

def suspended_arm(c, side, pivot_x, pivot_z, axle_x, y):
    start = Vector((pivot_x, pivot_z))
    end = Vector((axle_x, R))
    forward = (end - start).normalized()
    normal = Vector((-forward.y, forward.x))
    length = (end - start).length
    sign = 1 if y > 0 else -1
    kind = c['kind']

    def shape(points):
        return [tuple(start + forward * along * length + normal * across)
                for along, across in points]

    if kind == 'g3':
        # The inner taper follows the deep outer axle boss and leaves an open truss.
        outer = shape([(-.15, .042), (.23, .049), (.98, .026), (1.11, .008),
                       (1.10, -.017), (.86, -.024), (.13, -.037), (-.16, -.017)])
        inner = shape([(.17, .015), (.36, .022), (.73, .004), (.81, -.001),
                       (.78, -.005), (.66, -.010), (.30, -.013), (.15, -.004)])
        thickness = .024
        points = [(x, face_y, z) for face_y in (y - thickness / 2, y + thickness / 2)
                  for contour in (outer, inner) for x, z in contour]
        count = len(outer)
        faces = []
        for i in range(count):
            j = (i + 1) % count
            faces.extend([(i, j, count + j, count + i),
                          (2*count + i, 3*count + i, 3*count + j, 2*count + j),
                          (i, 2*count + i, 2*count + j, j),
                          (count + i, count + j, 3*count + j, 3*count + i)])
        mesh(side + ' orange through-cut suspension truss', points, faces, orange, b=.003)
    elif kind == 'master':
        profile(side + ' sculpted forged relief casting',
                shape([(-.14, .029), (.21, .036), (.51, .022), (.85, .022),
                       (1.13, .013), (1.13, -.016), (.94, -.025), (.58, -.023),
                       (.32, -.032), (-.14, -.024)]), .025, edge, y=y, b=.006)
        profile(side + ' recessed outer machined facet',
                shape([(.15, .017), (.48, .013), (.86, .013), (1.05, -.006),
                       (.79, -.014), (.43, -.014)]), .0035, black, y=y+sign*.013, b=.0015)
        accent_start = .48 if side == 'Rear' else .64
        profile(side + ' orange suspension face inlay',
                shape([(accent_start, -.010), (.91, -.010), (.96, .006),
                       (.75, .009)]), .002, orange, y=y+sign*.015, b=.001)
        for along in (.63, .84):
            x, z = shape([(along, -.004)])[0]
            bolt(side + ' inlay screw', (x, y+sign*.016, z), .0027)
    else:
        orange_arm = kind in ['max', 'pro']
        profile(side + ' shaped enclosed alloy swingarm',
                shape([(-.12, .025), (.14, .031), (.64, .023), (1.02, .021),
                       (1.13, .012), (1.13, -.013), (.91, -.025), (.35, -.024),
                       (-.12, -.019)]),
                .024, orange if orange_arm else paint, y=y, b=.006)
        if orange_arm:
            for along in (.28, .44, .60):
                profile(side + ' tapered suspension casting recess',
                        shape([(along-.051, .011), (along+.05, .009),
                               (along+.04, .002), (along-.025, .001)]),
                        .0025, edge, y=y+sign*.013, b=.0012)
        else:
            for along in (.31, .47, .63):
                profile(side + ' angular orange decal',
                        shape([(along-.054, .008), (along+.052, .008),
                               (along+.016, -.004), (along-.076, -.004)]),
                        .002, orange, y=y+sign*.013, b=.0007)
    bolt(side + ' suspension pivot', (pivot_x, y+sign*.016, pivot_z), .010)


def kickstand(c, width, deck_z, deck_depth):
    mount_x, offset_x, offset_y = c['stand']
    mount_y = -width / 2 + .006
    mount_z = deck_z - deck_depth + .004
    mount = Vector((mount_x, mount_y, mount_z))
    folded = offset_y < .01
    foot = Vector((mount_x + offset_x, mount_y - offset_y, mount_z - .019 if folded else .010))
    moving = bpy.data.objects.new('Kickstand', None)
    bpy.context.collection.objects.link(moving)
    moving.parent = groups['Chassis']
    moving['vfKickstandPose'] = 'folded' if folded else 'parked'
    groups['Kickstand'] = moving

    cube('Cast side-stand mounting plate', (mount_x, mount_y+.014, mount_z+.013),
         (.046, .035, .021), edge, b=.004)
    for dx in (-.015, .015):
        bolt('Side-stand mount fastener', (mount_x+dx, mount_y-.006, mount_z+.016), .0035)
    rod('Steel side-stand pivot shaft', mount + Vector((0, -.014, 0)),
        mount + Vector((0, .018, 0)), .010, steel)
    bolt('Kickstand pivot bolt', mount + Vector((0, -.016, 0)), .006)
    hinge = mount.lerp(foot, .14)
    rod('Forged parking leg, tapered', hinge, foot, .0070, edge, 'Kickstand', n=16, r2=.0053)
    rod('Pivoting alloy hinge clevis', mount, hinge, .009, black, 'Kickstand', n=16)
    shoe = cube('Textured parking foot pad', (foot.x, foot.y-.004, foot.z-.003),
                (.030, .025, .010), black, 'Kickstand', .0025)
    if folded:
        shoe.rotation_euler[1] = .09
    for shift in (-.008, 0, .008):
        cube('Parking foot traction rib', (foot.x+shift, foot.y-.004, foot.z+.002),
             (.002, .019, .002), steel, 'Kickstand', .0007)
    anchor = mount + Vector((-.013, -.012, -.005))
    end = mount.lerp(foot, .43) + Vector((-.011, -.002, 0))
    axis = end-anchor
    u = axis.normalized().cross(Vector((0, 1, 0))).normalized()
    v = axis.normalized().cross(u)
    helix = [anchor+axis*(i/56)+.0038*(u*cos(i*pi/4)+v*sin(i*pi/4)) for i in range(57)]
    curve('Parking stand return spring', helix, .0009, steel, 'Kickstand')
    return mount


def cockpit(c, top_x, height, accent):
    kind = c['kind']
    bar = c['bar']
    steering = groups['Steering']
    sweep = {'master': .025, 'g3': .021, 'max': .020, 'ultra': .033, 'g2': .019, 'pro': .018}[kind]
    tube_radius = .0111
    straight_grip_length = .119 if kind in ('master', 'g3') else .111
    cap_y = bar / 2 - .006
    grip_y = cap_y - straight_grip_length / 2
    grip_x = top_x - sweep
    center_z = height - .023

    def tag(first, role):
        for obj in parts[first:]:
            obj['vfCockpit'] = role

    def anchor(suffix, location):
        obj = bpy.data.objects.new('VF_Cockpit_' + suffix, None)
        bpy.context.collection.objects.link(obj)
        obj.parent = steering
        obj.location = location
        obj.empty_display_size = .016

    anchor('Center', (top_x, 0, center_z))
    first = len(parts)
    # Keep the outer stubs straight where the physical rubber sleeves fit.
    curve('Butted swept alloy handlebar',
          [(grip_x, -cap_y, height), (grip_x, -cap_y+straight_grip_length+.009, height),
           (top_x-sweep*.54, -.119, height-.009), (top_x, -.070, center_z),
           (top_x, 0, center_z), (top_x, .070, center_z),
           (top_x-sweep*.54, .119, height-.009),
           (grip_x, cap_y-straight_grip_length-.009, height), (grip_x, cap_y, height)],
          tube_radius, edge, 'Steering')
    tag(first, 'bar')

    for sy, suffix in [(-1, 'A'), (1, 'B')]:
        anchor('Grip'+suffix, (grip_x, sy*grip_y, height))
        anchor('Cable'+suffix, (top_x+.034, sy*.032, height-.190))
        first = len(parts)
        inner_y = cap_y - straight_grip_length
        ergonomic = kind in ('master', 'g3', 'ultra')
        radius = .0167 if kind == 'pro' else .0174
        levels = [(0, .0171), (.06, .0196), (.15, radius), (.65, radius-.0015),
                  (.86, radius+.0004), (.94, .0191), (1, .0185)]
        segments = 36
        vertices = []
        for fraction, width in levels:
            for step in range(segments):
                angle = 2*pi*step/segments
                palm = .0048*sin(angle)**2 * max(0, -cos(angle)) if ergonomic else 0
                vertices.append((grip_x+(width+palm*.63)*cos(angle),
                                 sy*(inner_y+fraction*straight_grip_length),
                                 height+(width+palm)*sin(angle)))
        faces = []
        for row in range(len(levels)-1):
            for step in range(segments):
                nxt = (step+1) % segments
                faces.append((row*segments+step, row*segments+nxt,
                              (row+1)*segments+nxt, (row+1)*segments+step))
        mesh('Contoured molded grip sleeve ' + suffix, vertices, faces, grip, 'Steering', smooth=True)
        if ergonomic:
            for row in range(8):
                y = sy*(inner_y+.021+row*.011)
                for index in range(18):
                    a = (index + (row % 2)*.5)*2*pi/18
                    width = radius + .0001
                    tip = (grip_x+(width+.0015)*cos(a), y, height+(width+.0015)*sin(a))
                    base = (grip_x+(width-.0015)*cos(a), y, height+(width-.0015)*sin(a))
                    rod('Raised grip texture block', base, tip, .0016, grip, 'Steering', n=6, r2=.0013)
        else:
            for j in range(16):
                ring('Molded grip ridge', grip_x, sy*(inner_y+.013+j*.0057), height,
                     radius+.00065, radius-.00180, .00125, grip, 'Steering', n=24)
        rod('Outer bar-end plug', (grip_x, sy*cap_y, height), (grip_x, sy*(bar/2), height),
            .0177, black, 'Steering', n=32, r2=.0147)
        rod('Inner grip lock collar', (grip_x, sy*inner_y, height), (grip_x, sy*(inner_y+.006), height),
            .0182, rubber, 'Steering', n=32)
        tag(first, 'grip'+suffix)

        first = len(parts)
        brake_y = inner_y - .017
        brake_x = top_x - sweep*.89
        cube('Split brake lever perch', (brake_x, sy*brake_y, height-.002),
             (.030, .022, .033), black, 'Steering', .003)
        curve('Forged finger brake lever',
              [(brake_x+.010, sy*brake_y, height+.003),
               (brake_x+.050, sy*(brake_y+.029), height-.002),
               (brake_x+.055, sy*(cap_y-.033), height-.011)],
              .0041, steel, 'Steering')
        rod('Brake lever rounded end', (brake_x+.055, sy*(cap_y-.044), height-.011),
            (brake_x+.055, sy*(cap_y-.030), height-.011), .0051, steel, 'Steering', n=16)
        bolt('Brake lever adjuster pivot', (brake_x+.012, sy*brake_y, height+.017),
             .003, 'Steering', axis='Z')
        control_y = brake_y - .036
        control_x = top_x - sweep*.72
        cube(('Multi-function switch' if sy < 0 else 'Thumb throttle')+' clamp housing',
             (control_x, sy*control_y, height-.007), (.035, .033, .032), black, 'Steering', .003)
        if sy < 0:
            for shift, color in [(-.008, accent), (.009, rubber)]:
                cube('Light and drive-mode buttons', (control_x+shift, sy*control_y, height+.011),
                     (.012, .020, .006), color, 'Steering', .0018)
        else:
            cube('Textured throttle paddle', (control_x-.025, sy*control_y, height-.019),
                 (.028, .024, .009), rubber, 'Steering', .003)
        tag(first, 'control'+suffix)
        curve('Upper brake hose with moving lever end',
              [(brake_x+.010, sy*brake_y, height-.009),
               (top_x+.068, sy*(brake_y*.73), height-.061),
               (top_x+.048, sy*.047, height-.166),
               (top_x+.034, sy*.032, height-.190)],
              .0022, black, 'Steering')['vfCockpit'] = 'cable'
        cube('Fixed handlebar center clamp', (top_x, sy*.024, center_z),
             (.035, .025, .030), black, 'Steering', .004)
        bolt('Bar clamp cap bolt', (top_x, sy*.024, center_z+.017),
             .004, 'Steering', axis='Z')


def build(key,c,entry):
 global groups,parts,black,edge,paint,rubber,grip,silver,steel,orange,gold,red,rotor,lens,screen,white,purple,R
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.preferences.filepaths.save_version=0
 black=mat('Black molded polymer',(.014,.019,.023),.1,.43);edge=mat('Dark anodized aluminum',(.034,.044,.052),.65,.34);steel=mat('Blackened steel',(.075,.09,.10),.7,.35);silver=mat('Brushed stainless fasteners',(.39,.43,.46),.85,.29);rubber=mat('Tire rubber',(.020,.024,.028),0,.79);grip=mat('Molded textured rubber',(.035,.041,.046),0,.71);orange=mat('KuKirin safety orange',(.98,.27,.009),.18,.36);gold=mat('Ausom gold accents',(.92,.46,.027),.5,.30);red=mat('Red optical lens',(.55,.007,.004),.25,.25);rotor=mat('Brake rotor steel',(.27,.30,.33),.9,.32);lens=mat('LED optical lens',(.75,.87,.95),.25,.20);screen=mat('Display glass',(.006,.024,.032),.3,.13);white=mat('Warm gray wordmark',(.63,.69,.72),.2,.38);purple=mat('Purple deck LED',(.18,.008,.95),.1,.25,2)
 kind=c['kind'];ausom=key.startswith('ausom');remodel=key in KUKIRIN_SOURCE
 if remodel:
  entry['source']='https://kukirin-escooter.com/products/'+KUKIRIN_SOURCE[key]
  for material in (black, edge, steel, rubber, grip, orange, red):
   bpy.data.materials.remove(material)
  black=mat('Black PA6 molded polymer',(.008,.010,.012),.02,.46)
  edge=mat('Dark anodized aluminium',(.019,.023,.027),.58,.34)
  steel=mat('Blackened steel',(.045,.050,.054),.71,.31)
  rubber=mat('Road tire rubber',(.013,.014,.015),0,.73)
  grip=mat('Molded rubber grip and standing pad',(.021,.022,.023),0,.66)
  orange=mat('KuKirin orange enamel',(.88,.103,.0035),.14,.34)
  red=mat('Red translucent optical lens',(.47,.006,.003),.16,.22)
 accent=gold if ausom else orange
 if remodel:
  shell_color={'g2':(.089,.103,.110), 'ultra':(.062,.071,.075),
               'master':(.022,.027,.033), 'max':(.031,.034,.036),
               'g3':(.017,.020,.023), 'pro':(.033,.038,.042)}[kind]
  paint=mat('Model powder coat',shell_color,.44,.38)
 else:
  paint=mat('Model powder coat',(.17,.20,.22) if kind in ['g2','ultra','t4','l2'] else ((.027,.034,.039) if not ausom else (.055,.067,.083)),.4,.42)
 if kind=='m4':paint=mat('Silver M4 cast aluminum',(.57,.62,.65),.65,.34)
 # Microscopic scale polymer texture, procedural and editable in native file.
 for m in [rubber,grip]:
  nt=m.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=260;noise.inputs['Detail'].default_value=2;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0005;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
 root=bpy.data.objects.new(entry['name'],None);bpy.context.collection.objects.link(root);root['creator']='Blender';root['accuracy']='Photo-guided visual reconstruction; not measured CAD';root['reference']=entry['image'];root['source']=entry['source'];root['observedGeometry']=c['notes'];root['frontAxis']='+X';root['units']='metres';root['canonicalKey']=key
 groups={};parts=[]
 for n in ['Chassis','Steering','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.parent=root;groups[n]=o
 R=c['r'];front=c['wb']/2;rear=-front;dl=c['dl'];dw=c['dw'];dz=c['dz'];depth=c.get('depth',.077);deckfront=dl/2-.02;deckrear=-dl/2-.02;neck=c['neck'];sx=deckfront+.090;topx=sx-.16;H=c['h'];bar=c['bar'];lower=neck+.10
 tire(front,'FrontWheel',c);tire(rear,'RearWheel',c)
 # Deck shells change topology and cross section by actual chassis family.
 if remodel:
  pts=[(deckrear-.018,dz-depth+.017),(deckrear+.018,dz-depth),
       (deckfront-.008,dz-depth),(deckfront+.023,dz-depth+.020),
       (deckfront+.017,dz-.004),(deckfront-.011,dz+.008),
       (deckrear+.008,dz+.008),(deckrear-.022,dz-.004)]
 elif kind in ['dt2','gosoulpro','k20','gosoul','f1']:
  pts=[(deckrear-.025,dz-.075),(deckfront-.005,dz-.075),(deckfront+.030,dz-.037),(deckfront+.018,dz-.008),(deckfront-.015,dz+.012),(deckrear+.025,dz+.012),(deckrear-.035,dz-.018)]
 else:pts=[(deckrear,dz-.077),(deckfront,dz-.077),(deckfront+.020,dz-.04),(deckfront+.012,dz+.006),(deckrear+.009,dz+.006),(deckrear-.018,dz-.025)]
 profile('Model-specific battery deck shell',pts,dw,paint,b=.006)
 cube('Sealed lower battery tray',((deckfront+deckrear)/2,0,dz-depth+.001),(dl*.96,dw*.92,.014),edge,b=.004)
 cube('Standing pad rubber',((deckfront+deckrear)/2,0,dz+.013),(dl*.94,dw*.92,.009 if remodel else .014),grip,b=.006)
 for yy in range(-5,6):
  y=yy*dw*.075;z=dz+(.0179 if remodel else .021);curve('Fine longitudinal deck traction groove',[(deckrear+.035,y,z),(0,y,z),(deckfront-.035,y,z)],.0007,black)
 for xx in [deckrear+.025,deckfront-.025]:
  for sy in [-1,1]:bolt('Deck countersunk bolt',(xx,sy*dw*.39,dz+(.018 if remodel else .023)),.0033,axis='Z')
 # Top pad family graphics follow the observed X / chevron / perimeter arrangements.
 if not ausom:
  for sy in [-1,1]:
   if remodel and kind=='max':
    curve('G2 Max raised X of deck grip',[(deckrear+.040,sy*dw*.39,dz+.019),
          (deckrear+.150,sy*.007,dz+.019),(.030,sy*.007,dz+.019),
          (deckfront-.047,sy*dw*.34,dz+.019)],.0042,orange)
   elif remodel and kind=='g3':
    curve('G3 Pro deck perimeter rail',[(deckrear+.039,sy*dw*.396,dz+.019),
          (deckfront-.103,sy*dw*.396,dz+.019),(deckfront-.051,0,dz+.019)],.0035,orange)
   elif kind=='pro':
    curve('Pro deck forked orange grip graphic',[(deckrear+.054,sy*dw*.32,dz+.019),
          (-.045,sy*dw*.073,dz+.019),(deckfront-.054,sy*dw*.27,dz+.019)],.0025,orange)
   elif kind=='master':
    curve('Master pinstriped pad inset',[(deckrear+.070,sy*dw*.33,dz+.019),
          (deckrear+.105,sy*dw*.22,dz+.019),(deckfront-.119,sy*dw*.22,dz+.019),
          (deckfront-.059,sy*dw*.38,dz+.019)],.0026,orange)
 elif kind=='f1':
  label('F1 deck end marking','F1 MAX',(deckrear+.11,-dw/2-.002,dz-.035),.018,gold)
 # Flank panels are modeled raised plates and lines, with editable text.
 for sy in [-1,1]:
  yy=sy*(dw/2+.001)
  if kind in ['gosoulpro','k20']:
   profile('LED recessed deck channel',[(deckrear+.035,dz-.057),(deckrear+.09,dz-.028),(deckfront-.12,dz-.028),(deckfront-.07,dz-.047),(deckfront-.14,dz-.049),(deckrear+.10,dz-.046),(deckrear+.06,dz-.065)],.003,black,y=yy,b=.002)
   curve('Purple illuminated deck flank',[(deckrear+.047,yy*1.015,dz-.057),(deckrear+.10,yy*1.015,dz-.036),(deckfront-.14,yy*1.015,dz-.036),(deckfront-.09,yy*1.015,dz-.050)],.003,purple)
  elif kind=='gosoul':
   for i in range(24):
    x=deckrear+.16+i*.016
    if x<deckfront-.02:rod('Diagonal ribbed Gosoul deck side',(x,yy,dz-.060),(x-.03,yy,dz-.006),.0028,steel,n=8)
  elif kind in ['dt2','l2']:
   profile('Faceted deck end panel',[(deckrear,dz-.07),(deckrear+.08,dz-.063),(deckrear+.12,dz-.035),(deckrear+.06,dz+.002),(deckrear-.015,dz-.005)],.004,steel,y=yy)
   profile('Forward deck end panel',[(deckfront-.10,dz-.064),(deckfront+.015,dz-.064),(deckfront+.025,dz-.003),(deckfront-.07,dz+.004),(deckfront-.12,dz-.03)],.004,steel,y=yy)
  elif kind=='m4':
   profile('Silver sculpted side extrusion',[(deckrear,dz-.07),(deckfront,dz-.07),(deckfront,dz+.004),(deckfront-.10,dz-.02),(deckrear+.10,dz-.02)],.007,paint,y=yy)
  elif kind=='g3':
   cube('Removable battery side rail',(-.03,yy,dz-.021),(dl*.72,.009,.042),edge,b=.002)
   for x in [-.22,-.14,-.06,.035,.12,.20]:
    for z in [dz-.039,dz-.005]:bolt('Removable battery rail fastener',(x,yy+sy*.006,z),.0025)
  if remodel:
   curve('Chamfered upper deck seam',[(deckrear+.013,yy,dz-.006),(0,yy,dz-.006),
         (deckfront-.027,yy,dz-.006)],.0014,steel)
   if kind in ['g3','max','master','ultra']:
    profile('Recessed red flank optic',[(deckrear+.029,dz-.029),(deckrear+.069,dz-.029),
            (deckrear+.083,dz-.013),(deckrear+.051,dz-.012)],.004,red,y=yy+sy*.003,b=.002)
   if kind=='master':
    profile('Raised sculpted deck side rib',[(deckrear+.071,dz-.033), (deckrear+.156,dz-.019),
            (deckfront-.117,dz-.019),(deckfront-.057,dz-.026),(deckfront-.137,dz-.031),
            (deckrear+.156,dz-.031)],.003,edge,y=yy+sy*.003,b=.001)
  if sy==-1:
   txt='AUSOM' if ausom else ('G2' if kind=='g2' else entry['name'])
   label('Deck brand marking',txt,(-.10 if kind!='gosoul' else .14,yy*1.015,dz-.034),.018,white if ausom or kind=='master' else accent)
  if kind in ['pro','m4']:
   cube('Amber side reflector',(deckrear+.07,yy*1.025,dz-.030),(.052,.004,.012),gold,b=.004)
  if kind in ['g2','ultra']:
   for i in range(6):
    for j in range(2):
     if (i+j)%2==0:cube('Orange checker deck graphic',(deckrear+.08+i*.017,yy*1.025,dz-.032+j*.011),(.014,.001,.009),orange,b=.0004)
 # Inferred service components are concealed inside hull and separately addressable.
 battery_z=dz-depth*.49 if remodel else dz-.038
 controller_z=battery_z-.002
 cube('Internal battery pack',(-.08,0,battery_z),(dl*.68,dw*.72,depth*.75),black,'BatteryMount',.005)
 for x in [-.22,.09]:cube('Battery retaining strap',(x,0,battery_z),(.019,dw*.75,depth*.83),steel,'BatteryMount',.002)
 cube('Finned motor controller',(deckfront-.065,0,controller_z),(.11,dw*.72,depth*.66),silver,'ControllerMount',.003)
 for i in range(8):cube('Controller heat sink fin',(deckfront-.11+i*.012,0,controller_z+depth*.39),(.004,dw*.70,.009),edge,'ControllerMount',.001)
 # Headstock: two side rails preserve a genuine open triangle.
 if kind in ['g2','ultra']:
  # lower diagonal and upright perimeter leave the central triangular opening
  profile('Open-neck front perimeter',[(deckfront-.015,dz-.055),(deckfront+.034,dz-.05),(sx+.062,neck-.014),(sx+.025,neck+.016),(sx-.007,neck-.012)],.083,paint,b=.005)
  for sy in [-1,1]:rod('Open headstock diagonal brace',(deckfront-.09,sy*.035,dz+.02),(sx+.015,sy*.035,neck-.016),.015,paint)
 elif remodel:
  for sy in (-1,1):
   profile('Hydroformed upper headstock rail',
           [(deckfront-.067,dz+.008),(deckfront+.011,dz+.019),
            (sx+.029,neck-.029),(sx+.011,neck+.015),
            (sx-.027,neck+.007),(deckfront-.069,dz+.035)],
           .024 if kind=='master' else .020,paint,y=sy*.039,b=.005)
   profile('Lower web with cast gusset',
           [(deckfront-.042,dz-.026),(deckfront+.034,dz-.023),
            (sx+.055,neck-.052),(sx+.029,neck-.009),
            (sx+.012,neck-.043),(deckfront-.024,dz+.002)],
           .022,edge,y=sy*.044,b=.005)
   bore=deckfront+.018
   rod('Lateral headstock pivot sleeve',(bore,sy*.034,dz+.009),(bore,sy*.059,dz+.009),
       .016,black,n=28)
   bolt('Head casting pivot fastener',(bore,sy*.060,dz+.009),.0085)
  rod('Machined spindle lower seat',(sx+.015,0,neck-.048),(sx+.015,0,neck+.035),
      .031,edge,'Steering',n=36)
 else:
  for sy in [-1,1]:
   profile('Neck cast side rail',[(deckfront-.025,dz-.025),(deckfront+.041,dz-.016),(sx+.055,neck-.05),(sx+.040,neck+.018),(sx-.018,neck+.028),(sx-.045,neck-.037)],.018 if kind not in ['gosoul','m4'] else .024,edge if kind in ['pro','max','g3','m4'] else paint,y=sy*.044,b=.006)
  rod('Neck front cross headstock',(sx+.015,0,neck-.050),(sx+.015,0,neck+.045),.045,black,'Steering')
  if kind in ['pro','max','g3']:
   for sy in [-1,1]:
    rod('Headstock diagonal machined brace',(deckfront-.045,sy*.043,dz+.024),(sx+.018,sy*.043,neck+.015),.014,edge)
    # sparse raised ribs follow the slotted brace silhouette
    for q in [.3,.5,.7]:
     x=(deckfront-.045)*(1-q)+(sx+.018)*q;z=(dz+.024)*(1-q)+(neck+.015)*q;cube('Neck embossed reinforcing boss',(x,sy*.055,z),(.018,.005,.008),steel,b=.002)
 # Folding collar and locking hardware.
 rod('Lower headset sleeve',(sx+.012,0,neck-.038),(sx+.012,0,neck+.035),.042,black,'Steering')
 for sy in [-1,1]:
  bolt('Neck main pivot',(deckfront+.025,sy*.066,dz+.002),.010)
  profile('Folding hinge cheek',[(sx-.033,neck+.016),(sx+.038,neck+.03),(sx+.015,lower+.015),(sx-.045,lower+.005)],.009,edge,'Steering',y=sy*.043)
  for zz in [neck+.045,neck+.075]:bolt('Stem hinge bolts',(sx,sy*.049,zz),.0045,'Steering')
 levermat=red if kind=='m4' else edge if remodel and kind in ['master','ultra','g2','pro'] else accent
 curve('Quick release lock lever',[(sx+.025,-.053,neck+.043),(sx+.042,-.057,neck+.082),
       (sx+.030,-.057,neck+.142 if kind=='f1' else neck+.108)],.0075,levermat,'Steering')
 if remodel:
  rod('Round hinge tension knob',(sx+.031,-.067,neck+.063),
      (sx+.031,-.076,neck+.063),.010,black,'Steering',n=32)
 # Chassis family suspension structure.
 fy=c.get('tire_half',.044)+.022 if remodel else (.069 if R<.14 else .080)
 if kind in ['m4','k20']:
  for sy in [-1,1]:
   rod('Telescopic fork polished stanchion',(sx+.025,sy*fy,neck-.016),(front-.025,sy*fy,R+.077),.012,silver)
   rod('Telescopic fork lower casting',(front-.025,sy*fy,R+.10),(front,sy*fy,R),.022,black)
   bolt('Front fork axle bolt',(front,sy*(fy+.015),R),.010)
 elif kind=='gosoul':
  for sy in [-1,1]:
   profile('Gosoul angular fork side plate',[(sx+.045,neck-.04),(sx+.09,neck-.13),(front+.026,R-.013),(front-.052,R-.013),(front-.058,R+.10),(sx-.025,neck-.06)],.021,paint,y=sy*fy,b=.006)
   bolt('Gosoul fork front bolt',(front,sy*(fy+.013),R),.009)
 else:
  for sy in [-1,1]:
   for side,x,pivx,pivz in [('Front',front,deckfront+.014,dz+.002),('Rear',rear,deckrear+.01,dz+.004)]:
    if remodel:
     suspended_arm(c,side,pivx,pivz,x,sy*fy)
     continue
    # exact family profile: simple rectangular bars, shaped cast arms, or genuine open arms.
    armmat=orange if kind in ['pro','max','g3'] else paint
    if kind in ['g3','t4']:
     window_arm(side+' open triangular swingarm',(pivx,pivz),(x,R),.023,armmat,sy*fy)
     if kind=='t4':rod('Orange thin suspension insert',(pivx,sy*(fy+.014),pivz-.006),(x+.025*(1 if x<0 else -1),sy*(fy+.014),R+.007),.004,orange,n=8)
    else:
     pts=[(pivx-.027,pivz-.026),(pivx+.027,pivz-.025),(x+.027,R+.010),(x+.018,R-.021),(x-.020,R-.023),(pivx-.027,pivz+.025)]
     # construct a clean capsule-ish linkage polygon by endpoint extrusion.
     d=Vector((x-pivx,R-pivz)).normalized();nn=Vector((-d[1],d[0]));a=Vector((pivx,pivz));bb=Vector((x,R));pts=[tuple(a+nn*.025-d*.020),tuple(bb+nn*.023+d*.012),tuple(bb-nn*.022+d*.018),tuple(a-nn*.027-d*.020)]
     profile(side+' cast swingarm',pts,.023,armmat,y=sy*fy,b=.006)
     if kind in ['master','dt2','l2','f1']:
      mid=(a+bb)/2;profile('Suspension inset casting',[(mid[0]-.025,mid[1]-.008),(mid[0]+.025,mid[1]-.008),(mid[0]+.01,mid[1]+.012)],.002,orange if kind=='master' else edge,y=sy*(fy+.014),b=.002)
     if kind in ['g2','ultra']:
      for i in range(3):cube('Arm orange graphic',(x+(pivx-x)*(.2+i*.15),sy*(fy+.013),R+(pivz-R)*(.2+i*.15)),(.022,.001,.010),orange,b=.001)
    if kind in ['max','pro'] and sy==-1:
     ang=math.atan2(R-pivz,x-pivx)
     if abs(ang)>pi/2:ang-=pi if ang>0 else -pi
     label('Swingarm KuKirin lettering','KuKirin',((x+pivx)/2,sy*(fy+.013),(R+pivz)/2),.010,white,angle=ang)
    bolt(side+' suspension pivot',(pivx,sy*(fy+.016),pivz),.010)
  # Front spring placement varies: Master exposed upright; F1 dual coil; others hidden lean.
  if kind=='f1':
   for sy in [-1,1]:shock('F1 front dual shock',(deckfront+.035,sy*.048,dz+.16),(front-.05,sy*.048,R+.037),.018)
  elif kind=='master':shock('Master exposed front shock',(deckfront+.062,0,dz+.129),(front-.098,0,R+.045),.019,orange)
  elif remodel:
   shock('Adjustable coil over front damper',(deckfront+.060,0,dz+.122),
         (deckfront+.094,0,R+.064),.015,orange if kind in ['g3','max'] else None)
  else:shock('Front suspension spring',(deckfront+.025,0,dz+.10),(front-.08,0,R+.027),.016)
 # Conventional-fork and single-motor platforms still have a separate rear swingarm.
 if kind in ['m4','k20','gosoul']:
  for sy in [-1,1]:
   a=Vector((deckrear+.016,dz+.002));bb=Vector((rear,R));d=(bb-a).normalized();nn=Vector((-d[1],d[0]));pts=[tuple(a+nn*.026-d*.018),tuple(bb+nn*.021+d*.016),tuple(bb-nn*.023+d*.016),tuple(a-nn*.028-d*.018)]
   profile('Rear sculpted swingarm',pts,.024,paint if kind=='m4' else edge,y=sy*fy,b=.005)
   bolt('Rear swingarm pivot',(deckrear+.016,sy*(fy+.017),dz+.002),.010)
   if kind=='m4':cube('M4 rear arm amber reflector',((deckrear+rear)/2,sy*(fy+.014),(dz+R)/2),(.052,.005,.025),gold,b=.004)
   else:
    if sy==-1:label('Rear ShocFree arm marking','SHOCFREE',((deckrear+rear)/2,sy*(fy+.014),(dz+R)/2),.008,white,angle=.22)
 # Rear damper common placement with observed coil colors and visible length.
 if kind=='m4':shock('M4 red rear damper',(deckrear+.020,0,dz+.074),(rear+.095,0,R+.062),.020,red)
 elif kind=='master':shock('Master orange rear shock',(deckrear-.058,0,dz+.092),(rear+.095,0,R+.051),.019,orange)
 elif remodel:
  shock('Rear preload adjustable coilover',(deckrear-.048,0,dz+c['kick']*.81),
        (rear+.079,0,R+.037),.016,orange if kind=='g3' else None)
 else:shock('Rear adjustable shock',(deckrear-.005,0,dz+c['kick']*.70),(rear+.10,0,R+.044),.017)
 # Fender forms follow photographed round, angular or flat silhouettes.
 angular=kind in ['dt2','t4','m4','gosoul','gosoulpro','k20']
 fender_width=c['tire_half']*2+.014 if remodel else (.108 if R<.14 else .12)
 fender('Front model-specific fender',front,R+(.011 if remodel else .020),fender_width,angular,False,remodel)
 fender('Rear model-specific fender',rear,R+(.012 if remodel else .023),
        fender_width+.005,angular or kind=='g3',True,remodel)
 if remodel and (kind in ['master','pro'] or c.get('abe') or c.get('vmp')):
  profile('Rear wheel mud flap with plate bracket',
          [(rear-R*.86,R*1.63),(rear-R*1.05,R*1.22),
           (rear-R*.99,R*1.18),(rear-R*.77,R*1.59)],
          fender_width*.71,black,b=.002)
 if c.get('abe') or c.get('vmp'):
  plate=cube('Vertical regional rear license mount',(rear-R*.88,0,R*1.53),
             (.010,.064,.050),black,b=.003)
  plate.rotation_euler[1]=-.23
  cube('Regional rear reflector',(rear-R*.98,0,R*1.41),(.009,.052,.013),red,b=.002)
 # Raised kickplate with real slots in Pro variants and ribs elsewhere.
 kx=deckrear-.029 if remodel else deckrear-.035;kz=dz+c['kick']
 for sy in [-1,1]:
  rod('Rear kickplate support',(deckrear+.020,sy*.043,dz+.015),(kx-.075,sy*.043,kz),.014,edge)
  if kind in ['pro','max']:
   curve('Slotted kick support upper edge',[(deckrear+.015,sy*.055,dz+.016),(kx-.04,sy*.055,kz-.010),(kx-.115,sy*.055,kz+.02)],.009,paint)
   curve('Slotted kick support lower edge',[(deckrear-.016,sy*.055,dz+.016),(kx-.06,sy*.055,kz-.039),(kx-.12,sy*.055,kz+.002)],.008,paint)
   for t in [.25,.62]:rod('Kick support slot bridge',(kx-.11*t,sy*.055,dz+.045+t*.065),(kx-.11*t+.018,sy*.055,dz+.055+t*.065),.007,paint)
 if remodel:
  plate_end={'max':.091,'master':.086,'g3':.099,'pro':.094,'g2':.105,'ultra':.112}[kind]
  lip={'max':.025,'master':.029,'g3':.018,'pro':.032,'g2':.030,'ultra':.024}[kind]
  profile('Low sculpted rear boot support',
          [(kx+.030,kz-.027),(kx+.028,kz-.008),(kx-plate_end,kz+lip),
           (kx-plate_end-.014,kz+lip-.008),(kx-plate_end+.006,kz+lip-.017)],
          dw*(.52 if kind in ['max','master','pro'] else .58),paint,b=.004)
  for j in range(6):
   x=kx+.014-j*.016
   z=kz-.002+j*.0048
   rod('Recessed rear boot tread rib',(x,-dw*.22,z),(x,dw*.22,z),.0021,grip,n=10)
  cube('Kick support rear tail lens',(kx-plate_end-.006,0,kz+lip-.010),
       (.010,dw*.40,.012),red,b=.003)
 else:
  profile('Raised rear foot plate',[(kx+.040,kz-.028),(kx+.027,kz-.006),(kx-.115,kz+.030),(kx-.133,kz+.013)],dw*.67,paint,b=.005)
  for j in range(5):
   x=kx+.005-j*.022;z=kz+.002+j*.005;rod('Kickpad traction rib',(x,-dw*.27,z),(x,dw*.27,z),.0025,grip,n=10)
 # Steering mast profile: telescopic models retain thinner upper shaft and collar.
 if c['stem']=='telescopic':
  joinz=H-.22;joinx=sx-.16*(joinz-lower)/(H-lower)
  mast_material=paint if remodel else edge
  if c.get('abe'):
   rail=mat('Smoked grey regional mast insert',(.050,.057,.062),.47,.38)
   for sy in [-1,1]:
    profile('Regional smoke-gray stem insert',
            [(sx-.024,lower+.089),(sx+.009,lower+.098),
             (joinx+.018,joinz-.015),(joinx-.019,joinz-.015)],
            .002,rail,'Steering',y=sy*.023,b=.001)
  profile('Lower rectangular telescopic mast',[(sx-.028,lower),(sx+.028,lower+.010),
          (joinx+.022,joinz),(joinx-.022,joinz)],.044 if remodel else .047,
          mast_material,'Steering',b=.004)
  rod('Upper telescoping steering shaft',(joinx,0,joinz-.020),(topx,0,H-.040),.016,edge,'Steering')
  clamp_material=red if kind=='m4' else edge if remodel and kind=='master' else orange
  cube('Telescopic quick clamp',(joinx,0,joinz),(.057,.055,.016),clamp_material,'Steering',.003)
 else:
  profile('Wide tapered model steering mast',[(sx-.030,lower),(sx+.029,lower+.011),(topx+.022,H-.040),(topx-.022,H-.040)],.053 if kind in ['ultra','dt2','f1'] else .047,edge,'Steering',b=.005)
  profile('Inset mast face',[(sx-.023,lower+.065),(sx+.021,lower+.073),(topx+.018,H-.065),(topx-.018,H-.065)],.002,paint,'Steering',y=-.028,b=.001)
 # Native lettering uses model designation and follows physical rake.
 ang=math.atan2(H-lower,-.16);mz=(H+lower)/2;mx=(sx+topx)/2
 text='AUSOM' if ausom else entry['name']
 if kind!='g3':
  label('Stem manufacturer model wordmark',text,(mx,-.031,mz+.06),.024 if not ausom else .018,accent if kind in ['master','ultra'] or ausom else white,'Steering',ang)
 if kind=='g3':
  zl=lower+.099;zu=H-.141;xl=sx-.16*(zl-lower)/(H-.04-lower);xu=sx-.16*(zu-lower)/(H-.04-lower)
  profile('G3 main rectangular orange mast extrusion',
          [(xl-.029,zl),(xl+.027,zl+.004),(xu+.021,zu),(xu-.022,zu)],
          .059,orange,'Steering',b=.003)
  label('G3 dark stem lettering','KuKirin G3 Pro',((xl+xu)/2,-.031,(zl+zu)/2+.015),.023,edge,'Steering',ang)
 if kind in ['t4','l2']:
  for z in [lower+.08,H-.12]:
   x=sx-.16*(z-lower)/(H-lower);bolt('Stem panel fastener',(x,-.033,z),.003,'Steering')
 # Fine routed cables, control hoses and cable spine.
 for sy in [-1,1]:
  if remodel:
   curve('Fixed lower front brake hose',
         [(topx+.034,sy*.032,H-.190),(topx+.039,sy*.033,H-.252),
          (sx+.044,sy*.029,lower+.01),(sx+.044,sy*.033,neck-.017),
          (front-.025,sy*.060,R+.065)],.0022,black,'Steering')
  else:
   curve('Handlebar brake cable loop',[(topx+.035,sy*.19,H-.01),(topx+.09,sy*.11,H-.10),(topx+.055,sy*.055,H-.18),(sx+.044,sy*.035,lower+.01),(front-.025,-.075,R+.065)],.0022,black,'Steering')
 curve('Rear brake routed hose',[(topx+.06,.07,H-.11),(sx-.04,.055,lower),(deckfront,.09,dz-.048),(deckrear,.09,dz-.048),(rear+.025,-.075,R+.06)],.002,black)
 for z in [lower+.12,H-.18]:
  x=sx-.16*(z-lower)/(H-lower);cube('Mast cable clip',(x+.030,.025,z),(.015,.012,.013),black,'Steering',.002)
 # Grip and control assembly. Ausom K20 uses visibly swept swallow bars.
 if remodel:
  cockpit(c,topx,H,accent)
 else:
  sweep=.043 if kind=='k20' else .018
  curve('Swept ergonomic handlebar',[(topx-sweep,-bar/2,H),(topx-sweep*.6,-.19,H+.005),(topx,-.09,H-.024),(topx,0,H-.025),(topx,.09,H-.024),(topx-sweep*.6,.19,H+.005),(topx-sweep,bar/2,H)],.011,edge,'Steering')
  for sy in [-1,1]:
   gy=bar/2;gx=topx-sweep;rod('Textured rubber grip',(gx,sy*(gy-.115),H),(gx,sy*gy,H),.018,grip,'Steering',32)
   for j in range(18):ring('Grip fine molded rib',gx,sy*(gy-.108+j*.006),H,.0187,.017,.0012,grip,'Steering',24)
   rod('Grip protective end cap',(gx,sy*gy,H),(gx,sy*(gy+.005),H),.019,black,'Steering')
   cube('Brake master lever clamp',(topx,sy*(gy-.13),H),(.03,.022,.033),black,'Steering',.003)
   curve('Cast curved brake lever',[(topx+.015,sy*(gy-.14),H+.004),(topx+.053,sy*(gy-.12),H-.006),(topx+.062,sy*(gy-.035),H-.012)],.004,steel,'Steering')
   bolt('Brake lever pivot',(topx+.018,sy*(gy-.13),H+.015),.003,'Steering',axis='Z')
   cube('Handlebar center clamp',(topx,sy*.025,H-.023),(.043,.027,.037),black,'Steering',.004)
  cube('Thumb throttle housing',(topx,bar/2-.17,H),(.036,.037,.031),black,'Steering',.004);cube('Thumb throttle paddle',(topx-.023,bar/2-.17,H-.015),(.03,.024,.008),black,'Steering',.003)
  cube('Left control block',(topx,-bar/2+.17,H+.002),(.034,.034,.038),black,'Steering',.004);cube('Mode control button',(topx,-bar/2+.17,H+.024),(.018,.020,.006),accent,'Steering',.002)
 # Dash is separate from headlight hardware and retains glass, bezel and segments.
 pod_width=.105 if kind=='master' else .081 if kind=='max' else .074 if kind=='pro' else .10
 pod=cube('Central instrument bezel',(topx+.012,0,H+.012),(.071,pod_width,.031),black,'Steering',.008);pod.rotation_euler[1]=-.20
 dash=cube('Instrument display glass',(topx+.008,0,H+.030),(.060,pod_width-.014,.004),screen,'Steering',.003);dash.rotation_euler[1]=-.20
 if not remodel:
  for x in [-.011,0,.011]:cube('Instrument digital segments',(topx+x,-.010,H+.034),(.005,.024,.001),white,'Steering',.0005)
 # Headlight exact placement/type is one of the strongest family differences.
 def headlamp(lx,lz,round=False,twin=False):
  for yy in ([-.024,.024] if twin else [0]):
   if round or twin:
    rod('Round headlight ribbed housing',(lx-.028,yy,lz),(lx+.013,yy,lz),.021 if twin else .025,black,'Steering',32)
    rod('Round headlight clear lens',(lx+.013,yy,lz),(lx+.016,yy,lz),.017 if twin else .021,
        lens if kind!='master' else steel,'Steering',32)
    for q in range(5):cube('Lamp heatsink fin',(lx-.023+q*.006,yy,lz),(.002,.050,.047),black,'Steering',.001)
   else:
    cube('Rectangular LED lamp housing',(lx,yy,lz),(.046,.064,.044),black,'Steering',.004)
    cube('LED optical window',(lx+.024,yy,lz),(.004,.052,.032),lens,'Steering',.003)
    for y in [-.016,0,.016]:cube('Lamp lens divider',(lx+.027,yy+y,lz),(.001,.001,.028),silver,'Steering',.0003)
 if c['lamp']=='console':headlamp(topx+.056,H+.005)
 elif c['lamp']=='high-square':headlamp(sx-.10+.045,H-.21)
 elif c['lamp']=='twin-low':
  if kind=='g3':
   cube('G3 shared twin lamp back plate',(sx+.055,0,neck-.015),(.044,.107,.055),
        black,'Steering',.005)
   for sy in [-1,1]:
    cube('G3 optical cage side rail',(sx+.073,sy*.053,neck-.012),(.025,.009,.045),
         black,'Steering',.002)
  headlamp(sx+.067,neck-.012,True,True)
 elif c['lamp']=='fender':headlamp(front+.005,R*2+.044)
 else:headlamp(sx+.067,neck-.012,c['lamp']=='low-round')
 if kind=='master':
  for yy in [-.008,.008]:
   for zz in [-.008,.008]:
    rod('Individual Master projector optic',(sx+.083,yy,neck-.012+zz),
        (sx+.086,yy,neck-.012+zz),.0063,lens,'Steering',n=24)
 if c.get('abe') or c.get('vmp'):
  for sy in (-1,1):
   rod('Regional front amber reflector',(sx+.026,sy*.051,neck-.054),
       (sx+.026,sy*.054,neck-.054),.015,gold,'Steering',n=28)
 # Stem safety decals and hanging key/clip, seat only where photographed.
 if kind in ['pro','master','g3']:
  z=lower+.10;x=sx-.16*(z-lower)/(H-lower);cube('Yellow warning decal',(x,-.032,z),(.039,.001,.013),gold,'Steering',.0004)
 if c.get('seat'):
  # two open rails and short cross ties make the slotted pedestal genuinely hollow.
  bx=-.17
  for yy in [-.035,.035]:
   for xx in [bx-.022,bx+.022]:rod('Seat pedestal open side rail',(xx,yy,dz+.025),(xx+.015,yy,.60),.008,edge)
   for z in [dz+.035,.39,.46,.53,.59]:rod('Seat pedestal cross tie',(bx-.022,yy,z),(bx+.037,yy,z),.008,edge)
  cube('Seat base mounting plate',(bx,0,dz+.028),(.12,.12,.016),black,b=.004)
  rod('Seat telescopic post',(bx+.015,0,.55),(bx+.015,0,.79),.018,edge)
  rod('Seat upper polished post',(bx+.015,0,.68),(bx+.015,0,.85),.012,silver)
  cube('Seat orange quick clamp',(bx+.015,0,.60),(.067,.054,.018),orange,b=.003)
  for z in [.72,.735,.75,.765]:rod('Seat post bellows',(bx+.015,0,z-.0045),(bx+.015,0,z+.0045),.023,grip,n=24)
  # Tail shoulders square off before tapering into the narrow, lowered nose.
  seat_outline=[(-.136,-.083),(-.092,-.101),(-.046,-.100),(.006,-.069),
                (.071,-.039),(.124,-.033),(.146,-.014),(.145,.014),
                (.124,.033),(.071,.039),(.006,.069),(-.046,.100),
                (-.092,.101),(-.136,.083),(-.145,.048),(-.145,-.048)]
  seat_vertices=[(bx+x*scale,y*scale,.851+height+.071*x) for scale,height in
                 [(.89,-.018),(1,0),(.98,.026),(.90,.036)] for x,y in seat_outline]
  n=len(seat_outline)
  seat_faces=[tuple(reversed(range(n))),tuple(range(n*3,n*4))]
  for j in range(3):
   for i in range(n):
    k=(i+1)%n
    seat_faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
  mesh('Upholstered saddle with dropped nose',seat_vertices,seat_faces,grip,b=.006)
  cube('Seat underside rails',(bx+.015,0,.824),(.17,.068,.022),edge,b=.008)
  for yy in [-.04,.04]:curve('Saddle spring wire',[(bx-.07,yy,.82),(bx-.085,yy,.79),(bx-.055,yy,.78),(bx-.030,yy,.82)],.003,steel)
 # Charging port and deployed stand; stand rests on z=0.
 rod('Charging port cover',(deckfront-.11,-dw/2,dz-.030),(deckfront-.11,-dw/2-.006,dz-.030),.009,black)
 stand_pivot=None
 if remodel:
  stand_pivot=kickstand(c,dw,dz,depth)
 else:
  curve('Deployed side stand',[(-.15,-dw*.48,dz-.067),(-.19,-dw*.70,.05),(-.205,-dw*.73,.007)],.006,steel)
  cube('Stand floor shoe',(-.205,-dw*.73,.007),(.029,.022,.012),black,b=.003)
 # Convert authoring curves, apply fabrication radii, and compact by assembly/material.
 for o in list(parts):
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  if o.type!='MESH':bpy.ops.object.convert(target='MESH')
  for md in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=md.name)
   except RuntimeError:pass
 for parent in groups.values():
  buckets={}
  for o in list(parent.children):
   if o.type=='MESH':buckets.setdefault((o.data.materials[0].name,o.get('vfCockpit','')),[]).append(o)
  for (mn,role),objs in buckets.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in objs:o.select_set(True)
   bpy.context.view_layer.objects.active=objs[0]
   if len(objs)>1:bpy.ops.object.join()
   objs[0].name=parent.name+' | '+mn+(' | '+role if role else '')
 # Bake each consolidated object's transform: rotated-rod/text local AABBs otherwise
 # become loose in Three.js Box3 and report false below-floor bounds.
 for parent in groups.values():
  for o in parent.children:
   if o.type=='MESH':
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Reposition named assembly origins while preserving world transforms.
 assembly_origins=[('FrontWheel',(front,0,R)),('RearWheel',(rear,0,R)),
                   ('BatteryMount',(-.08,0,battery_z)),
                   ('ControllerMount',(deckfront-.065,0,controller_z)),('MotorMount',(rear,0,R))]
 if stand_pivot is not None:
  assembly_origins.append(('Kickstand',stand_pivot))
 for gn,co in assembly_origins:
  bpy.context.view_layer.update();p=groups[gn];ms=[(o,o.matrix_world.copy()) for o in p.children];p.location=co;bpy.context.view_layer.update()
  for o,m in ms:o.matrix_world=m
 bpy.context.view_layer.update()
 model=[o for p in groups.values() for o in p.children if o.type=='MESH'];tri=0
 for o in model:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for p in groups.values():
  p.select_set(True)
  for o in p.children:o.select_set(True)
 export=OUT/(key+'.glb');bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 # Pack only this vehicle's exact reference(s); factory reset prevents cross-asset data buildup.
 for typ,img in [('REFERENCE',entry['image']),('SUPPLEMENTAL',entry.get('supplementalImage'))]:
  if img:
   im=bpy.data.images.load(str(ROOT/'apps/web/public'/img.lstrip('/')));im.pack();o=bpy.data.objects.new(typ+' photo - not CAD',None);bpy.context.collection.objects.link(o);o.empty_display_type='IMAGE';o.data=im;o.location=(0,2,.7);o.rotation_euler=(pi/2,0,0);o.hide_render=True;o.hide_viewport=True
 scene=bpy.context.scene;scene.world=bpy.data.worlds.new('STUDIO world');scene.unit_settings.system='METRIC';scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.25,.25,.25);scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
 gm=mat('STUDIO warm gray',(.74,.76,.78),0,.85);bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));o=bpy.context.object;o.name='STUDIO floor';o.data.materials.append(gm)
 for name,loc,power,size in [('Key',(1,-3,4),460,3),('Fill',(-2,-1,2),220,2.5),('Rim',(1.5,2,3),450,2.5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO '+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.65))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(2.2,-5.2,1.65) if remodel else (2.5,-4.4,2.05));cam=bpy.context.object;cam.name='STUDIO three-quarter camera';cam.rotation_euler=(Vector((0,0,H*.49))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(H+0.28,c['wb']+R*2+.25);scene.camera=cam;scene.render.filepath=str(PROOF/(key+'.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
 # Purge all orphan construction datablocks prior to compressed native save.
 bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(BLENDS/(key+'.blend')),compress=True)
 note=dict(key=key,name=entry['name'],family=c['family'],observed=c['notes'],reference=entry['image'],source=entry['source'],triangles=tri,meshes=len(model),bytes=export.stat().st_size,blendBytes=(BLENDS/(key+'.blend')).stat().st_size,render=f'artifacts/blender/catalog/scooters/{key}.png',limitations='Approximate photographic reconstruction; hidden faces and internal battery/controller inferred. No measured CAD accuracy. Procedural microtexture retained in Blender; GLB has PBR surface parameters.')
 assert tri<160000,(key,tri)
 assert len(model)<70,(key,len(model))
 assert export.stat().st_size<20000000,(key,export.stat().st_size)
 json.dump(note,open(PROOF/(key+'.json'),'w'),indent=2)
 # Reload latest manifest so parent readers and per-asset reruns retain completed entries.
 manifest=json.load(open(MANIFEST))
 for e in manifest:
  if e['key']==key:e.update(source=entry['source'],family=c['family'],variantNote=c['notes']+' Photo-based visual reconstruction; not measured CAD. Hidden/internal surfaces inferred.',triangles=tri,meshes=len(model),bytes=export.stat().st_size)
 MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
 print('SCOOTER_COMPLETE '+json.dumps(note),flush=True)

if __name__=='__main__':
 selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(C)
 for key in selected:
  ent=next(e for e in json.load(open(MANIFEST)) if e['key']==key)
  build(key,C[key],ent)
 print('SCOOTER_BATCH_COMPLETE',len(selected),flush=True)
