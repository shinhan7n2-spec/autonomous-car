import bpy,math,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'outputs/20261029_structure_v2_A'; OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/layout-preview-v1/20261029_자율주행자동차_부품배치_v1.0_A.blend'))
s=bpy.context.scene; s.render.resolution_x=1100;s.render.resolution_y=850
cam=s.camera; cam.data.type='ORTHO'
parts=[o for o in s.objects if o.type=='MESH']; lower=[]; upper=[]; hardware=[]; base=[]
def coll(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
cb=coll('01_둥근바닥판_검토형상');cl=coll('02_하부고정대');cu=coll('03_선반과전방거치대');ch=coll('04_지지대와볼트_조립설명용');cr=coll('05_제공부품_참고형상')
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
for o in parts:move(o,cr)
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
cream=mat('몸체_아이보리',(.78,.79,.73));teal=mat('거치대_청록',(.17,.48,.50));gold=mat('금속_체결설명',(.75,.56,.22));silver=mat('가상체결표시',(.68,.70,.73))
def finish(o,name,m,c,group):
 o.name=name;o.data.materials.append(m);move(o,c);group.append(o);o['status']='CONCEPT ONLY: proposed geometry, no verified fabrication dimensions';return o
def box(name,dims,loc,m=teal,c=cu,group=upper,bevel=1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('soft_edges','BEVEL');mod.width=bevel;mod.segments=3
 return finish(o,name,m,c,group)
def cyl(name,r,depth,loc,m=gold,c=ch,group=hardware,axis='Z',vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc,rotation=(0,math.pi/2,0) if axis=='X' else (0,0,0));return finish(bpy.context.object,name,m,c,group)
def outline():
 pts=[]
 for cx,cy,start in [(48,135,0),(-48,135,90),(-48,-117,180),(48,-117,270)]:
  for i in range(13):
   a=math.radians(start+i*90/12);x=cx+30*math.cos(a);y=cy+30*math.sin(a)
   # Rear wheel recess: narrow the body where the rear wheels rotate.
   factor=.705 if y<-35 else (.705+(y+35)/15*.295 if y<-20 else 1)
   pts.append((x*factor,y))
 return pts
pts=outline();n=len(pts)
def plate(name,xy,z0,z1,m,c,group):
 n=len(xy);v=[(x,y,z) for z in [z0,z1] for x,y in xy];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o);return finish(o,name,m,c,group)
plate('둥근바닥판_두께미확정',pts,62,66,cream,cb,base)
# Low perimeter rim; top is open for servicing.
inner=[(x*.95,(y-9)*.97+9) for x,y in pts];verts=[]
for z,loop in [(66,pts),(73,pts),(66,inner),(73,inner)]:verts.extend([(x,y,z) for x,y in loop])
faces=[]
for i in range(n):
 j=(i+1)%n
 faces.extend([(i,j,j+n,i+n),(2*n+i,3*n+i,3*n+j,2*n+j),(n+i,n+j,3*n+j,3*n+i),(i,2*n+i,2*n+j,j)])
me=bpy.data.meshes.new('rim');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('낮은둥근테두리',me);s.collection.objects.link(ob);finish(ob,ob.name,cream,cb,base)
# Nominal contact levels align the components with the new support surfaces.
bpy.data.objects['보조배터리'].location.z+=3;bpy.data.objects['리포배터리'].location.z+=3
bpy.data.objects['라즈베리'].location.z+=5;bpy.data.objects['L298N_43x43x27_SPEC_ENVELOPE'].location.z+=3
board=bpy.data.objects['라즈베리'];sensor=bpy.data.objects['HY_SRF05_PCB_45x21_NO_DEPTH']
# Shelf on four nominal 30mm spacers. Holes/threads deliberately not finalized.
box('분리형보드선반_장착구멍미확정',(150,126,4),(0,27.5,98),teal,cu,upper,3)
for x in [-68,68]:
 for y in [-20,75]:
  cyl('M4_30mm_지지대_위치제안',3.5,30,(x,y,81))
  cyl('M4_20mm_볼트_기호',2,20,(x,y,99),silver)
  cyl('M4_머리_개념표시',4,3,(x,y,110.5),silver)
# Electronics board uses its own cradle, not M4 standoffs through Pi holes.
for x in [-49,9]:box('보드옆받침_실물형상대조전',(3,90,7),(x,10,103.5),teal)
# Battery tray lips, no tightening onto battery cells.
for x in [-62,53]:box('배터리측면받침',(3,144,8),(x,10,70),cream,cb,base)
box('배터리뒤멈춤',(115,3,8),(-4.5,-62,70),cream,cb,base)
# Driver support ledge and keep-out edge, based on known outer envelope only.
box('드라이버받침',(49,49,3),(27,-115,67.5),teal,cb,base)
bpy.data.objects['L298N_43x43x27_SPEC_ENVELOPE'].location.z+=3
for x in [3,51]:box('드라이버측면턱',(3,49,5),(x,-115,71),teal,cb,base)
# Motor saddles: split ring concept from scan bounding section, not fit-tested bores.
for x in [-30,30]:
 box('모터고정대_상부플랜지',(27,40,4),(x,-80,60),teal,cl,lower)
 for top in [False,True]:
  seg=24;v=[]
  for xx in [x-10,x+10]:
   for radius in [15,18]:
    for k in range(seg+1):
     a=(0 if top else math.pi)+math.pi*k/seg;v.append((xx,-80+radius*math.cos(a),48+radius*math.sin(a)))
  stride=seg+1;faces=[]
  for k in range(seg):
   faces.extend([(k,k+1,stride+k+1,stride+k),(2*stride+k,3*stride+k,3*stride+k+1,2*stride+k+1),(k,2*stride+k,2*stride+k+1,k+1),(stride+k,stride+k+1,3*stride+k+1,3*stride+k)])
  for k in [0,seg]:faces.append((k,stride+k,3*stride+k,2*stride+k))
  me=bpy.data.meshes.new('saddle');me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new('motorcap',me);s.collection.objects.link(o);finish(o,'모터새들_'+('상부' if top else '하부')+'_끼움미확정',teal,cl,lower)
 for y in [-97,-63]:cyl('모터고정볼트_위치설명',2,20,(x,y,55),silver)
# Caster backing plate touches nominal top of caster. Actual four hole pattern not invented.
box('캐스터장착보강판_구멍패턴대조전',(54,64,3),(0,124,60.5),teal,cl,lower,2)
# Forward sensor U-frame; open in front and around transducer region.
box('센서받침턱',(51,12,3),(0,146,78),teal)
for x in [-25,25]:box('센서옆기둥',(4,10,28),(x,146,90),teal)
for x in [-25,25]:box('센서거치대다리',(5,17,12),(x,139,72),teal)
# Camera support only. Camera body and thread location are not fabricated.
for x in [-20,20]:box('카메라받침기둥',(7,14,42),(x,116,87),teal)
box('카메라받침대_크기미확정',(54,32,4),(0,116,110),teal)
cyl('카메라_M6x20_조립기호_위치미확정',3,20,(0,116,122),silver)
cyl('카메라볼트머리_개념',5,3,(0,116,110.5),silver)
allmesh=[o for o in s.objects if o.type=='MESH']
def render(name,objs,d=(1,-1,.8),scale=460):
 for o in allmesh:o.hide_render=o not in objs
 bpy.context.view_layer.update();pts=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);center=(lo+hi)/2
 v=Vector(d).normalized();cam.location=center+v*1100;cam.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler()
 if d==(0,0,1):cam.rotation_euler=(0,0,0)
 if d==(0,0,-1):cam.rotation_euler=(math.pi,0,0)
 cam.data.ortho_scale=scale;s.render.filepath=str(OUT/f'{name}.png');bpy.ops.render.render(write_still=True)
render('assembled',allmesh)
render('front_iso',allmesh,(1,1,.75))
for name,d in [('top',(0,0,1)),('bottom',(0,0,-1)),('front',(0,1,0)),('rear',(0,-1,0)),('left',(-1,0,0)),('right',(1,0,0))]:render(name,allmesh,d)
hideupper=set(upper+[board,sensor]);render('lower', [o for o in allmesh if o not in hideupper],(1,1,1))
render('structure',[o for o in base+lower+upper+hardware],(1,1,.8))
# Exploded assembly: genuine objects shifted by group, then restored.
original={o:o.location.copy() for o in allmesh}
for o in upper:o.location.z+=68
board.location.z+=108;sensor.location.z+=68
for o in hardware:o.location.z+=40
for o in lower:o.location.z-=48
for name in ['모터','Motor_Right']:bpy.data.objects[name].location.z-=48
bpy.data.objects['캐스터 휠'].location.z-=85
bpy.data.objects['메카넘휠'].location.x-=48;bpy.data.objects['Wheel_Right_REFERENCE_ONLY'].location.x+=48
render('exploded',allmesh,(1,1,.7),560)
for o,pos in original.items():o.location=pos;o.hide_render=False
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   a=area.spaces.active;a.region_3d.view_location=(0,10,65);a.region_3d.view_distance=480;a.region_3d.view_rotation=Vector((1,1,.8)).to_track_quat('Z','Y');a.region_3d.view_perspective='ORTHO';a.clip_end=10000;a.shading.color_type='MATERIAL';a.overlay.show_floor=False
bpy.ops.object.select_all(action='DESELECT')
text=bpy.data.texts.new('먼저읽기_구조검토용');text.write('구조검토용 초안. 출력금지. 몸체 두께/고정대 끼움/구멍/배선/강도 미검증. 볼트는 조립 설명용 기호. 카메라 본체 미포함. 원본 STL 보존. Scene 컬렉션 01~05로 부품을 숨겨 내부 확인 가능.')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/structure-preview-v2/20261029_자율주행자동차_몸체조립검토_v2.0_A.blend'))
(OUT/'assumptions.json').write_text(json.dumps({'status':'CONCEPT ONLY - NOT PRINT READY','base_z':[62,66],'shelf_z':[96,100],'spacer_length_mm':30,'assumed_structure':'All body, saddle, cradle, shelf sizes are visualization proposals, not measured or approved fabrication dimensions. No final bolt holes or threads. No camera body.','source_blend':'layout-preview-v1'},ensure_ascii=False,indent=2),encoding='utf-8')
