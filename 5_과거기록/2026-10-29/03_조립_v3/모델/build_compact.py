import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2]; O=R/'outputs/20261029_assembly_v3_A'; O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_원본배율검토_v3.0_A.blend'))
s=bpy.context.scene
refs=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠','L298N_43x43x27_SPEC_ENVELOPE','HY_SRF05_PCB_45x21_NO_DEPTH']
for o in list(s.objects):
 if o.type=='MESH' and o.name not in refs: bpy.data.objects.remove(o,do_unlink=True)
for t in list(bpy.data.texts): bpy.data.texts.remove(t)
def collection(n):
 c=bpy.data.collections.new(n);s.collection.children.link(c);return c
body=collection('V3_01_一体底板_한장바닥판');upper=collection('V3_02_선반_카메라센서');mount=collection('V3_03_모터캐스터_추정');hold=collection('V3_04_배터리고정');metal=collection('V3_05_지지대');wires=collection('V3_06_배선경로_예시')
made=[]
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);return m
cream=mat('V3_몸체',(.77,.79,.73));teal=mat('V3_고정대',(.13,.46,.5));gold=mat('V3_금속',(.78,.57,.2));orange=mat('V3_배선예시',(.95,.3,.05))
def finish(o,n,m,c):
 o.name=n;o.data.materials.clear();o.data.materials.append(m)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);made.append(o);o['fabrication_status']='REVIEW - estimated fits, no print release';return o
def cube(n,d,p,c=body,m=cream):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,m,c)
def cylinder(n,r,h,p,c=metal,m=gold,axis='Z',verts=40):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=h,location=p,rotation=(0,math.pi/2,0) if axis=='X' else (0,0,0));return finish(bpy.context.object,n,m,c)
def boolean(a,b,operation='DIFFERENCE'):
 bpy.context.view_layer.objects.active=a;mod=a.modifiers.new('mechanical_cut','BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=b;bpy.ops.object.modifier_apply(modifier=mod.name)
 made.remove(b);bpy.data.objects.remove(b,do_unlink=True)
def hole(o,x,y,z,diam=5,h=100):boolean(o,cylinder('cut',diam/2,h,(x,y,z)))
def slot(o,x,y,z,length,width,axis='X'):
 # Rounded-end slot, plan view. Length is overall length.
 a=(length-width)/2
 d=(length-width,width,120) if axis=='X' else (width,length-width,120)
 boolean(o,cube('slot',d,(x,y,z)))
 for sign in [-1,1]:hole(o,x+sign*a*(axis=='X'),y+sign*a*(axis=='Y'),z,width,120)
def bound(o):
 bpy.context.view_layer.update();p=[o.matrix_world@Vector(v) for v in o.bound_box];return ([min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)])
raw={n:hashlib.sha256(bpy.data.objects[n].data.vertices[0].co[:].__repr__().encode()).hexdigest() for n in refs[:8]}
for n in refs[:8]:bpy.data.objects[n].scale=(1,1,1)
caster=bpy.data.objects['캐스터 휠'];caster.location=(0,55,74.484130859375/2)
wheelz=97.0308837890625/2
for n,x in [('메카넘휠',-112),('Wheel_Right_REFERENCE_ONLY',112)]:bpy.data.objects[n].location=(x,-48,wheelz)
for n,x in [('모터',-53),('Motor_Right',53)]:bpy.data.objects[n].location=(x,-48,wheelz)
# Castor envelope top used as support contact, no mesh rescale.
z0=74.484130859375;zt=z0+5;zs=zt+30
bank=bpy.data.objects['보조배터리'];bank.location=(-34,0,zt+8.25)
lipo=bpy.data.objects['리포배터리'];lipo.location=(40,0,zt+12.5)
pi=bpy.data.objects['라즈베리'];pi.location=(-34,10,zs+4+12)
driver=bpy.data.objects['L298N_43x43x27_SPEC_ENVELOPE'];driver.location=(38,-25,zs+4+3+13.5)
sensor=bpy.data.objects['HY_SRF05_PCB_45x21_NO_DEPTH'];sensor.location=(0,91,zt+13.5)
# 190 x 185 plate with rounded front, narrowed rear for wheel clearance.
xy=[(-80,-80),(-76,-88),(-66,-92.5),(66,-92.5),(76,-88),(80,-80),(80,2),(95,18),(95,73),(92,83),(84,90),(74,92.5),(-74,92.5),(-84,90),(-92,83),(-95,73),(-95,18),(-80,2)]
N=len(xy);v=[(x,y,z) for z in [z0,zt] for x,y in xy];f=[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
me=bpy.data.meshes.new('base');me.from_pydata(v,[],f);me.update();base=bpy.data.objects.new('P01_한장바닥판_190x185x5',me);s.collection.objects.link(base);finish(base,base.name,cream,body)
shelf=cube('P02_분리선반_150x130x4',(150,130,4),(0,5,zs+2),upper,teal)
# Four M4 standoff clearance holes, class recommendation +1 mm.
for x in [-69,69]:
 for y in [-59,64]:
  hole(base,x,y,zt);hole(shelf,x,y,zs)
  cylinder('REF_M4_30_지지대',3.5,30,(x,y,zt+15))
# PCB envelope cradles, with clearance and open connector ends.
for x in [-64, -4]:cube('Pi_옆가이드',(2,64,3),(x,10,zs+5.5),upper,teal)
pad=cube('P03_드라이버받침_조절슬롯',(49,49,3),(38,-25,zs+5.5),upper,teal)
for x in [22,54]:
 for y in [-41,-9]:slot(pad,x,y,zs,9,4)
# 12 x 24 cable opening clear of boards and batteries, plus base tie-through slots.
slot(shelf,48,42,zs,26,12,'Y')
for x,y in [(78,40),(-82,40),(0,-78)]:slot(base,x,y,zt,12,4,'Y')
# Battery hard stops and removable bridge retainers: no strap purchases assumed.
for name,cx,w,l,h,postx in [('BANK',-34,68.5,140,16.5,[-74,6]),('LIPO',40,37,104,25,[16,64])]:
 for yy in [-l/2-2,l/2+2]:cube('stop_'+name,(w+4,2,5),(cx,yy,zt+2.5),hold,teal)
 for xx in [cx-w/2-2,cx+w/2+2]:cube('side_'+name,(2,l-12,4),(xx,0,zt+2),hold,teal)
 # One bridge; side stops and end stops constrain planar escape.
 bridgez=zt+h+1
 bridge=cube('P04_'+name+'_着脱固定バー',(postx[1]-postx[0]+8,10,3),((postx[0]+postx[1])/2,15,bridgez+1.5),hold,teal)
 for xx in postx:
  post=cube('P05_'+name+'_ねじ支柱',(8,12,h+1),(xx,15,zt+(h+1)/2),hold,teal)
  hole(post,xx,15,zt,4);hole(bridge,xx,15,zt,4)
  # Open lateral captive-nut pocket, M3 nut nominal 5.5 AF + clearance.
  boolean(post,cube('nut_access',(9,6.2,3),(xx,15,bridgez-4.5)))
# Motor brackets: scan envelope clearance; bore diameter is a design allowance, not motor spec.
for x in [-53,53]:
 high=cube('P06_모터상부_추정끼움',(20,46,z0-wheelz),(x,-48,(z0+wheelz)/2),mount,teal)
 low=cube('P07_모터하부_추정끼움',(20,46,19),(x,-48,wheelz-9.5),mount,teal)
 for p in [high,low]:
  boolean(p,cylinder('motor_envelope',14.5,30,(x,-48,wheelz),axis='X'))
  for yy in [-68,-28]:hole(p,x,yy,wheelz,5)
 for yy in [-68,-28]:
  hole(base,x,yy,zt,5)
  # Nut access near top; cap fasteners use separate lower captive nuts after measurement.
  boolean(high,cube('upper_nut_access',(22,8.2,3.8),(x,yy,z0-5)))
  boolean(high,cube('lower_cap_nut_access',(22,8.2,3.8),(x,yy,wheelz+6)))
# Adjustable caster M5 slots. Pattern is explicitly provisional, no nominal alteration of STL.
for x in [-19,19]:
 for y in [41,69]:slot(base,x,y,zt,14,6,'X')
# Front camera bridge and sensor bracket; exact camera threaded joint remains provisional.
for x in [-24,24]:
 foot=cube('P08_전방기둥',(8,12,40),(x,80,zt+20),upper,teal)
 hole(foot,x,80,zt,5);hole(base,x,80,zt,5)
camera=cube('P09_카메라받침_추정',(60,26,4),(0,79,zt+42),upper,teal);slot(camera,0,79,zt,17,7,'Y')
for x in [-25,25]:cube('P10_센서옆가이드',(3,7,25),(x,88,zt+12.5),upper,teal)
cube('P10_센서하단받침',(53,7,3),(0,88,zt+1.5),upper,teal)
# Show cable paths, not guaranteed connector envelopes. Kept separate and excluded from fabrication.
def cable(n,pts):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=1.2;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 ob=bpy.data.objects.new(n,cu);wires.objects.link(ob);cu.materials.append(orange)
cable('배선_경로예시',[(40,-52,zt+6),(76,-52,zt+7),(82,30,zt+10),(48,42,zs+10),(38,-2,zs+10)])
cable('USB_경로예시',[(-34,70,zt+9),(-78,75,zt+15),(-78,30,zs+14),(-34,57,zs+14)])
# Unite fixed stops and posts with base, so there are no unsecured loose feet.
for ob in list(hold.objects):
 if not ob.name.startswith('P04_'):boolean(base,ob,'UNION')
for ob in list(upper.objects):
 if ob.name.startswith('Pi_'):boolean(shelf,ob,'UNION')
# Driver pad is integral to shelf; its slots continue through shelf.
boolean(shelf,pad,'UNION')
for x in [22,54]:
 for y in [-41,-9]:slot(shelf,x,y,zs,9,4)
# Recess caster bolt heads below the battery support plane (estimated head envelope).
for x in [-19,19]:
 for y in [41,69]:
  boolean(base,cylinder('caster_head_recess',6,3.2,(x,y,zt-1.5)))
# Permanent front guides are united to base; camera deck remains removable.
for ob in list(upper.objects):
 if ob.name.startswith(('P08_','P10_')):boolean(base,ob,'UNION')

# Numeric audit: bounds are conservative; small contact overlaps are intentionally not called collisions.
audit={'scale_policy':'STL geometry unchanged; reference scales all 1; rotations/translations only','printer_mm':[210,200,195], 'base_mm':[190,185,5], 'single_vs_split':{'single':'selected: no structural seam, lower part/fastener count; tighter servicing space','split':'312 mm reference layout needs two base pieces and joint; more routing room but joint stiffness/fastener access unverified'},'assumptions':{'motor_mount_bore_mm':29,'motor_mount_width_mm':20,'caster_slot_centers_mm':[38,28],'caster_slot_size_mm':[14,6],'M4_clearance_mm':5,'M3_clearance_mm':4,'camera_slot_mm':[17,7],'battery_top_gap_mm':1,'battery_bar_thickness_mm':3,'battery_nut_pocket_mm':[6.2,3],'standoff_female_depth':'not assumed; bolt length pending','caster_sweep':'not verified, visible static envelope only','wheel_motor_fit':'shaft centers estimated from scan envelope; no coupler STL','battery_mass':'not known; no dynamic stability claim'},'reference_bounds':{n:bound(bpy.data.objects[n]) for n in refs},'checks':{}}
audit['checks']['all_STL_scales_1']=all(tuple(bpy.data.objects[n].scale)==(1,1,1) for n in refs[:8])
audit['checks']['reference_first_vertex_unchanged']=all(raw[n]==hashlib.sha256(bpy.data.objects[n].data.vertices[0].co[:].__repr__().encode()).hexdigest() for n in refs[:8])
audit['checks']['overall_wheel_width_mm']=bound(bpy.data.objects['Wheel_Right_REFERENCE_ONLY'])[1][0]-bound(bpy.data.objects['메카넘휠'])[0][0]
audit['checks']['wheel_to_rear_plate_lateral_gap_mm']=bound(bpy.data.objects['Wheel_Right_REFERENCE_ONLY'])[0][0]-80
audit['checks']['lipo_top_to_shelf_mm']=zs-bound(lipo)[1][2]
audit['checks']['lipo_bar_top_to_shelf_mm']=zs-(zt+25+1+3)
audit['checks']['ground_reference_wheels_caster_mm']=[bound(bpy.data.objects[n])[0][2] for n in ['메카넘휠','캐스터 휠']]
audit['checks']['bed_margin_per_side_mm']=[(210-190)/2,(200-185)/2]
audit['checks']['mesh_collision_test']='not complete: conservative envelope checks only; joints and caster rotation require verification'
(O/'v3_engineering_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
txt=bpy.data.texts.new('V3_README_출력전확인');txt.write(json.dumps(audit,ensure_ascii=False,indent=2))
for o in made:
 o['note']='New structure proposal. Fits/nut pockets pending actual assembly checks.'
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   a=area.spaces.active;a.region_3d.view_location=(0,0,75);a.region_3d.view_distance=410;a.region_3d.view_rotation=Vector((1,1,.8)).to_track_quat('Z','Y');a.region_3d.view_perspective='ORTHO';a.shading.color_type='MATERIAL';a.overlay.show_floor=False
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
cam=s.camera
def render(n,vec):
 center=Vector((0,0,75));d=Vector(vec).normalized();cam.location=center+d*1000;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=390;s.render.filepath=str(O/(n+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_한장차체조립_v3.1_A.blend'))
render('v3_assembled',(1,1,.85));render('v3_top',(0,0,1));render('v3_bottom',(0,0,-1))
for o in list(upper.objects)+list(metal.objects):o.hide_render=True
pi.hide_render=True;driver.hide_render=True
render('v3_lower',(1,1,1))
for o in list(upper.objects)+list(metal.objects):o.hide_render=False
pi.hide_render=False;driver.hide_render=False
print('AUDIT',json.dumps(audit['checks'],ensure_ascii=False))
