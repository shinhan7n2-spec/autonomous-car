import bpy,bmesh,json,os
from pathlib import Path
from mathutils.bvhtree import BVHTree
# v5.2: caster plate holes from scan (approx 54 x 24 mm, M5), rotated 90deg (long side along car width).
SRC=os.environ['CAR_SRC'];O=Path(os.environ['CAR_OUT']);O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC);s=bpy.context.scene
Z0=79.484130859375;ZB=Z0-5
def cube(n,d,p):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def cyl(r,h,p):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=h,location=p);return bpy.context.object
def boolean(a,b,op='DIFFERENCE'):
 bpy.context.view_layer.objects.active=a;m=a.modifiers.new('b','BOOLEAN');m.operation=op;m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(b,do_unlink=True)
base=bpy.data.objects['P01_한장바닥판_190x185x5']
# 1) fill the old estimated slots (38x28 pattern, 14x6)
for x in [-19,19]:
 for y in [41,69]:boolean(base,cube('fill',(14.2,6.2,5),(x,y,Z0-2.5)),'UNION')
# 2) new slots: centre (0,50), holes x+-27, y 38/62; 5.5mm wide, +-2mm adjustable along x
holes=[(x,y) for x in [-27,27] for y in [38,62]]
for x,y in holes:
 sl=cube('slot',(4,5.5,20),(x,y,Z0));boolean(sl,cyl(2.75,20,(x-2,y,Z0)),'UNION');boolean(sl,cyl(2.75,20,(x+2,y,Z0)),'UNION');boolean(base,sl)
 # nut pocket in top face, 4mm deep, 8.2 across flats (nut cannot spin), lengthened with the slot
 boolean(base,cube('nut',(13,8.2,4.0),(x,y,Z0-2.0+0.01)))
bm=bmesh.new();bm.from_mesh(base.data);nm=sum(1 for e in bm.edges if not e.is_manifold);bm.free()
def tree(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);t=BVHTree.FromBMesh(bm);bm.free();return t
tb=tree(base)
new=[o.name for o in s.objects if o.type=='MESH' and o!=base and tb.overlap(tree(o))]
rep={'version':'v5.2','caster_plate_from_scan_mm':[68,51],'hole_pattern_mm':[54,24],'hole_dia_scan_mm':'4.4-5.0 (M5)','orientation':'long side along car width (rotated 90deg vs scan)',
 'holes_xy':holes,'slot':'5.5mm wide, +-2mm along x','nut_pocket':'13x8.2x4mm in top face, M5 nut flush; M5x10 from below through caster plate + base',
 'old_38x28_slots':'filled','non_manifold_edges':nm,'base_contacts_after':new,'note':'scan surface rough, measure plate holes before printing'}
(O/'caster_fix_v5_2.json').write_text(json.dumps(rep,ensure_ascii=False,indent=1),encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT');base.select_set(True);bpy.context.view_layer.objects.active=base
bpy.ops.wm.stl_export(filepath=str(O/'P01_한장바닥판_190x185x5.stl'),export_selected_objects=True)
bpy.ops.wm.save_as_mainfile(filepath=os.environ['CAR_BLEND'],copy=True)
print(json.dumps(rep,ensure_ascii=False))
