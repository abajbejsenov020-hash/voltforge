import bpy,bmesh,math
from mathutils import Vector,Matrix
from math import sin,cos,pi
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
