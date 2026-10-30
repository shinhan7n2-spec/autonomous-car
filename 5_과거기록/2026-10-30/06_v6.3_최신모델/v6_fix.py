import bpy,bmesh,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v6.blend');s=bpy.context.scene;O=bpy.data.objects
Z0=79.484130859375
exec(open('/home/claude/w/v6_helpers.py').read())
mat=O['P01_한장바닥판_190x185x5'].data.materials[0]
for n in ['P06_모터받침_일체','P07_모터하판_일체']: bpy.data.objects.remove(O[n])
def wedge(x):
    yz=[(-66,20),(-30,20),(-30,45.4),(-48,63.4),(-66,45.4)]
    v=[(xx,y,z) for xx in [x-12,x+12] for y,z in yz];n=5
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new('w');me.from_pydata(v,[],f);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new('w',me);s.collection.objects.link(o);return o
cr=box(-63,63,-75,-21,Z0-9,Z0-5,'P06_모터받침_일체')
for x in (-53,53): U(cr,box(x-10,x+10,-75,-21,43,Z0-5.001))
for x in (-53,53): D(cr,wedge(x))
for x in (-53,53):
    for y in (-70,-26): D(cr,cyl(1.7,40,Z0-4,x,y))
pl=box(-63,63,-75,-21,28.6,32.6,'P07_모터하판_일체')
for x in (-53,53): U(pl,box(x-10,x+10,-75,-21,32.599,36.6))
for x in (-53,53):
    for y in (-70,-26): D(pl,cyl(2.25,20,40,x,y))
# bridge between mounts must clear motors: cut cradle bridge where motors pass? (motors below z 62.3, bridge z>=70.5) ok
for o in (cr,pl): o.data.materials.append(mat); print(o.name,'nm',clean(o))
b=O['P01_한장바닥판_190x185x5'];bm=bmesh.new();bm.from_mesh(b.data)
for e in bm.edges:
    if not e.is_manifold: print('base edge',[tuple(round(c,2) for c in v.co) for v in e.verts],len(e.link_faces))
bm.free()
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/w/out52/v6.blend')
