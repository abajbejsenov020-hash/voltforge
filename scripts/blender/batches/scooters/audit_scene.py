import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if o.type=='MESH' and not o.name.startswith('STUDIO'):
  boundlow=min((o.matrix_world@Vector(c)).z for c in o.bound_box)
  low=min((o.matrix_world@v.co).z for v in o.data.vertices)
  if boundlow<-.001 or low<-.001:print('LOW',o.name,'looseBox',round(boundlow,5),'vertices',round(low,5),'rotation',tuple(round(v,3) for v in o.rotation_euler))
