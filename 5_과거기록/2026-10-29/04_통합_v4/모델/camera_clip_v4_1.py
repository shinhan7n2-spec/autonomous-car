import bpy,bmesh,math,json,hashlib,array
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_camera_clip_v4_1_A';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_통합설계_v4.0_A.blend'));s=bpy.context.scene
files=list((R/'references/parts/stl').glob('*.stl'));hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
names=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
def digest(o):
 a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
before={n:digest(bpy.data.objects[n]) for n in names}
blue=bpy.data.materials['차체_블루그레이'];black=bpy.data.materials['창문_실제유리아님'];silver=bpy.data.materials['USB금속']
def cube(n,d,p,mat=blue):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
def boolean(a,b,op='DIFFERENCE'):
 bpy.context.view_layer.objects.active=a;m=a.modifiers.new('fit','BOOLEAN');m.operation=op;m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(b,do_unlink=True)
def cyl(n,r,h,p,axis='Z',verts=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=h,location=p,rotation=(math.pi/2 if axis=='Y' else 0,0,0));o=bpy.context.object;o.name=n;return o
# Replace only generated parts in a new scene file; preserve previous .blend and original STLs.
for o in list(s.objects):
 if o.name=='P09_카메라받침_추정' or o.name.startswith(('REF_APC850_','REF_카메라렌즈_')):bpy.data.objects.remove(o,do_unlink=True)
stand=cube('P09_카메라_클립받침',(78,30,4),(0,79,121.484130859375))
boolean(stand,cube('monitor_blade',(74,8,49),(0,82,146.5)),'UNION')
for x in [-24,24]:boolean(stand,cyl('deck_hole',2.5,12,(x,80,121.5)))
# M3 through-holes and front-open captive nut pockets. No camera threaded socket assumed.
for x in [-31,31]:
 boolean(stand,cyl('M3',2,20,(x,82,151),'Y'))
 boolean(stand,cyl('M3_nut',3.5,3.2,(x,84.6,151),'Y',6))
bar=cube('P13_カメラ_뒤클립누름판',(74,4,12),(0,70,151))
for x in [-31,31]:boolean(bar,cyl('M3',2,12,(x,70,151),'Y'))
# Estimated camera base and articulated back flap; separate from printable parts.
cam=cube('REF_카메라_몸체_치수추정',(70,34,38),(0,84,198),black)
bridge=cube('REF_카메라_힌지받침_추정',(48,28,6),(0,78,174),black)
front=cube('REF_카메라_앞걸림턱_추정',(48,4,16),(0,89,163),black)
back=cube('REF_카메라_뒤접이판_추정',(48,4,36),(0,75,151),black)
lens=cyl('REF_렌즈',10,3,(0,102,198),'Y',48);lens.data.materials.append(silver)
hinge=cube('REF_본체힌지_추정',(18,10,4),(0,80,178),black)
rearhinge=cube('REF_뒤접이힌지_추정',(48,4,4),(0,75,170),black)
camera=[cam,bridge,front,back,lens,hinge,rearhinge]
bolts=[]
for x in [-31,31]:
 o=cyl('REF_M3x20_카메라누름판_나사산생략',1.5,20,(x,78,151),'Y');o.data.materials.append(silver);bolts.append(o)
 o=cyl('REF_볼트머리_추정',3,2,(x,67,151),'Y');o.data.materials.append(silver);bolts.append(o)
cover=bpy.data.objects['P10_해치백덮개']
# Rear flap service pocket, clamp tool access, and vertical removal path.
boolean(cover,cube('clip_service_clearance',(82,38,70),(0,78,158)))
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
bpy.context.view_layer.update()
checks=[]
for a in [stand,bar]+camera:
 for b in [cover,bpy.data.objects['라즈베리'],bpy.data.objects['P02_분리선반_150x130x4']]:
  checks.append({'a':a.name,'b':b.name,'surface_pairs':len(tree(a).overlap(tree(b)))})
parts=[]
for o in [stand,bar,cover]:
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);todo=set(bm.verts);components=0
 while todo:
  components+=1;stack=[todo.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);stack.append(v)
 bm.free()
 cp=o.copy();cp.data=o.data.copy();s.collection.objects.link(cp)
 if o==stand:cp.rotation_euler.x=math.pi/2
 if o==cover:cp.rotation_euler.x=math.pi
 bpy.context.view_layer.update();pts=[cp.matrix_world@Vector(v) for v in cp.bound_box];lo=Vector([min(v[k] for v in pts) for k in range(3)]);hi=Vector([max(v[k] for v in pts) for k in range(3)])
 cp.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));bpy.ops.object.select_all(action='DESELECT');cp.select_set(True);bpy.context.view_layer.objects.active=cp
 bpy.ops.wm.stl_export(filepath=str(O/(o.name+'.stl')),export_selected_objects=True,global_scale=1,use_scene_unit=False);bpy.data.objects.remove(cp,do_unlink=True)
 parts.append({'name':o.name,'size_mm':list(hi-lo),'nonmanifold_edges':bad,'components':components})
report={'status':'estimated clip mount; physical fit not verified','assumptions':{'camera_body_mm':[70,34,38],'rear_flap_mm':[48,4,36],'blade_thickness_mm':8,'blade_top_z_mm':171,'front_back_clearance_mm':1,'clamp_initial_gap_mm':1,'hardware':'2 supplied common-set M3x20 bolts and M3 nuts; quantity not verified','M6':'not used; camera socket not assumed','rear_service_opening_mm':[82,38,70]},'no_tape_or_additional_purchased_parts':True,'original_files_unchanged':all(hashes[p.name]==hashlib.sha256(p.read_bytes()).hexdigest() for p in files),'reference_meshes_unchanged':all(before[n]==digest(bpy.data.objects[n]) for n in names),'reference_scale_one':all(tuple(bpy.data.objects[n].scale)==(1,1,1) for n in names),'parts':parts,'surface_checks':checks,'limitations':'estimated camera hinge positions; no motion sweep, clamping-force or actual assembly test'}
(O/'camera_mount_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
t=bpy.data.texts.new('カメラ_클립고정_추정기록');t.write(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_카메라클립_v4.1_A.blend'))
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
def render(name,d,center,scale):
 d=Vector(d).normalized();s.camera.location=Vector(center)+d*1000;s.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
render('assembly',(1,1,.65),(0,0,105),440)
visible=set([stand,bar]+camera+bolts)
for o in s.objects:
 if o.type in ['MESH','CURVE'] and o not in visible:o.hide_render=True
render('clip_rear',(-1,-1,.4),(0,80,168),165)
render('clip_side',(1,0,.05),(0,80,168),150)
print(json.dumps(report,ensure_ascii=False))
