import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v63.blend');s=bpy.context.scene;O=bpy.data.objects
exec(open('/home/claude/w/v6_helpers.py').read())
P=O['P07_모터하판_일체']
bb=[P.matrix_world@Vector(c) for c in P.bound_box];print('P07 bbox',[round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)])
# z profile at wing x=54 and center x=0
for x in (0,54,-54):
    r=[]
    for z in [28.0+0.5*i for i in range(20)]:
        hit=P.ray_cast(P.matrix_world.inverted()@Vector((x,-48,z)),Vector((0,1,0)),distance=200)[0]
        r.append(1 if hit else 0)
    print('x',x,''.join(map(str,r)))
def tree(o):
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);t=BVHTree.FromBMesh(bm);bm.free();return t
M=[o for o in s.objects if o.type=='MESH' and not o.hide_viewport and o is not P]
fill=[box(45,63.0,-75,-21,28.6,32.62,'fR'),box(-63.0,-45,-75,-21,28.6,32.62,'fL')]
for f in fill:
    t=tree(f);print(f.name,'겹침',[o.name for o in M if t.overlap(tree(o))])
for f in fill: U(P,f)
print('nm',clean(P))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/w/out52/v64.blend')
