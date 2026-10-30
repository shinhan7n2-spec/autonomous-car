import bpy, bmesh, math, json, os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
# v5.0 cover: lift-off on 4 pins, flat roof printed roof-down (minimal support), 2.4mm wall.
R=Path(os.environ.get('CAR_ROOT',Path(__file__).resolve().parents[2]))
SRC=Path(os.environ.get('CAR_SRC',R/'models/assembly-v3/20261029_자율주행자동차_센서고정_v4.3_A.blend'))
O=Path(os.environ.get('CAR_OUT',R/'outputs/20261029_cover_v5_0_A'));O.mkdir(parents=True,exist_ok=True)
DST=Path(os.environ.get('CAR_BLEND',R/'models/assembly-v3/20261029_자율주행자동차_들어올림덮개_v5.0_A.blend'))
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
blue=bpy.data.materials['차체_블루그레이']
Z0=79.484130859375;TOP=162.0;CH=14.0;WALL=2.4
HX,Y0,Y1,RC=87.5,-91.0,92.0,18.0
def ring(inset,z,n=8):
 hx=HX-inset;y0=Y0+inset;y1=Y1-inset;r=max(RC-inset,2.0);pts=[]
 for cx,cy,a0 in [(hx-r,y1-r,0),(-hx+r,y1-r,90),(-hx+r,y0+r,180),(hx-r,y0+r,270)]:
  for k in range(n+1):
   a=math.radians(a0+90*k/n);pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
 return pts
def loft(name,stations):
 v=[];m=None
 for inset,z in stations:
  p=ring(inset,z);m=len(p);v.extend(p)
 f=[tuple(range(m))[::-1],tuple(range(m*(len(stations)-1),m*len(stations)))]
 for i in range(len(stations)-1):
  for j in range(m):f.append((i*m+j,i*m+(j+1)%m,(i+1)*m+(j+1)%m,(i+1)*m+j))
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(blue);return o
def cube(n,d,p,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  md=o.modifiers.new('r','BEVEL');md.width=bevel;md.segments=3;bpy.ops.object.modifier_apply(modifier=md.name)
 return o
def cyl(n,r,h,p,v=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=h,location=p);o=bpy.context.object;o.name=n;return o
def boolean(a,b,op='DIFFERENCE'):
 bpy.context.view_layer.objects.active=a;md=a.modifiers.new('b','BOOLEAN');md.operation=op;md.solver='EXACT';md.object=b;bpy.ops.object.modifier_apply(modifier=md.name);bpy.data.objects.remove(b,do_unlink=True)

for n in ['P10_해치백덮개','장식_헤드램프_부품추가아님','장식_헤드램프_부품추가아님.001']:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
cover=loft('P10_들어올림덮개_v5',[(0,Z0),(0,TOP-CH),(CH,TOP)])
inner=loft('inner',[(WALL,Z0-1),(WALL,TOP-CH-1),(CH+WALL*.6,TOP-WALL)])
boolean(cover,inner)
# Wheel arches (open at the bottom edge), same envelope as v4.
for sx in [-1,1]:boolean(cover,cube('arch',(24,112,33),(sx*88,-48,85),4))
# Front: full-height centre opening (x+-42) so the cover lifts straight up past sensor, camera deck and camera.
boolean(cover,cube('front_open',(84,24,260),(0,92,Z0)))
# Camera: opening through roof and upper front so the camera parts pass while lifting.
boolean(cover,cube('camera_open',(82,70,80),(0,52+35,123+40),3))
# Rear: battery slide-out opening (kept from v4.2) and cable gap.
boolean(cover,cube('rear_service_opening',(150,46,2*(110.3-Z0)),(-5,-80,Z0)))
# Vents (short bridges when printed roof-down).
for xx in [-39,-21,-3,15,33,51]:boolean(cover,cube('roof_vent',(5,40,10),(xx,-12,TOP)))
for sx in [-1,1]:
 for yy in [24,40,56]:boolean(cover,cube('side_vent',(10,8,14),(sx*HX,yy,135),1))
# Lift-off pins into existing base holes (+-73,-82)/(+-73,83): feet + 3.6mm pins, no tools.
for xx in [-73,73]:
 for yy in [-82,83]:
  foot=cube('foot',(14,18,5),(xx,yy,Z0+2.5)) if yy>0 else cube('foot',(14,10.1,5),(xx,-83.55,Z0+2.5));boolean(cover,foot,'UNION')
  boolean(cover,cyl('pin',1.8,4.2,(xx,yy,Z0-2.1)),'UNION')
bm=bmesh.new();bm.from_mesh(cover.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cover.data);bm.free()

# ---- checks: static fit, lift sweep, mesh, print ----
def tree(o,dz=0):
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
 if dz:bmesh.ops.translate(bm,verts=bm.verts,vec=(0,0,dz))
 t=BVHTree.FromBMesh(bm);bm.free();return t
others=[o for o in s.objects if o.type=='MESH' and o!=cover and not o.hide_viewport]
T={o.name:tree(o) for o in others}
static=[n for n,t in T.items() if tree(cover).overlap(t)]
sweep={}
for dz in range(2,131,2):
 tc=tree(cover,dz);hit=[n for n,t in T.items() if tc.overlap(t)]
 if hit:sweep[dz]=hit
bm=bmesh.new();bm.from_mesh(cover.data);nm=sum(1 for e in bm.edges if not e.is_manifold);vol=abs(bm.calc_volume())
# print roof-down: overhang = faces pointing up in model (they face down when flipped), excluding roof underside region
ov=sum(f.calc_area() for f in bm.faces if f.normal.z>0.7 and f.calc_center_median().z<TOP-WALL-0.5 and f.calc_center_median().z>Z0+5.5)
bm.free()
rep={'version':'v5.0','status':'design review; not machine-ready','mount':'4 printed pins into base holes, lift straight up, no tools',
 'print':{'orientation':'roof down on bed','dims_mm':[round(x,1) for x in cover.dimensions],'bed_3dwox1':[210,200,195],'overhang_cm2_roof_down':round(ov/100,1),'volume_cm3':round(vol/1000,1)},
 'non_manifold_edges':nm,'static_contacts':static,'lift_sweep_collisions':sweep}
(O/'cover_v5_checks.json').write_text(json.dumps(rep,ensure_ascii=False,indent=1),encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT');cover.select_set(True);bpy.context.view_layer.objects.active=cover
bpy.ops.wm.stl_export(filepath=str(O/'P10_들어올림덮개_v5.stl'),export_selected_objects=True)
bpy.ops.wm.save_as_mainfile(filepath=str(DST),copy=True)
print(json.dumps(rep,ensure_ascii=False))
