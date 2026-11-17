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
'kukirin-g2-max':dict(family='G2 Max single motor',kind='max',wb=1.01,r=.130,dl=.59,dw=.215,dz=.255,h=1.27,bar=.64,orange=True,dual=False,tread='block',neck=.485,lamp='low-round',stem='telescopic',kick=.115,notes='Solid orange swingarms, open front wheel, rear hub motor; long telescopic stem and low round headlight.'),
'kukirin-g2-master':dict(family='G2 Master dual motor',kind='master',wb=1.04,r=.132,dl=.63,dw=.238,dz=.273,h=1.29,bar=.68,dual=True,tread='block',neck=.50,lamp='low-square',stem='telescopic',kick=.115,notes='Sculpted black dual-sided arms with amber triangular insets; exposed orange front/rear springs and dual hub motors.'),
'kukirin-g2':dict(family='G2 open-neck chassis',kind='g2',wb=.94,r=.125,dl=.56,dw=.215,dz=.255,h=1.22,bar=.61,dual=False,tread='block',neck=.47,lamp='console',stem='square',kick=.105,notes='Gray open triangular headstock, compact deck, checkerboard gray swingarms and spoked front wheel.'),
'kukirin-g4-ultra':dict(family='G4 Ultra dual motor',kind='ultra',wb=1.10,r=.152,dl=.66,dw=.27,dz=.302,h=1.36,bar=.72,dual=True,tread='street',neck=.55,lamp='console',stem='square',kick=.12,notes='Larger broad deck and 12-inch-class road tires, two enclosed hub motors; gray open neck, geometric orange arm/stem graphics.'),
'kukirin-m4-max':dict(family='M4 Max telescopic fork',kind='m4',wb=1.02,r=.130,dl=.61,dw=.225,dz=.262,h=1.27,bar=.65,dual=False,tread='block',neck=.46,lamp='low-square',stem='telescopic',kick=.105,notes='Silver sculpted deck extrusion, conventional twin telescopic front fork, red rear damper and red stem clamp.'),
'kukirin-t4':dict(family='T4 long low deck',kind='t4',wb=1.06,r=.128,dl=.65,dw=.22,dz=.247,h=1.23,bar=.64,dual=False,tread='block',neck=.46,lamp='console',stem='square',kick=.09,notes='Low long sculpted deck, gray triangular windowed arms, orange thin arm insets; short angular fenders.'),
'kukirin-g2-pro-abe':dict(family='G2 Pro regional',kind='pro',wb=.94,r=.118,dl=.55,dw=.205,dz=.242,h=1.19,bar=.60,dual=False,tread='block',neck=.45,lamp='low-square',stem='telescopic',kick=.14,abe=True,notes='Seatless ABE reference: amber flank reflector, upright license bracket and square road headlight.'),
'kukirin-g3-pro':dict(family='G3 Pro removable battery chassis',kind='g3',wb=1.08,r=.140,dl=.67,dw=.255,dz=.292,h=1.33,bar=.69,dual=True,tread='block',neck=.53,lamp='low-square',stem='square',kick=.12,notes='Orange open triangular suspension arms, exposed removable battery hatch/bolted side rails, broad orange front stem panel and dual motors.'),
'kukirin-g2-pro-vmp':dict(family='G2 Pro regional',kind='pro',wb=.94,r=.118,dl=.55,dw=.205,dz=.242,h=1.19,bar=.60,dual=False,tread='block',neck=.45,lamp='low-square',stem='telescopic',kick=.14,vmp=True,notes='Seatless VMP reference: open-slot rear kickplate, no seat mount, amber flank reflector and square headlight. Hidden regional differences not invented.'),
'kukirin-g2-pro':dict(family='G2 Pro seated',kind='pro',wb=.94,r=.118,dl=.55,dw=.205,dz=.242,h=1.19,bar=.60,dual=False,tread='block',neck=.45,lamp='low-round',stem='telescopic',kick=.14,seat=True,notes='Photographed seated configuration: tall slotted seat pedestal, telescopic sprung post, orange quick clamp and black saddle.'),
'ausom-dt2-pro':dict(family='Ausom DT2 Pro',kind='dt2',wb=1.08,r=.145,dl=.67,dw=.265,dz=.295,h=1.35,bar=.70,dual=True,tread='street',neck=.54,lamp='console',stem='square',kick=.12,notes='Wide angular faceted deck, long swept neck, dark cast suspension arms, rectangular clipped fenders and two hub motors.'),
'ausom-l2-max-dual':dict(family='Ausom L2 Max',kind='l2',wb=1.03,r=.132,dl=.64,dw=.23,dz=.266,h=1.30,bar=.68,dual=True,tread='street',neck=.50,lamp='fender',stem='square',kick=.105,notes='Slimmer deep gray deck with pointed side caps, angular shallow-V arms, two hub motors, front fender light and slotted stem panel.'),
'ausom-gosoul-2-pro-dual-motor':dict(family='Ausom Gosoul 2 Pro ShocFree',kind='gosoulpro',wb=1.04,r=.136,dl=.63,dw=.25,dz=.273,h=1.31,bar=.68,dual=True,tread='block',neck=.49,lamp='high-square',stem='square',kick=.105,notes='ShocFree leading swingarm front suspension, dual black hub motors, faceted wide deck and purple illuminated flank strip.'),
'ausom-k20-pro-dual-motor':dict(family='Ausom K20 / Laluz 2 Pro',kind='k20',wb=1.015,r=.133,dl=.62,dw=.24,dz=.268,h=1.29,bar=.68,dual=True,tread='block',neck=.46,lamp='high-square',stem='square',kick=.10,notes='Conventional telescopic front fork, gold rim stripes, purple deck LED strip and rear adjustable spring; swallow handlebar.'),
'ausom-laluz-2-pro-dual-motor':dict(family='Ausom K20 / Laluz 2 Pro',kind='k20',wb=1.015,r=.133,dl=.62,dw=.24,dz=.268,h=1.29,bar=.68,dual=True,tread='block',neck=.46,lamp='high-square',stem='square',kick=.10,notes='Manufacturer-confirmed alias of K20 Pro (Laluz 2 Pro), intentionally same physical geometry; full-size primary reference replaces corrupted thumbnail.'),
'ausom-f1-max':dict(family='Ausom F1 Max dual spring',kind='f1',wb=1.10,r=.142,dl=.67,dw=.26,dz=.29,h=1.34,bar=.72,dual=True,tread='block',neck=.49,lamp='twin-low',stem='square',kick=.13,notes='Two exposed front coil dampers, sculpted carbon-pattern-looking arms, ribbed long deck, twin round low headlamps and tall gold fold lever; manufacturer clean photo supplements action reference.'),
'ausom-gosoul-2':dict(family='Ausom Gosoul 2 single motor',kind='gosoul',wb=1.00,r=.132,dl=.62,dw=.24,dz=.265,h=1.29,bar=.66,dual=False,tread='street',neck=.47,lamp='high-square',stem='square',kick=.105,notes='Single rear hub motor, open-spoked front wheel, solid angular fork side plates and diagonal ribbed deck flank; no purple strip.'),
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

def fender(name,x,r,w,angular=False,rear=False):
 if angular:
  # Real faceted raised canopy: flat top and sloping quarter panels.
  pts=[(x-r*.86,R+r*.66),(x-r*.57,R+r*1.02),(x+r*.42,R+r*1.04),(x+r*.91,R+r*.62),(x+r*.83,R+r*.56),(x+r*.37,R+r*.96),(x-r*.53,R+r*.95),(x-r*.80,R+r*.60)]
  profile(name,pts,w,black,b=.002)
 else:
  v=[];f=[];n=38;nw=6
  start=(-.09 if rear else .23)*pi;end=(.89 if rear else .97)*pi
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
  profile('Rear descending license and spray flap',[(x-r*.88,R+r*.72),(x-r*1.05,R+r*.20),(x-r*.98,R+r*.19),(x-r*.79,R+r*.73)],w*.73,black,b=.002)
  cube('Rear red tail optical lens',(x-r*.89,0,R+r*.72),(.009,w*.67,.024),red,b=.002)

def tire(x,parent,c):
 rr=c['r'];wide=.044 if rr<.14 else .052;na=192;nb=28;v=[];f=[]
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


def build(key,c,entry):
 global groups,parts,black,edge,paint,rubber,grip,silver,steel,orange,gold,red,rotor,lens,screen,white,purple,R
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.preferences.filepaths.save_version=0
 black=mat('Black molded polymer',(.014,.019,.023),.1,.43);edge=mat('Dark anodized aluminum',(.034,.044,.052),.65,.34);steel=mat('Blackened steel',(.075,.09,.10),.7,.35);silver=mat('Brushed stainless fasteners',(.39,.43,.46),.85,.29);rubber=mat('Tire rubber',(.020,.024,.028),0,.79);grip=mat('Molded textured rubber',(.035,.041,.046),0,.71);orange=mat('KuKirin safety orange',(.98,.27,.009),.18,.36);gold=mat('Ausom gold accents',(.92,.46,.027),.5,.30);red=mat('Red optical lens',(.55,.007,.004),.25,.25);rotor=mat('Brake rotor steel',(.27,.30,.33),.9,.32);lens=mat('LED optical lens',(.75,.87,.95),.25,.20);screen=mat('Display glass',(.006,.024,.032),.3,.13);white=mat('Warm gray wordmark',(.63,.69,.72),.2,.38);purple=mat('Purple deck LED',(.18,.008,.95),.1,.25,2)
 kind=c['kind'];ausom=key.startswith('ausom');accent=gold if ausom else orange
 paint=mat('Model powder coat',(.17,.20,.22) if kind in ['g2','ultra','t4','l2'] else ((.027,.034,.039) if not ausom else (.055,.067,.083)),.4,.42)
 if kind=='m4':paint=mat('Silver M4 cast aluminum',(.57,.62,.65),.65,.34)
 # Microscopic scale polymer texture, procedural and editable in native file.
 for m in [rubber,grip]:
  nt=m.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=260;noise.inputs['Detail'].default_value=2;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0005;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
 root=bpy.data.objects.new(entry['name'],None);bpy.context.collection.objects.link(root);root['creator']='Blender';root['accuracy']='Photo-guided visual reconstruction; not measured CAD';root['reference']=entry['image'];root['source']=entry['source'];root['observedGeometry']=c['notes'];root['frontAxis']='+X';root['units']='metres';root['canonicalKey']=key
 groups={};parts=[]
 for n in ['Chassis','Steering','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.parent=root;groups[n]=o
 R=c['r'];front=c['wb']/2;rear=-front;dl=c['dl'];dw=c['dw'];dz=c['dz'];deckfront=dl/2-.02;deckrear=-dl/2-.02;neck=c['neck'];sx=deckfront+.090;topx=sx-.16;H=c['h'];bar=c['bar'];lower=neck+.10
 tire(front,'FrontWheel',c);tire(rear,'RearWheel',c)
 # Deck shells change topology and cross section by actual chassis family.
 if kind in ['dt2','gosoulpro','k20','gosoul','f1']:
  pts=[(deckrear-.025,dz-.075),(deckfront-.005,dz-.075),(deckfront+.030,dz-.037),(deckfront+.018,dz-.008),(deckfront-.015,dz+.012),(deckrear+.025,dz+.012),(deckrear-.035,dz-.018)]
 else:pts=[(deckrear,dz-.077),(deckfront,dz-.077),(deckfront+.020,dz-.04),(deckfront+.012,dz+.006),(deckrear+.009,dz+.006),(deckrear-.018,dz-.025)]
 profile('Model-specific battery deck shell',pts,dw,paint,b=.006)
 cube('Sealed lower battery tray',((deckfront+deckrear)/2,0,dz-.076),(dl*.96,dw*.92,.014),edge,b=.004)
 cube('Standing pad rubber',((deckfront+deckrear)/2,0,dz+.013),(dl*.94,dw*.92,.014),grip,b=.006)
 for yy in range(-5,6):
  y=yy*dw*.075;curve('Fine longitudinal deck traction groove',[(deckrear+.035,y,dz+.021),(0,y,dz+.021),(deckfront-.035,y,dz+.021)],.0007,black)
 for xx in [deckrear+.025,deckfront-.025]:
  for sy in [-1,1]:bolt('Deck countersunk bolt',(xx,sy*dw*.39,dz+.023),.0033,axis='Z')
 # Top pad family graphics follow the observed X / chevron / perimeter arrangements.
 if not ausom:
  for sy in [-1,1]:
   if kind in ['max','pro','g3']:
    curve('Orange deck angular graphic',[(deckrear+.055,sy*dw*.37,dz+.022),(-.045,sy*dw*.12,dz+.022),(deckfront-.055,sy*dw*.34,dz+.022)],.002,orange)
   elif kind=='master':
    curve('Master elongated deck stripe',[(deckrear+.07,sy*dw*.31,dz+.022),(deckfront-.09,sy*dw*.18,dz+.022),(deckfront-.12,sy*dw*.27,dz+.022)],.002,orange)
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
   cube('Removable battery side rail',(-.03,yy,dz-.035),(dl*.72,.009,.05),edge,b=.002)
   for x in [-.26,-.16,-.06,.04,.14,.24]:
    for z in [dz-.058,dz-.012]:bolt('Removable battery rail fastener',(x,yy*1.03,z),.0025)
  if sy==-1:
   txt='AUSOM' if ausom else ('G2' if kind=='g2' else entry['name'])
   label('Deck brand marking',txt,(-.10 if kind!='gosoul' else .14,yy*1.015,dz-.034),.018,white if ausom or kind=='master' else accent)
  if kind in ['pro','max','m4']:
   cube('Amber side reflector',(deckrear+.07,yy*1.025,dz-.030),(.052,.004,.016),gold,b=.004)
  if kind in ['g2','ultra']:
   for i in range(6):
    for j in range(2):
     if (i+j)%2==0:cube('Orange checker deck graphic',(deckrear+.08+i*.017,yy*1.025,dz-.050+j*.016),(.014,.001,.012),orange,b=.0004)
 # Inferred service components are concealed inside hull and separately addressable.
 cube('Internal battery pack',(-.08,0,dz-.038),(dl*.68,dw*.72,.058),black,'BatteryMount',.005)
 for x in [-.22,.09]:cube('Battery retaining strap',(x,0,dz-.038),(.019,dw*.75,.063),steel,'BatteryMount',.002)
 cube('Finned motor controller',(deckfront-.065,0,dz-.040),(.11,dw*.72,.051),silver,'ControllerMount',.003)
 for i in range(8):cube('Controller heat sink fin',(deckfront-.11+i*.012,0,dz-.012),(.004,dw*.70,.009),edge,'ControllerMount',.001)
 # Headstock: two side rails preserve a genuine open triangle.
 if kind in ['g2','ultra']:
  points=[(deckfront-.015,dz-.055),(deckfront+.034,dz-.05),(sx+.062,neck-.014),(sx+.038,neck+.025),(sx-.018,neck+.025),(deckfront-.10,dz+.045)]
  # lower diagonal and upright perimeter leave the central triangular opening
  profile('Open-neck front perimeter',[(deckfront-.015,dz-.055),(deckfront+.034,dz-.05),(sx+.062,neck-.014),(sx+.025,neck+.016),(sx-.007,neck-.012)],.083,paint,b=.005)
  for sy in [-1,1]:rod('Open headstock diagonal brace',(deckfront-.09,sy*.035,dz+.02),(sx+.015,sy*.035,neck-.016),.015,paint)
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
 levermat=red if kind=='m4' else accent
 curve('Quick release lock lever',[(sx+.025,-.053,neck+.043),(sx+.049,-.057,neck+.10),(sx+.038,-.057,neck+.142 if kind=='f1' else neck+.12)],.008,levermat,'Steering')
 # Chassis family suspension structure.
 fy=.069 if R<.14 else .080
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
  elif kind=='master':shock('Master exposed front shock',(deckfront+.025,0,dz+.15),(front-.095,0,R+.040),.018,orange)
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
 elif kind=='master':shock('Master orange rear shock',(deckrear-.005,0,dz+.139),(rear+.095,0,R+.040),.018,orange)
 else:shock('Rear adjustable shock',(deckrear-.005,0,dz+c['kick']*.70),(rear+.10,0,R+.044),.017)
 # Fender forms follow photographed round, angular or flat silhouettes.
 angular=kind in ['dt2','t4','m4','gosoul','gosoulpro','k20']
 fender('Front model-specific fender',front,R+.020,.108 if R<.14 else .12,angular,False)
 fender('Rear model-specific fender',rear,R+.023,.113 if R<.14 else .125,angular or kind=='g3',True)
 # Raised kickplate with real slots in Pro variants and ribs elsewhere.
 kx=deckrear-.035;kz=dz+c['kick']
 for sy in [-1,1]:
  rod('Rear kickplate support',(deckrear+.020,sy*.043,dz+.015),(kx-.075,sy*.043,kz),.014,edge)
  if kind in ['pro','max']:
   curve('Slotted kick support upper edge',[(deckrear+.015,sy*.055,dz+.016),(kx-.04,sy*.055,kz-.010),(kx-.115,sy*.055,kz+.02)],.009,paint)
   curve('Slotted kick support lower edge',[(deckrear-.016,sy*.055,dz+.016),(kx-.06,sy*.055,kz-.039),(kx-.12,sy*.055,kz+.002)],.008,paint)
   for t in [.25,.62]:rod('Kick support slot bridge',(kx-.11*t,sy*.055,dz+.045+t*.065),(kx-.11*t+.018,sy*.055,dz+.055+t*.065),.007,paint)
 profile('Raised rear foot plate',[(kx+.040,kz-.028),(kx+.027,kz-.006),(kx-.115,kz+.030),(kx-.133,kz+.013)],dw*.67,paint,b=.005)
 for j in range(5):
  x=kx+.005-j*.022;z=kz+.002+j*.005;rod('Kickpad traction rib',(x,-dw*.27,z),(x,dw*.27,z),.0025,grip,n=10)
 # Steering mast profile: telescopic models retain thinner upper shaft and collar.
 if c['stem']=='telescopic':
  joinz=H-.22;joinx=sx-.16*(joinz-lower)/(H-lower)
  profile('Lower rectangular telescopic mast',[(sx-.033,lower),(sx+.032,lower+.010),(joinx+.026,joinz),(joinx-.026,joinz)],.047,edge,'Steering',b=.004)
  rod('Upper telescoping steering shaft',(joinx,0,joinz-.020),(topx,0,H-.040),.016,edge,'Steering')
  cube('Telescopic quick clamp',(joinx,0,joinz),(.063,.061,.017),red if kind=='m4' else orange,'Steering',.003)
 else:
  profile('Wide tapered model steering mast',[(sx-.036,lower),(sx+.032,lower+.011),(topx+.025,H-.040),(topx-.025,H-.040)],.055 if kind in ['ultra','dt2','f1'] else .047,edge,'Steering',b=.005)
  profile('Inset mast face',[(sx-.024,lower+.065),(sx+.021,lower+.073),(topx+.018,H-.065),(topx-.018,H-.065)],.002,paint,'Steering',y=-.029,b=.001)
 # Native lettering uses model designation and follows physical rake.
 ang=math.atan2(H-lower,-.16);mz=(H+lower)/2;mx=(sx+topx)/2
 text='AUSOM' if ausom else entry['name']
 label('Stem manufacturer model wordmark',text,(mx,-.031,mz+.06),.024 if not ausom else .018,accent if kind in ['master','ultra','g3'] or ausom else white,'Steering',ang)
 if kind=='g3':
  zl=lower+.14;zu=H-.16;xl=sx-.16*(zl-lower)/(H-.04-lower);xu=sx-.16*(zu-lower)/(H-.04-lower)
  profile('G3 broad orange stem face',[(xl-.021,zl),(xl+.021,zl),(xu+.019,zu),(xu-.019,zu)],.0015,orange,'Steering',y=-.0295,b=.001)
  label('G3 dark stem lettering','KuKirin G3 Pro',(mx,-.033,mz+.09),.023,edge,'Steering',ang)
 if kind in ['t4','l2']:
  for z in [lower+.08,H-.12]:
   x=sx-.16*(z-lower)/(H-lower);bolt('Stem panel fastener',(x,-.033,z),.003,'Steering')
 # Fine routed cables, control hoses and cable spine.
 for sy in [-1,1]:
  curve('Handlebar brake cable loop',[(topx+.035,sy*.19,H-.01),(topx+.09,sy*.11,H-.10),(topx+.055,sy*.055,H-.18),(sx+.044,sy*.035,lower+.01),(front-.025,-.075,R+.065)],.0022,black,'Steering')
 curve('Rear brake routed hose',[(topx+.06,.07,H-.11),(sx-.04,.055,lower),(deckfront,.09,dz-.048),(deckrear,.09,dz-.048),(rear+.025,-.075,R+.06)],.002,black)
 for z in [lower+.12,H-.18]:
  x=sx-.16*(z-lower)/(H-lower);cube('Mast cable clip',(x+.030,.025,z),(.015,.012,.013),black,'Steering',.002)
 # Grip and control assembly. Ausom K20 uses visibly swept swallow bars.
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
 pod=cube('Central instrument bezel',(topx+.012,0,H+.012),(.071,.10,.031),black,'Steering',.007);pod.rotation_euler[1]=-.20
 dash=cube('Instrument display glass',(topx+.008,0,H+.030),(.060,.086,.004),screen,'Steering',.003);dash.rotation_euler[1]=-.20
 for x in [-.011,0,.011]:cube('Instrument digital segments',(topx+x,-.010,H+.034),(.005,.024,.001),white,'Steering',.0005)
 # Headlight exact placement/type is one of the strongest family differences.
 def headlamp(lx,lz,round=False,twin=False):
  for yy in ([-.024,.024] if twin else [0]):
   if round or twin:
    rod('Round headlight ribbed housing',(lx-.028,yy,lz),(lx+.013,yy,lz),.021 if twin else .025,black,'Steering',32)
    rod('Round headlight clear lens',(lx+.013,yy,lz),(lx+.016,yy,lz),.017 if twin else .021,lens,'Steering',32)
    for q in range(5):cube('Lamp heatsink fin',(lx-.023+q*.006,yy,lz),(.002,.050,.047),black,'Steering',.001)
   else:
    cube('Rectangular LED lamp housing',(lx,yy,lz),(.046,.064,.044),black,'Steering',.004)
    cube('LED optical window',(lx+.024,yy,lz),(.004,.052,.032),lens,'Steering',.003)
    for y in [-.016,0,.016]:cube('Lamp lens divider',(lx+.027,yy+y,lz),(.001,.001,.028),silver,'Steering',.0003)
 if c['lamp']=='console':headlamp(topx+.056,H+.005)
 elif c['lamp']=='high-square':headlamp(sx-.10+.045,H-.21)
 elif c['lamp']=='twin-low':headlamp(sx+.067,neck-.012,True,True)
 elif c['lamp']=='fender':headlamp(front+.005,R*2+.044)
 else:headlamp(sx+.067,neck-.012,c['lamp']=='low-round')
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
  # Soft saddle, front nose narrower and rear shoulders wider.
  bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,location=(bx-.008,0,.866));o=bpy.context.object;o.scale=(.148,.105,.044);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,'Padded shaped black saddle',grip,smooth=True)
  cube('Seat underside rails',(bx+.015,0,.824),(.17,.068,.022),edge,b=.008)
  for yy in [-.04,.04]:curve('Saddle spring wire',[(bx-.07,yy,.82),(bx-.085,yy,.79),(bx-.055,yy,.78),(bx-.030,yy,.82)],.003,steel)
 # Charging port and deployed stand; stand rests on z=0.
 rod('Charging port cover',(deckfront-.11,-dw/2,dz-.030),(deckfront-.11,-dw/2-.006,dz-.030),.009,black)
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
   if o.type=='MESH':buckets.setdefault(o.data.materials[0].name,[]).append(o)
  for mn,objs in buckets.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in objs:o.select_set(True)
   bpy.context.view_layer.objects.active=objs[0]
   if len(objs)>1:bpy.ops.object.join()
   objs[0].name=parent.name+' | '+mn
 # Bake each consolidated object's transform: rotated-rod/text local AABBs otherwise
 # become loose in Three.js Box3 and report false below-floor bounds.
 for parent in groups.values():
  for o in parent.children:
   if o.type=='MESH':
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Reposition named assembly origins while preserving world transforms.
 for gn,co in [('FrontWheel',(front,0,R)),('RearWheel',(rear,0,R)),('BatteryMount',(-.08,0,dz-.038)),('ControllerMount',(deckfront-.065,0,dz-.04)),('MotorMount',(rear,0,R))]:
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
 bpy.ops.object.camera_add(location=(2.5,-4.4,2.05));cam=bpy.context.object;cam.name='STUDIO three-quarter camera';cam.rotation_euler=(Vector((0,0,H*.49))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(H+0.28,c['wb']+R*2+.25);scene.camera=cam;scene.render.filepath=str(PROOF/(key+'.png'));bpy.ops.render.render(write_still=True)
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
  if e['key']==key:e.update(family=c['family'],variantNote=c['notes']+' Photo-based visual reconstruction; not measured CAD. Hidden/internal surfaces inferred.',triangles=tri,meshes=len(model),bytes=export.stat().st_size)
 json.dump(manifest,open(MANIFEST,'w'),indent=2)
 print('SCOOTER_COMPLETE '+json.dumps(note),flush=True)

if __name__=='__main__':
 selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(C)
 for key in selected:
  ent=next(e for e in json.load(open(MANIFEST)) if e['key']==key)
  build(key,C[key],ent)
 print('SCOOTER_BATCH_COMPLETE',len(selected),flush=True)
