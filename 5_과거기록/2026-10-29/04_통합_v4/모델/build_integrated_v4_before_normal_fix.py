import bpy, math, json, hashlib, array, bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_integrated_v4_A';O.mkdir(exist_ok=True);D=O/'STL_슬라이서검사전';D.mkdir(exist_ok=True)
sources=list((R/'references/parts/stl').glob('*.stl'));hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_U받침조립_v3.3_A.blend'));s=bpy.context.scene
refs=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
def digest(o):
 a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
before={n:digest(bpy.data.objects[n]) for n in refs}
def mat(n,col):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);return m
blue=mat('차체_블루그레이',(.22,.48,.62));black=mat('창문_실제유리아님',(.055,.10,.14));white=mat('LAN_흰색',(.92,.93,.91));silver=mat('USB금속',(.62,.66,.7));amber=mat('램프_출력표면표시',(.95,.67,.19))
c=bpy.data.collections.new('V4_신규설계');s.collection.children.link(c);reference=bpy.data.collections.new('V4_추정형상_출력제외');s.collection.children.link(reference)
def move(o,col):
 for cc in list(o.users_collection):cc.objects.unlink(o)
 col.objects.link(o)
def cube(n,d,p,m=blue,bevel=0,col=c):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  md=o.modifiers.new('round','BEVEL');md.width=bevel;md.segments=4;bpy.ops.object.modifier_apply(modifier=md.name)
 o.data.materials.append(m);move(o,col);return o
def cut(a,b,operation='DIFFERENCE'):
 bpy.context.view_layer.objects.active=a;md=a.modifiers.new('joint','BOOLEAN');md.operation=operation;md.solver='EXACT';md.object=b;bpy.ops.object.modifier_apply(modifier=md.name);bpy.data.objects.remove(b,do_unlink=True)
def hole(a,x,y,z,diam=4):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=diam/2,depth=120,location=(x,y,z));cut(a,bpy.context.object)
base=bpy.data.objects['P01_한장바닥판_190x185x5'];shelf=bpy.data.objects['P02_분리선반_150x130x4'];z=79.484130859375
# Tapered longitudinal silhouette: hatch rear, roof, windscreen, low bonnet.
stations=[(-88,127,78),(-70,151,73),(-45,166,70),(18,166,70),(60,140,78),(76,126,84),(91,116,86)]
def loft(name,inner=False):
 v=[]
 for y,h,w in stations:
  yy=y+(3 if y<0 else -3) if y in [-88,91] and inner else y
  wb=83 if inner else 86;ww=w-3 if inner else w;hh=h-3 if inner else h;bottom=z-5 if inner else z
  v.extend([(-wb,yy,bottom),(wb,yy,bottom),(ww,yy,hh),(-ww,yy,hh)])
 n=len(stations);f=[(3,2,1,0),tuple(4*(n-1)+k for k in range(4))]
 for i in range(n-1):
  for j in range(4):f.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);o.data.materials.append(blue);return o
cover=loft('P10_해치백덮개');cut(cover,loft('inner',True))
for xx in [-86,86]:
 cut(cover,cube('wheel_arch',(20,112,33),(xx,-48,85),bevel=4))
 cut(cover,cube('lower_air',(18,32,16),(xx,38,91),bevel=3))
# Camera and USB/RF service opening, cover cannot shade lens in front.
cut(cover,cube('camera_open',(80,60,66),(0,82,141),bevel=5))
cut(cover,cube('usb_rf_open',(46,55,26),(-47,77,124),bevel=3))
cut(cover,cube('shelf_clearance',(158,30,11),(0,70,113.5)))
for xx in [-39,-21,-3,15,33,51]:cut(cover,cube('roof_vent',(5,43,25),(xx,-12,163),bevel=1))
for xx in [-80,80]:
 for yy in [-44,-28,-12,4]:cut(cover,cube('side_vent',(26,6,17),(xx,yy,139),bevel=1))
# Integral cover feet: use M3x16, accessible from the underside, nuts seated above feet.
for xx in [-73,73]:
 for yy in [-82,83]:
  foot=cube('cover_foot',(14,18,5),(xx,yy,z+2.5));cut(cover,foot,'UNION');hole(cover,xx,yy,z);hole(base,xx,yy,z)
  # Hexagonal nut seat open from above; exact nut must match before release.
  bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=3.5,depth=3,location=(xx,yy,z+4));cut(cover,bpy.context.object)
# Corner retainers around reference board envelope; cooling surface remains open.
for label,postxs,ys,height,reach in [('PI',[-69,1],[-20,40],25,7),('DRIVER',[10.5,65.5],[-37,-13],31,6)]:
 floor=113.484130859375
 for side,xx in enumerate(postxs):
  for yy in ys:
   post=cube('post',(8,10,height),(xx,yy,floor+height/2));hole(post,xx,yy,floor)
   cut(post,cube('nut_access',(7,6.2,3),(xx-1,yy,floor+height-4.5)))
   cut(shelf,post,'UNION')
   dx=reach if side==0 else -reach
   tab=cube(f'P11_{label}_脱落防止',(18,10,3),(xx+dx/2,yy,floor+height+1.5));hole(tab,xx,yy,floor)
# Camera stand now has screws from underneath; two positions are generic estimates.
camera_deck=bpy.data.objects['P09_카메라받침_추정']
for xx in [-24,24]:
 hole(camera_deck,xx,80,120,5)
# Sensor back retaining strip, clamping edges rather than covering transducers.
sensorbar=cube('P12_센서뒤고정띠',(56,3,6),(0,86,99));
# Shape references are NOT print parts, dimensions remain explicit assumptions.
lan=cube('REF_A1000mini_推定24.6x16x8',(16,24.6,8),(-48,65.3,122),white,1.2,reference)
cube('REF_USB插入端_推定',(12,8,4.5),(-48,51,122),silver,0,reference)
cam=cube('REF_APC850_외형추정',(70,34,38),(0,84,145),black,5,reference)
cube('REF_APC850_클립추정',(48,26,6),(0,79,126.5),black,2,reference)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=10,depth=3,location=(0,102,145),rotation=(math.pi/2,0,0));lens=bpy.context.object;lens.name='REF_카메라렌즈_예시';lens.data.materials.append(silver);move(lens,reference)
# No extra real-world lighting parts: these are colour-only surface patches, excluded from exports.
decor=[]
for xx in [-62,62]:decor.append(cube('장식_헤드램프_부품추가아님',(24,1,7),(xx,91.5,104),amber,0,reference))
for ob in s.objects:
 if ob.type=='CURVE':ob.hide_render=True;ob.hide_viewport=True
# Document assumptions and verify existing STL data untouched.
report={'status':'integrated design with estimated interfaces; not machine-ready','material':'PLA selected; machine cartridge unconfirmed','wifi':{'model':'A1000mini internal antenna','shape_estimate_mm':[24.6,16,8],'reserved_protrusion_mm':30,'source':'https://www.kwshop.co.kr/goods/view?no=6540','exact_dimensions_verified':False,'USB_port_position':'estimated from provided Pi envelope'},'camera':{'estimate_mm':[70,34,38],'exact_dimensions_verified':False},'thermal':'roof/side vents and lower inlet; no added fan; no temperature simulation','radio':'opening around USB adapter; no RF test or signal-strength guarantee','cover_mount':'4 M3x16 bolts and M3 nuts proposed; nut AF6.06 cavity estimate','board_retention':'edge tabs around reference envelope; actual PCB component clearance pending','sensor_retention':'back strip only; attachment detail incomplete','source_hashes_unchanged':{p.name:hashes[p.name]==hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'reference_geometry_unchanged':{n:before[n]==digest(bpy.data.objects[n]) for n in refs},'scale_one':all(tuple(bpy.data.objects[n].scale)==(1,1,1) for n in refs),'parts':[]}
bpy.context.view_layer.update()
for o in [o for o in s.objects if o.type=='MESH' and o.name.startswith('P')]:
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);todo=set(bm.verts);components=0
 while todo:
  components+=1;stack=[todo.pop()]
  while stack:
   vv=stack.pop()
   for e in vv.link_edges:
    v=e.other_vert(vv)
    if v in todo:todo.remove(v);stack.append(v)
 bm.free()
 cp=o.copy();cp.data=o.data.copy();s.collection.objects.link(cp)
 if o.name.startswith('P06_'):cp.rotation_euler.y=math.pi/2
 if o==cover:cp.rotation_euler.x=math.pi
 bpy.context.view_layer.update();pts=[cp.matrix_world@Vector(v) for v in cp.bound_box];lo=Vector([min(v[k] for v in pts) for k in range(3)]);hi=Vector([max(v[k] for v in pts) for k in range(3)])
 cp.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));bpy.ops.object.select_all(action='DESELECT');cp.select_set(True);bpy.context.view_layer.objects.active=cp
 fn=o.name+'.stl';bpy.ops.wm.stl_export(filepath=str(D/fn),export_selected_objects=True,global_scale=1,use_scene_unit=False)
 report['parts'].append({'file':fn,'size_mm':list(hi-lo),'nonmanifold_edges':bad,'connected_components':components,'bed_fit':all(a<=b for a,b in zip(hi-lo,[210,200,195]))});bpy.data.objects.remove(cp,do_unlink=True)
(O/'engineering_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
txt=bpy.data.texts.new('V4_추정및검증범위');txt.write(json.dumps(report,ensure_ascii=False,indent=2));bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   a=area.spaces.active;a.region_3d.view_location=(0,0,90);a.region_3d.view_distance=440;a.region_3d.view_rotation=Vector((1,1,.6)).to_track_quat('Z','Y');a.region_3d.view_perspective='ORTHO';a.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_통합설계_v4.0_A.blend'))
s.render.resolution_x=1200;s.render.resolution_y=900
def render(n,d,center=(0,0,90),scale=410):
 d=Vector(d).normalized();s.camera.location=Vector(center)+d*1000;s.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(O/(n+'.png'));bpy.ops.render.render(write_still=True)
render('front',(1,1,.6));render('side',(1,0,.12));render('rear',(-1,-1,.6));cover.hide_render=True
for ob in decor:ob.hide_render=True
render('inside',(1,1,1));cover.hide_render=False;cover.location.z+=110;render('exploded',(1,1,.7),(0,0,125),490)
print('REPORT',json.dumps(report,ensure_ascii=False))
