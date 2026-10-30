import bpy,bmesh,json,os
from pathlib import Path
from mathutils.bvhtree import BVHTree
# v5.1: front-left opening for power-bank USB-A plug (Pi power) + plug clearance check.
SRC=os.environ.get('CAR_SRC');O=Path(os.environ.get('CAR_OUT'));DST=os.environ.get('CAR_BLEND')
bpy.ops.wm.open_mainfile(filepath=SRC);s=bpy.context.scene
Z0=79.484130859375
def cube(n,d,p):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def boolean(a,b):
 bpy.context.view_layer.objects.active=a;m=a.modifiers.new('b','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(b,do_unlink=True)
cover=bpy.data.objects['P10_들어올림덮개_v5'];cover.name='P10_들어올림덮개_v5.1'
# Opening x -70..-40, full height (open bottom) so the plug + cable loop pass and the cover still lifts.
boolean(cover,cube('usb_open',(30,24,200),(-55,92,Z0+60)))
ref=bpy.data.collections['V4_추정형상_출력제외']
def refbox(n,d,p):
 o=cube(n,d,p)
 for c in list(o.users_collection):c.objects.unlink(o)
 ref.objects.link(o);return o
plugA=refbox('REF_USB_A_플러그+케이블굽힘_추정',(16,40,8),(-53,70+20,89))
plugIn=refbox('REF_충전입력_플러그_추정',(12,30,7),(-10,70+15,89))
def tree(o,dz=0):
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
 if dz:bmesh.ops.translate(bm,verts=bm.verts,vec=(0,0,dz))
 t=BVHTree.FromBMesh(bm);bm.free();return t
others=[o for o in s.objects if o.type=='MESH' and not o.hide_viewport]
T={o.name:tree(o) for o in others}
res={}
for p in [plugA,plugIn]:
 res[p.name]=[n for n,t in T.items() if n not in(p.name,'보조배터리') and T[p.name].overlap(t)]
sweep={}
for dz in range(2,131,2):
 tc=tree(cover,dz);h=[n for n,t in T.items() if n!=cover.name and tc.overlap(t)]
 if h:sweep[dz]=h
bm=bmesh.new();bm.from_mesh(cover.data);nm=sum(1 for e in bm.edges if not e.is_manifold);bm.free()
rep={'version':'v5.1','power_bank_ports':'front end (y=+70), from scan: USB-A x-59..-47 and x-41..-29, small input x~-10, z87..91',
 'pi_power_use_port':'outer USB-A (x-59..-47); inner one is 1mm from the left pillar','plug_collisions':res,'lift_sweep_collisions':sweep,'non_manifold_edges':nm,'static_contacts':[n for n,t in T.items() if n!=cover.name and tree(cover).overlap(t)]}
(O/'cover_v5_1_checks.json').write_text(json.dumps(rep,ensure_ascii=False,indent=1),encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT');cover.select_set(True);bpy.context.view_layer.objects.active=cover
bpy.ops.wm.stl_export(filepath=str(O/'P10_들어올림덮개_v5.1.stl'),export_selected_objects=True)
bpy.ops.wm.save_as_mainfile(filepath=DST,copy=True)
print(json.dumps(rep,ensure_ascii=False))
