import bpy,bmesh,math,json,os
from mathutils import Matrix,Vector
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v63.blend');s=bpy.context.scene
OUT='/home/claude/w/print';os.makedirs(OUT,exist_ok=True)
X=lambda a:Matrix.Rotation(math.radians(a),4,'X');Y=lambda a:Matrix.Rotation(math.radians(a),4,'Y')
rot={'P07':X(90),'P06':X(180),'P09':Y(90),'P10':X(180),'P14':X(90),'P04_배터리':X(90)}
def ov(bm):
  z0=min(v.co.z for v in bm.verts);return sum(f.calc_area() for f in bm.faces if f.normal.z<-0.75 and f.calc_center_median().z>z0+0.3)/100
rows=[]
for o in sorted(s.objects,key=lambda o:o.name):
  if not(o.type=='MESH' and o.name[:1]=='P' and o.name[1:3].isdigit()):continue
  R=next((m for k,m in rot.items() if o.name.startswith(k)),Matrix.Identity(4))
  bm=bmesh.new();bm.from_mesh(o.data);bm.transform(R@o.matrix_world)
  if o.name.startswith('P02'):
    b2=bm.copy();bmesh.ops.transform(b2,matrix=X(180),verts=b2.verts);print('P02 as-modeled',round(ov(bm),1),'flipped',round(ov(b2),1));b2.free()
  mn=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);mx=Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
  bmesh.ops.translate(bm,verts=bm.verts,vec=(-(mn.x+mx.x)/2,-(mn.y+mx.y)/2,-mn.z))
  me=bpy.data.meshes.new('t');bm.to_mesh(me);ovv=ov(bm);bm.free()
  t=bpy.data.objects.new('t_'+o.name,me);s.collection.objects.link(t)
  bpy.ops.object.select_all(action='DESELECT');t.select_set(True);bpy.context.view_layer.objects.active=t
  fn=o.name.replace('.','_')+'.stl';bpy.ops.wm.stl_export(filepath=f'{OUT}/{fn}',export_selected_objects=True)
  rows.append({'file':fn,'print_size_mm':[round(v,1) for v in (mx-mn)],'steep_overhang_cm2':round(ovv,1)})
  bpy.data.objects.remove(t)
for r in rows:print(r)
json.dump(rows,open(f'{OUT}/print_manifest.json','w'),ensure_ascii=False,indent=1)
