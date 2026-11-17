"""Shared geometry primitives adapted from the accepted surron_lbx.py reconstruction.
No external dependencies. Blender 4.5 LTS. +X front, +Z up, metres.
"""
import bpy, math
from mathutils import Vector
from math import sin, cos, pi

def mat(name, color, metallic=0, rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=rough
    return m

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

def project_body_livery(root,family,bw,seat):
    """Conform printed graphics to the molded shroud surface along the side axis."""
    if family not in {'ultra','storm','hyper','sigma','delta','omega','eride4'}:return 0
    eligible={'Model accent'} if family in {'ultra','storm','hyper'} else {'Printed white graphics'}
    body=[o for o in root.children_recursive if o.type=='MESH' and o.parent and o.parent.name=='Bodywork']
    decals=[o for o in body if o.data.materials and o.data.materials[0].name in eligible]
    targets=[o for o in body if o not in decals and o.data.materials and o.data.materials[0].name not in {'Grained charcoal saddle','Headlamp lens','Red lamp and accents'}]
    count=0
    for graphic in decals:
        # A broad decal needs interior samples across the shroud's crease; projecting
        # only the outline corners leaves its middle buried in the molded panel.
        if not graphic.data.get('conform_grid'):
            import bmesh
            bm=bmesh.new();bm.from_mesh(graphic.data)
            bmesh.ops.triangulate(bm,faces=list(bm.faces))
            selected=set()
            for face in bm.faces:
                center=graphic.matrix_world @ face.calc_center_median()
                if abs(center.y)>bw and -.66<center.x<.28 and seat*.70<center.z<seat*1.01:
                    selected.update(e for e in face.edges if e.calc_length()>.018)
            if selected:bmesh.ops.subdivide_edges(bm,edges=list(selected),cuts=5,use_grid_fill=True)
            bm.to_mesh(graphic.data);bm.free();graphic.data['conform_grid']=True
        inv=graphic.matrix_world.inverted()
        for vertex in graphic.data.vertices:
            p=graphic.matrix_world @ vertex.co
            # Principal side livery only; keep front/rear fenders and small lamps intact.
            if abs(p.y)<bw or p.x<-.66 or p.x>.28 or p.z<seat*.70 or p.z>seat*1.01:continue
            sign=1 if p.y>0 else -1
            origin=Vector((p.x,sign*.8,p.z));direction=Vector((0,-sign,0));hits=[]
            for surface in targets:
                matrix=surface.matrix_world;local=matrix.inverted()
                hit,point,normal,index=surface.ray_cast(local @ origin,(local.to_3x3() @ direction).normalized())
                if hit:
                    wp=matrix @ point
                    if wp.y*sign>bw*.65:hits.append(wp.y*sign)
            if hits:
                vertex.co=inv @ Vector((p.x,sign*(max(hits)+.0015),p.z));count+=1
        graphic.data.update()
    return count
