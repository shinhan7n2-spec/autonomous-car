import bpy, math, json, array, hashlib, bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_assembly_v3_3_A';O.mkdir(exist_ok=True);D=O/'STL';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_한장차체조립_v3.2_A.blend'))
s=bpy.context.scene;refs=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
def digest(o):
 a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
before={n:digest(bpy.data.objects[n]) for n in refs}
for o in list(s.objects):
 if o.name.startswith(('P06_','P07_')):bpy.data.objects.remove(o,do_unlink=True)
c=bpy.data.collections.new('V3_3_모터_U받침과평판');s.collection.children.link(c)
m=bpy.data.materials.get('V3_고정대');new=[]
def finish(o,n):
 o.name=n
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m);return o
def box(n,d,p):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n)
def cut(a,b):
 bpy.context.view_layer.objects.active=a;md=a.modifiers.new('cut','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=b;bpy.ops.object.modifier_apply(modifier=md.name);bpy.data.objects.remove(b,do_unlink=True)
def hole(a,x,y):
 bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=2.5,depth=100,location=(x,y,55));cut(a,bpy.context.object)
def wedge(x):
 # Open-ended 90-degree V opening, not a closed horizontal bore.
 yz=[(-48-18,20),(-48+18,20),(-48+18,45.4),(-48,63.4),(-48-18,45.4)]
 v=[(xx,y,z) for xx in [x-12,x+12] for y,z in yz];n=5
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new('v_cut');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('v_cut',me);s.collection.objects.link(o);return o
for x,side in [(-53,'L'),(53,'R')]:
 u=box('P06_'+side+'_U받침_V홈',(20,46,31.484130859375),(x,-48,(43+74.484130859375)/2));cut(u,wedge(x))
 cap=box('P07_'+side+'_평판',(20,46,4),(x,-48,34.6))
 for y in [-68,-28]:
  hole(u,x,y);hole(cap,x,y)
  # Two separate M4 nut seats: upper chassis attachment / lower plate clamp.
  for z in [65,49]:cut(u,box('nut_slot',(16,8.2,3.8),(x-3,y,z)))
 new.extend([u,cap])
# Show fasteners as separate non-print references, no modeled threads.
metal=bpy.data.collections.new('볼트_금속실물_출력하지않음');s.collection.children.link(metal)
gold=bpy.data.materials.get('V3_금속')
for x in [-53,53]:
 for y in [-68,-28]:
  for z in [69.484130859375,42.6]:
   bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=2,depth=20,location=(x,y,z));o=bpy.context.object;o.name='REF_M4x20_모터체결_나사산생략'
   for cc in list(o.users_collection):cc.objects.unlink(o)
   metal.objects.link(o);o.data.materials.append(gold)
report={'status':'STL PACKAGE; NOT MACHINE GCODE; material and fit verification pending','original_STL_full_hash_unchanged':{n:before[n]==digest(bpy.data.objects[n]) for n in refs},'assumptions':{'mount_V_angle_deg':90,'V_apex_z_mm':63.4,'motor_nominal_diameter_mm':22,'U_mm':[20,46,31.484130859375],'plate_mm':[20,46,4],'M4_hole_mm':5,'M4_nut_slot_mm':[8.2,3.8],'clamp_bolts':'M4x20 estimated; 2 upper + 2 lower per motor','fit':'V and flat plate proposed for nominal 22 mm motor; scan skew/shaft alignment not validated'},'parts':[]}
parts=[o for o in s.objects if o.type=='MESH' and o.name.startswith('P')]
for i,o in enumerate(sorted(parts,key=lambda v:v.name),1):
 cp=o.copy();cp.data=o.data.copy();s.collection.objects.link(cp)
 if o in new and o.name.startswith('P06_'):cp.rotation_euler.y=math.pi/2 # extruded side flat on bed; open V profile vertical
 bpy.context.view_layer.update();p=[cp.matrix_world@Vector(v) for v in cp.bound_box];lo=Vector([min(v[k] for v in p) for k in range(3)]);hi=Vector([max(v[k] for v in p) for k in range(3)]);cp.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 bpy.ops.object.select_all(action='DESELECT');cp.select_set(True);bpy.context.view_layer.objects.active=cp
 filename=f'{i:02d}_{o.name}.stl';bpy.ops.wm.stl_export(filepath=str(D/filename),export_selected_objects=True,global_scale=1,use_scene_unit=False)
 bm=bmesh.new();bm.from_mesh(cp.data);bad=sum(not e.is_manifold for e in bm.edges);todo=set(bm.verts);components=0
 while todo:
  components+=1;stack=[todo.pop()]
  while stack:
   vv=stack.pop()
   for edge in vv.link_edges:
    other=edge.other_vert(vv)
    if other in todo:todo.remove(other);stack.append(other)
 bm.free()
 report['parts'].append({'file':filename,'object':o.name,'export_bbox_mm':list(hi-lo),'nonmanifold_edges':bad,'connected_components':components,'bed_fit':all(a<=b for a,b in zip(hi-lo,[210,200,195]))})
 bpy.data.objects.remove(cp,do_unlink=True)
(O/'manufacturing_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for t in list(bpy.data.texts):
 if 'README' in t.name or '주의' in t.name:bpy.data.texts.remove(t)
t=bpy.data.texts.new('READ_ME_재료확인전_Gcode없음');t.write(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_U받침조립_v3.3_A.blend'))
s.render.resolution_x=1200;s.render.resolution_y=900
def render(n,center,d,scale):
 d=Vector(d).normalized();s.camera.location=Vector(center)+d*1000;s.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(O/(n+'.png'));bpy.ops.render.render(write_still=True)
render('assembly',(0,0,75),(1,1,.85),390)
for o in s.objects:
 if o.type in ['MESH','CURVE']:o.hide_render=o not in new[:2] and o.name!='모터'
render('motor_assembled',(-53,-48,52),(-1,-1,.7),110)
new[1].location.z-=18
render('motor_exploded',(-53,-48,45),(-1,-1,.7),120)
print(json.dumps(report,ensure_ascii=False))
