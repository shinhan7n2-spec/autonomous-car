import bpy,bmesh,math,json,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_battery_service_v4_2_A';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_카메라클립_v4.1_A.blend'));s=bpy.context.scene
names=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
def digest(o):
 a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
before={n:digest(bpy.data.objects[n]) for n in names};files=list((R/'references/parts/stl').glob('*.stl'));sha={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
mat=bpy.data.materials['차체_블루그레이'];z=79.484130859375
def cube(n,d,p):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
def boolean(a,b,op='DIFFERENCE'):
 bpy.context.view_layer.objects.active=a;m=a.modifiers.new('service','BOOLEAN');m.solver='EXACT';m.operation=op;m.object=b;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(b,do_unlink=True)
def cylinder(r,h,p,y=False,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=h,location=p,rotation=(math.pi/2 if y else 0,0,0));return bpy.context.object
base=bpy.data.objects['P01_한장바닥판_190x185x5'];shelf=bpy.data.objects['P02_분리선반_150x130x4'];cover=bpy.data.objects['P10_해치백덮개'];gates=[]
# A rear standoff obstructed the unchanged power-bank envelope. Relocate the supplied spacer.
for o in s.objects:
 if o.name.startswith('REF_M4_30_지지대') and o.location.x<0:o.location.x=8 if o.location.y<0 else -76
boolean(shelf,cube('front_left_mount_ear',(16,16,4),(-76,64,111.484130859375)),'UNION')
for o in [base,shelf]:boolean(o,cylinder(2.5,100,(8,-59,100)))
for o in [base,shelf]:boolean(o,cylinder(2.5,100,(-76,64,100)))
boolean(cover,cube('front_spacer_relief',(12,12,36),(-76,64,97)))
boolean(cover,cube('front_ear_relief',(18,18,6),(-76,64,111.484130859375)))
# Reinforce the now cantilevered shelf edge, with clearance above the taller LiPo.
for y in [-49,-24]:boolean(shelf,cube('shelf_rib',(144,5,3.1),(0,y,108.034130859375)),'UNION')
for name,cx,w,l,h,xs in [('BANK',-34,68.5,140,16.5,[-74,6]),('LIPO',40,37,104,25,[16,64])]:
 gy=-l/2-6
 # Remove only the fixed rear stop, preserving the five-mm floor and side guides.
 boolean(base,cube('rear_stop_relief',(w+6,8,8),(cx,-l/2-2,z+4.01)))
 gate=cube('P14_'+name+'_뒤잠금판',(xs[1]-xs[0]+8,4,h+3),((xs[0]+xs[1])/2,gy,z+(h+3)/2));gates.append(gate)
 # Open cable notch has no closed eye that would trap a connector during removal.
 boolean(gate,cube('open_cable_notch',(24,8,9),(cx,gy,z+h+1)))
 for x in xs:
  block=cube('rear_anchor',(8,10,10),(x,gy+7,z+4.9))
  boolean(block,cylinder(2,24,(x,gy+7,z+5),True))
  boolean(block,cylinder(3.5,3.2,(x,gy+10.6,z+5),True,6))
  boolean(base,block,'UNION');boolean(gate,cylinder(2,12,(x,gy,z+5),True))
# Remove the rear shell wall from both withdrawal paths. The main cover stays installed.
boolean(cover,cube('rear_service_opening',(150,46,31),(-5,-80,z+15.3)))
# Inspect conservative straight withdrawal volumes without altering reference geometry.
audit=[]
for name,cx,w,l,h,travel in [('BANK',-34,68.5,140,16.5,165),('LIPO',40,37,104,25,155)]:
 sweep=cube('audit_sweep',(w+.6,l+travel,h+.4),(cx,-travel/2,z+h/2+.3))
 obstacles=[base,shelf,cover,bpy.data.objects['P04_보조배터리_고정가로대'],bpy.data.objects['P05_리포배터리_고정가로대']]+[o for o in s.objects if o.name.startswith('REF_M4_30_지지대')]
 for o in obstacles:
  cp=sweep.copy();cp.data=sweep.data.copy();s.collection.objects.link(cp);bpy.context.view_layer.objects.active=cp;m=cp.modifiers.new('overlap','BOOLEAN');m.operation='INTERSECT';m.solver='EXACT';m.object=o;bpy.ops.object.modifier_apply(modifier=m.name)
  bm=bmesh.new();bm.from_mesh(cp.data);vol=abs(bm.calc_volume());bm.free();bpy.data.objects.remove(cp,do_unlink=True)
  audit.append({'battery':name,'obstacle':o.name,'intersection_mm3':vol})
 bpy.data.objects.remove(sweep,do_unlink=True)
parts=[]
for o in [base,shelf,cover]+gates:
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);todo=set(bm.verts);components=0
 while todo:
  components+=1;stack=[todo.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);stack.append(v)
 bm.free();cp=o.copy();cp.data=o.data.copy();s.collection.objects.link(cp)
 if o==cover:cp.rotation_euler.x=math.pi
 if o in gates:cp.rotation_euler.x=math.pi/2
 bpy.context.view_layer.update();pts=[cp.matrix_world@Vector(v) for v in cp.bound_box];lo=Vector([min(v[k] for v in pts) for k in range(3)]);hi=Vector([max(v[k] for v in pts) for k in range(3)])
 cp.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));bpy.ops.object.select_all(action='DESELECT');cp.select_set(True);bpy.context.view_layer.objects.active=cp;bpy.ops.wm.stl_export(filepath=str(O/(o.name+'.stl')),export_selected_objects=True,global_scale=1,use_scene_unit=False);bpy.data.objects.remove(cp,do_unlink=True)
 parts.append({'name':o.name,'size_mm':list(hi-lo),'nonmanifold_edges':bad,'components':components})
report={'status':'mechanical service design; no electrical/charging verification','original_files_unchanged':all(sha[p.name]==hashlib.sha256(p.read_bytes()).hexdigest() for p in files),'reference_geometry_unchanged':all(before[n]==digest(bpy.data.objects[n]) for n in names),'reference_scales_one':all(tuple(bpy.data.objects[n].scale)==(1,1,1) for n in names),'hardware':'4 supplied M3x16 bolts and M3 nuts for two rear gates; actual quantities/head shape unverified','battery_motion':'negative Y straight withdrawal after disconnecting and removing corresponding rear gate; 165mm BANK / 155mm LIPO swept clearance','standoff_move_mm':[{'from':[-69,-59],'to':[8,-59]},{'from':[-69,64],'to':[-76,64]}],'wire_notch_mm':[24,9],'limits':['connector dimensions/locations and cable bend radius estimated, cables not included in sweep','no charger compatibility, charging behaviour or thermal test','no loaded shelf stiffness or vibration test','STL scan unit assumed mm; shape and scale unchanged'],'parts':parts,'withdrawal_checks':audit}
(O/'battery_service_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');t=bpy.data.texts.new('배터리탈착_검토');t.write(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_배터리탈착_v4.2_A.blend'))
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
def render(n,d,center=(0,0,110),scale=430):
 d=Vector(d).normalized();s.camera.location=Vector(center)+d*1000;s.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(O/(n+'.png'));bpy.ops.render.render(write_still=True)
render('rear_closed',(-1,-1,.45))
for o in gates:o.hide_render=True
bpy.data.objects['보조배터리'].location.y-=165;bpy.data.objects['리포배터리'].location.y-=155
render('battery_removal',(-1,-1,.8),(0,-55,105),510)
print('DONE',json.dumps(report,ensure_ascii=False))

