import bpy,bmesh,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v6.blend');s=bpy.context.scene;O=bpy.data.objects
Z0=79.484130859375
exec(open('/home/claude/w/v6_helpers.py').read())
mat=O['P01_한장바닥판_190x185x5'].data.materials[0]
bpy.data.objects.remove(O['P07_모터하판_일체'])
pl=box(-45,45,-75,-21,28.6,32.7,'P07_모터하판_일체')
for x in (-53,53): U(pl,box(x-10,x+10,-75,-21,32.6,36.6))
for x in (-53,53):
    for y in (-70,-26): D(pl,cyl(2.25,20,40,x,y))
pl.data.materials.append(mat);print('nm',clean(pl))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/w/out52/v6.blend')
