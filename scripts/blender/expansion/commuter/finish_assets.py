"""Last reference-driven native geometry/material pass; never touches original catalog assets."""
import bpy,bmesh,json,math,sys
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'artifacts/blender/expansion/commuter';rows=json.load(open(O/'selected.json'));args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];rows=[e for e in rows if not args or e['key'] in args]
def cylinder(name,x,y,z,r,width,material,parent):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=width,location=(x,y,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=name;o.parent=parent;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);return o

def panel(name,points,width,material,parent):
 n=len(points);v=[(x,y,z) for y in [-width/2,width/2] for x,z in points];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];d=bpy.data.meshes.new(name);d.from_pydata(v,[],faces);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(material);md=o.modifiers.new('Molded edge radius','BEVEL');md.width=.006;md.segments=3;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=md.name);o.select_set(False);return o

def descendants(o):
 out=[]
 for ch in o.children:out.append(ch);out.extend(descendants(ch))
 return out
for e in rows:
 key=e['key'];name=e['name'];f=O/(key+'.json');note=json.load(open(f))
 if note.get('geometryReview'):
  print('Finish already authored in model generator:',key,flush=True)
  continue
 c=note['parameters'];bpy.ops.wm.open_mainfile(filepath=str(R/note['nativeSource']));root=bpy.data.objects[name];gr={n:bpy.data.objects[n] for n in ['Chassis','Steering','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']};paint=bpy.data.materials['Model powder coat'];black=bpy.data.materials['Black molded polymer'];accent=bpy.data.materials['Model accents'];changes=[]
 # Real scooters use dark anodized cast wheels, not bright chrome toy-like trim.
 for matname,col,metal,rough in [('Silver machining',(.065,.077,.087),.65,.40),('Steel',(.028,.034,.039),.65,.45),('Black molded polymer',(.007,.009,.012),.08,.52),('Textured grip rubber',(.009,.011,.013),0,.79)]:
  m=bpy.data.materials.get(matname)
  if m:
   m.diffuse_color=(*col,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 paint.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.08;paint.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.55
 accent.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0;accent.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.55
 wb=c['wb'];r=c['r'];dz=c['dz'];dl=c['dl'];wide=c['wide'];front=wb/2;rear=-front;sx=front-.09;tx=sx-.15;lo=dz+.18
 if name in ['Segway Ninebot ES1','Segway Ninebot ES2','Segway Ninebot ES4']:
  # ES1/ES2 store battery inside the round stem. Only ES4 has one external pack.
  for o in list(gr['BatteryMount'].children):
   if o.type=='MESH' and any(m and m.name=='Model powder coat' for m in o.data.materials):bpy.data.objects.remove(o,do_unlink=True)
  changes.append('Removed inferred external pack; ES4 keeps its single documented auxiliary battery')
 if name.startswith('Segway Ninebot Max G30') or name=='Segway Ninebot Max G2':
  cylinder('Front sealed drum brake dust cover',front,0,r,(r-.032)*.96,wide*1.99,black,gr['FrontWheel']);changes.append('Added enclosed nonmotor front drum cover')
 if name=='NIU KQi2 Pro':
  cylinder('NIU front drum brake center',front,0,r,.047,wide*1.95,black,gr['FrontWheel'])
 if name in ['Segway Ninebot GT1','Segway Ninebot GT2','Segway Ninebot GT3']:
  pts=[(dl*.38,dz-.02),(sx-.11,dz+.38),(sx+.035,dz+.32),(front-.04,r+.18),(front-.10,r+.10),(dl*.44,dz-.065)];panel('GT sculpted load-bearing front fairing',pts,.13,paint,gr['Steering']);panel('GT brushed front side plate',[(dl*.45,dz+.025),(sx-.095,dz+.33),(sx-.025,dz+.28),(front-.08,r+.18)],.137,bpy.data.materials['Steel'],gr['Steering']);changes.append('Added GT deep front fairing and side plate silhouette')
 if name in ['Segway Ninebot P65','Segway Ninebot P100S']:
  panel('P-Series sculpted headstock shell',[(dl*.30,dz-.03),(sx-.07,lo+.09),(sx+.03,lo+.055),(sx+.025,lo-.04),(dl*.42,dz-.065)],.12,paint,gr['Steering'])
  panel('P-Series orange rear heel trim',[(rear+.05,r+.12),(-dl*.43,dz+.05),(-dl*.57,dz+.13),(rear+.015,r+.17)],.115,accent,gr['Chassis']);changes.append('Added P monocoque neck and rear orange heel trim')
 if name=='Segway Ninebot ZT3 Pro':
  # Actual signature X lamp is down on the headstock, not under the console.
  lens=bpy.data.materials['Headlamp diffuser'];cx=sx+.065;cz=lo+.055
  panel('ZT3 headstock lamp housing',[(cx-.018,cz-.036),(cx+.025,cz-.036),(cx+.025,cz+.036),(cx-.018,cz+.036)],.10,black,gr['Steering'])
  for sy in [-1,1]:
   for sign in [-1,1]:
    a=Vector((cx+.028,sy*.035,cz+sign*.020));b=Vector((cx+.028,0,cz));d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.004,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.name='ZT3 signature X optical segment';o.parent=gr['Steering'];o.data.materials.append(lens);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  changes.append('Added source-position low X headlight')
 if name in ['KuKirin M4','KuKirin M4 Pro']:
  for sy in [0]:
   panel('M4 red deck flank stripe',[(-dl*.46,dz-.045),(dl*.41,dz-.045),(dl*.43,dz-.026),(-dl*.47,dz-.026)],c['dw']+.002,accent,gr['Chassis'])
  changes.append('Added M4 red battery-deck flank trim')
 if name=='Bogist M5 Pro':
  # M5 has teal rim rings in the exact retailer photograph.
  for parent,x in [(gr['FrontWheel'],front),(gr['RearWheel'],rear)]:
   for sy in [-1,1]:
    bpy.ops.mesh.primitive_torus_add(major_segments=56,minor_segments=8,major_radius=r-.031,minor_radius=.003,location=(x,sy*(wide+.003),r),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='M5 Pro teal rim accent';o.parent=parent;o.data.materials.append(accent);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 if name=='Kugoo S1 Pro':
  # Perforated sidewalls are actual open geometry: outer tread and inner bead linked by radial webs.
  for gn,x in [('FrontWheel',front),('RearWheel',rear)]:
   parent=gr[gn]
   for o in list(parent.children):
    if o.type=='MESH' and any(m and m.name=='Tire rubber' for m in o.data.materials):bpy.data.objects.remove(o,do_unlink=True)
   rubber=bpy.data.materials['Tire rubber']
   for ro,ri in [(r,r-.012),(r-.026,r-.033)]:
    n=84;v=[];faces=[]
    for y,rr in [(-wide,ro),(wide,ro),(-wide,ri),(wide,ri)]:v.extend((x+rr*math.cos(i*2*math.pi/n),y,r+rr*math.sin(i*2*math.pi/n)) for i in range(n))
    for i in range(n):
     j=(i+1)%n
     for a,b in [(0,1),(2,0),(1,3),(3,2)]:faces.append((a*n+i,a*n+j,b*n+j,b*n+i))
    d=bpy.data.meshes.new('Perforated rubber band');d.from_pydata(v,[],faces);d.update();o=bpy.data.objects.new('S1 Pro open honeycomb tire band',d);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(rubber)
   for i in range(30):
    a=i*2*math.pi/30;center=Vector((x+(r-.019)*math.cos(a),0,r+(r-.019)*math.sin(a)));bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name='S1 Pro honeycomb radial web';o.dimensions=(.014,wide*2,.006);o.rotation_euler[1]=-a;o.parent=parent;o.data.materials.append(rubber);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  changes.append('Authored open perforated honeycomb tire sidewalls')
 # Bake all additions and recompute exact statistics after final geometry.
 model=[o for o in descendants(root) if o.type=='MESH'];tri=0
 for o in model:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 # Compact added honeycomb webs and other new same-material objects by assembly.
 for g in gr.values():
  bucket={}
  for o in list(g.children):
   if o.type=='MESH':bucket.setdefault(o.data.materials[0].name,[]).append(o)
  for mn,objs in bucket.items():
   if len(objs)<2:continue
   bpy.ops.object.select_all(action='DESELECT')
   for o in objs:o.select_set(True)
   bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();objs[0].name=g.name+' | '+mn
 model=[o for o in descendants(root) if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in descendants(root):o.select_set(True)
 export=R/'apps/web/public'/note['url'].lstrip('/');bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 scene=bpy.context.scene;scene.cycles.samples=4;scene.render.filepath=str(O/(key+'.png'));bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(R/note['nativeSource']),compress=True)
 note.update(triangles=tri,meshes=len(model),bytes=export.stat().st_size,finalReferenceReview=changes or ['Material finish matched dark anodized hardware']);json.dump(note,open(f,'w'),indent=2);assert tri<120000 and len(model)<65 and export.stat().st_size<5000000,note;print('FINISHED',key,flush=True)
print('FINISH_PASS_COMPLETE',len(rows),flush=True)
