import bpy,bmesh,math
from mathutils import Vector,Matrix
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v64.blend');s=bpy.context.scene;O=bpy.data.objects
exec(open('/home/claude/w/v6_helpers.py').read())
P=O['P07_모터하판_일체']
for x in (-53,53):
    for y in (-70,-26):
        D(P,cyl(2.25,27,38,x,y)); D(P,cyl(4.25,27,32.6,x,y))   # through hole + head pocket from below (same bolt seat height as before)
print('nm',clean(P))
# islands
bm=bmesh.new();bm.from_mesh(P.data);seen=set();k=0
for v in bm.verts:
    if v in seen: continue
    k+=1;st=[v]
    while st:
        a=st.pop()
        if a in seen: continue
        seen.add(a);st.extend(e.other_vert(a) for e in a.link_edges)
print('islands',k)
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/w/out52/v64.blend')
# export flat: bottom (z28.6) on bed, no rotation
me=P.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
bm=bmesh.new();bm.from_mesh(me);bm.transform(P.matrix_world)
z0=min(v.co.z for v in bm.verts);cx=sum(v.co.x for v in bm.verts)/len(bm.verts)
bmesh.ops.translate(bm,verts=bm.verts,vec=(0,48,-z0))
m2=bpy.data.meshes.new('o');bm.to_mesh(m2);o=bpy.data.objects.new('P07_모터하판_일체',m2);s.collection.objects.link(o)
for x in s.objects: x.select_set(False)
o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.wm.stl_export(filepath='/home/claude/w/print/P07_모터하판_일체.stl',export_selected_objects=True,apply_modifiers=False)
