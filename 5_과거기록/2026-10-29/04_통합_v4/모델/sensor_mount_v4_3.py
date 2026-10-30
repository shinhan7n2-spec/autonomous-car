import bpy, bmesh, math, json, hashlib, array, os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
# v4.3: front sensor/camera pillars, sensor slide-in groove, cover sensor notch, camera deck fixed to shelf.
R=Path(os.environ.get('CAR_ROOT',Path(__file__).resolve().parents[2]))
O=Path(os.environ.get('CAR_OUT',R/'outputs/20261029_sensor_mount_v4_3_A'));O.mkdir(parents=True,exist_ok=True)
SRC=R/'models/assembly-v3/20261029_자율주행자동차_배터리탈착_v4.2_A.blend'
DST=Path(os.environ.get('CAR_BLEND',R/'models/assembly-v3/20261029_자율주행자동차_센서고정_v4.3_A.blend'))
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
refs=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
def digest(o):
 a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
before={n:digest(bpy.data.objects[n]) for n in refs}
blue=bpy.data.materials['차체_블루그레이'];silver=bpy.data.materials['USB금속']
green=bpy.data.materials.new('센서기판_참고');green.diffuse_color=(.1,.45,.25,1)
col=bpy.data.collections.new('V4_3_센서카메라기둥');s.collection.children.link(col)
refcol=bpy.data.collections['V4_추정형상_출력제외']
def link(o,c):
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o)
def cube(n,d,p,m=blue,c=col,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  md=o.modifiers.new('r','BEVEL');md.width=bevel;md.segments=3;bpy.ops.object.modifier_apply(modifier=md.name)
 o.data.materials.append(m);link(o,c);return o
def cyl(n,r,h,p,axis='Z',v=32,m=blue,c=col):
 rot=(math.pi/2,0,0) if axis=='Y' else (0,0,0)
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=h,location=p,rotation=rot);o=bpy.context.object;o.name=n;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);o.data.materials.append(m);link(o,c);return o
def boolean(a,b,op='DIFFERENCE'):
 bpy.context.view_layer.objects.active=a;md=a.modifiers.new('b','BOOLEAN');md.operation=op;md.solver='EXACT';md.object=b;bpy.ops.object.modifier_apply(modifier=md.name);bpy.data.objects.remove(b,do_unlink=True)

# --- Assumptions (HY-SRF05 school-type, to be measured) ---
PCB=dict(w=45,h=21,t=1.6);TX=dict(pitch=26,d=16,length=12)
Z0=79.484130859375                # base plate top
LIFT=6.0                           # camera deck raised so the downward pin header + DuPont plugs fit under the PCB
PCB_Y_BACK,PCB_Y_FRONT=82.7,84.3   # PCB inside groove 82.6..84.4 (existing pillars y 74..86)
PCB_Z=102.0                        # PCB bottom; downward DuPont plugs (~16.5mm) end ~6mm above plate
TXZ=PCB_Z+PCB['h']/2
DECK_Z=119.484130859375+LIFT       # camera deck underside after lift
SHELF_TOP=113.484130859375
base=bpy.data.objects['P01_한장바닥판_190x185x5'];deck=bpy.data.objects['P09_카메라_클립받침'];shelf=bpy.data.objects['P02_분리선반_150x130x4'];cover=bpy.data.objects['P10_해치백덮개']
changed=[base,deck,shelf,cover]
pre=None
bpy.data.objects.remove(bpy.data.objects['P12_센서뒤고정띠'],do_unlink=True)
# Raise camera deck, rear clip and all camera reference shapes together.
camnames=['P09_카메라_클립받침','P13_カメラ_뒤클립누름판']
for o in s.objects:
 if o.name in camnames or o.name.startswith(('REF_카메라','REF_렌즈','REF_본체힌지','REF_뒤접이힌지','REF_볼트머리','REF_M3x20_카메라')):o.location.z+=LIFT
bpy.context.view_layer.update()
for o in [deck,bpy.data.objects['P13_カメラ_뒤클립누름판']]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
# Existing base pillars (x 20..28, y 74..86, to z 119.5): extend 6mm, add locating pegs, cut PCB groove + transducer relief.
for sgn in [-1,1]:
 boolean(base,cube('pillar_ext',(8,12,LIFT),(sgn*24,80,119.484130859375+LIFT/2)),'UNION')
 boolean(base,cyl('peg',2.3,4.0,(sgn*24,80,DECK_Z+2.0)),'UNION')
 g0,g1=sorted([sgn*19.5,sgn*23.0]);boolean(base,cube('pcb_groove',(g1-g0,1.8,DECK_Z-PCB_Z+6),((g0+g1)/2,83.5,(PCB_Z+DECK_Z+6)/2)))
 r0,r1=sorted([sgn*19.5,sgn*21.2]);boolean(base,cube('tx_relief',(r1-r0,2.2,DECK_Z-PCB_Z+6),((r0+r1)/2,85.5,(PCB_Z+DECK_Z+6)/2)))
# Old low sensor ledge centre removed so DuPont plugs and wires pass.
boolean(base,cube('ledge_gap',(20,9,4),(0,88,Z0+1.6)))
# Camera deck pads onto shelf front strip; M3x20 + nut under shelf.
for sgn in [-1,1]:
 boolean(deck,cube('pad',(10,7.5,DECK_Z-SHELF_TOP+.4),(sgn*24,68.25,(SHELF_TOP+DECK_Z)/2+.2)),'UNION')
 boolean(deck,cyl('m3',1.7,24,(sgn*24,68,DECK_Z)))
 boolean(shelf,cyl('m3',1.7,20,(sgn*24,68,SHELF_TOP)))
# Cover: notch open upward so the cover lowers past the transducers.
boolean(cover,cube('sensor_notch',(44,12,30),(0,90,TXZ-10+15)))
old=bpy.data.objects.get('HY_SRF05_PCB_45x21_NO_DEPTH')
if old:bpy.data.objects.remove(old,do_unlink=True)
pcb=cube('REF_HY_SRF05_기판_45x21x1.6_추정',(PCB['w'],PCB['t'],PCB['h']),(0,(PCB_Y_BACK+PCB_Y_FRONT)/2,TXZ),green,refcol)
txs=[cyl(f'REF_HY_SRF05_송수신기_{i}',TX['d']/2,TX['length'],(x,PCB_Y_FRONT+TX['length']/2,TXZ),'Y',48,silver,refcol) for i,x in enumerate([-TX['pitch']/2,TX['pitch']/2])]
hdr=cube('REF_HY_SRF05_핀+듀폰_아래방향_추정',(13,2.6,16.5),(0,83.5,PCB_Z-8.25),silver,refcol)
# ---- Checks ----
def bvh(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);t=BVHTree.FromBMesh(bm);
 nm=sum(1 for e in bm.edges if not e.is_manifold);bm.free();return t,nm
def islands(o):
 bm=bmesh.new();bm.from_mesh(o.data);seen=set();n=0
 for v in bm.verts:
  if v.index in seen:continue
  n+=1;st=[v]
  while st:
   x=st.pop()
   if x.index in seen:continue
   seen.add(x.index);st.extend(e.other_vert(x) for e in x.link_edges)
 bm.free();return n
mesh=[o for o in s.objects if o.type=='MESH' and not o.hide_viewport]
cache={o.name:bvh(o) for o in mesh}
def overlap(a,b):return len(cache[a.name][0].overlap(cache[b.name][0]))
# Pairs that are designed to touch (bolted/seated faces) are reported separately from real interference.
touch={frozenset(p) for p in [(base.name,deck.name),(deck.name,shelf.name),(base.name,pcb.name)]}
baseline=set(json.loads(os.environ.get('BASELINE','[]')) and [frozenset(x) for x in json.loads(os.environ['BASELINE'])])
report={'version':'v4.3','status':'design review; not machine-ready','assumptions':{'pcb_mm':PCB,'transducer_mm':TX,'header':'5-pin straight down, breadboard type (assumed, to confirm)','transducer_center_z':TXZ,'sensor_insert':'slide PCB down into pillar grooves BEFORE fitting camera deck'},
 'fasteners_new':{'M3x20+M3 nut (deck to shelf)':2},'camera_deck_lift_mm':LIFT,'parts':{},'interference':[],'designed_contacts':[],'preexisting_contact_in_v4_2':[]}
for o in changed:
 report['parts'][o.name]={'non_manifold_edges':cache[o.name][1],'islands':islands(o),'dims_mm':[round(v,2) for v in o.dimensions]}
for a in changed+[bpy.data.objects['P13_カメラ_뒤클립누름판']]+[o for o in s.objects if o.name.startswith('REF_카메라')]+[pcb]+txs+[hdr]:
 for b in mesh+[pcb]+txs+[hdr]:
  if a is b or b.name.startswith('REF_HY') and a.name.startswith('REF_HY'):continue
  if b.name not in cache:cache[b.name]=bvh(b)
  if a.name not in cache:cache[a.name]=bvh(a)
  n=overlap(a,b)
  if n:
   key=frozenset((a.name,b.name));rec={'a':a.name,'b':b.name,'tri_pairs':n}
   (report['designed_contacts'] if key in touch else report['preexisting_contact_in_v4_2'] if key in baseline else report['interference']).append(rec)
# de-duplicate symmetric pairs
def dedup(l):
 seen=set();out=[]
 for r in l:
  k=frozenset((r['a'],r['b']))
  if k not in seen:seen.add(k);out.append(r)
 return out
report['interference']=dedup(report['interference']);report['preexisting_contact_in_v4_2']=dedup(report['preexisting_contact_in_v4_2']);report['designed_contacts']=dedup(report['designed_contacts'])
# Transducer clear path forward (rays from transducer centres must leave the car).
clear={}
for t in txs:
 x=t.location.x;hit=None
 for o in mesh:
  if o.name.startswith('REF_'):continue
  inv=o.matrix_world.inverted();r=o.ray_cast(inv@Vector((x,PCB_Y_FRONT+.1,TXZ)),inv.to_3x3()@Vector((0,1,0)),distance=300)
  if r[0]:hit=o.name
 clear[t.name]=hit is None
report['transducer_forward_clear']=clear
report['reference_geometry_unchanged']={n:before[n]==digest(bpy.data.objects[n]) for n in refs}
(O/'sensor_mount_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=1),encoding='utf-8')
for o in changed:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.wm.stl_export(filepath=str(O/f'{o.name}.stl'),export_selected_objects=True,apply_modifiers=True)
bpy.ops.wm.save_as_mainfile(filepath=str(DST),copy=True)
print(json.dumps(report,ensure_ascii=False)[:3000])
