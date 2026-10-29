import bpy, math, hashlib, json, array, bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_cover_preview_v3_4_A';O.mkdir(exist_ok=True)
sources=list((R/'references/parts/stl').glob('*.stl'))
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_U받침조립_v3.3_A.blend'))
s=bpy.context.scene
names=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
def digest(o):
 a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
ref={n:digest(bpy.data.objects[n]) for n in names}
c=bpy.data.collections.new('V3_4_둥근덮개_외형프리뷰');s.collection.children.link(c)
mat=bpy.data.materials.new('덮개_밝은아이보리');mat.diffuse_color=(.85,.88,.84,1)
def cube(n,d,p,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('rounded','BEVEL');m.width=bevel;m.segments=8;bpy.ops.object.modifier_apply(modifier=m.name)
 return o
def cut(a,b):
 bpy.context.view_layer.objects.active=a;m=a.modifiers.new('opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(b,do_unlink=True)
z=79.484130859375
cover=cube('덮개_外형검토_고정부미설계',(168,156,82),(0,-10,z+41),14)
cut(cover,cube('inner',(162,150,90),(0,-10,z+34),11))
# Free the wheels at the rear, without modifying reference wheel geometry.
for x in [-86,86]:cut(cover,cube('wheel_clearance',(20,120,32),(x,-50,z+5),3))
# Open front for camera bracket and sensor service access. Camera body is not modeled.
cut(cover,cube('front_access',(78,35,67),(0,67,z+28),9))
# Clear the existing shelf edge across the front opening.
cut(cover,cube('shelf_front_clearance',(156,24,10),(0,67,113.5),1))
# Ventilation slots above the shelf and side cable access below it.
for x in [-82,82]:
 for y in [-38,-22,-6,10,26]:cut(cover,cube('vent',(16,6,18),(x,y,141),2))
 cut(cover,cube('cable_access',(16,35,22),(x,39,95),3))
cover.data.materials.append(mat)
for old in list(cover.users_collection):old.objects.unlink(cover)
c.objects.link(cover)
cover['status']='EXTERIOR PREVIEW ONLY. No attachment holes or print orientation qualification. Camera envelope unknown.'
# Hide indicative wire curves, which are routes rather than physical cables.
for ob in s.objects:
 if ob.type=='CURVE':ob.hide_render=True;ob.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   a=area.spaces.active;a.region_3d.view_location=(0,0,83);a.region_3d.view_distance=440;a.region_3d.view_rotation=Vector((1,1,.7)).to_track_quat('Z','Y');a.region_3d.view_perspective='ORTHO';a.shading.color_type='MATERIAL'
bm=bmesh.new();bm.from_mesh(cover.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
report={'status':'cover appearance preview only; not print-ready','outer_mm':[168,156,82],'nominal_wall_mm':3,'mounts':'not designed','camera_body':'not included, front cutout provisional','curves':'illustrative wire routes hidden','nonmanifold_edges':bad,'source_files_unchanged':{p.name:hashes[p.name]==hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'reference_mesh_unchanged':{n:ref[n]==digest(bpy.data.objects[n]) for n in names},'all_reference_scales_one':all(tuple(bpy.data.objects[n].scale)==(1,1,1) for n in names)}
(O/'preview_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
t=bpy.data.texts.new('덮개프리뷰_먼저읽기');t.write(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_덮개프리뷰_v3.4_A.blend'))
s.render.resolution_x=1200;s.render.resolution_y=900
def render(n,d,center=(0,0,83),scale=410):
 d=Vector(d).normalized();s.camera.location=Vector(center)+d*1000;s.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(O/(n+'.png'));bpy.ops.render.render(write_still=True)
render('cover_front',(1,1,.7));render('cover_rear',(-1,-1,.7));render('cover_side',(1,0,.2))
cover.location.z+=105;render('cover_lifted',(1,1,.75),(0,0,115),490)
print(json.dumps(report,ensure_ascii=False))
