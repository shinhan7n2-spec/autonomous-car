import bpy,bmesh,json
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out51/v51.blend');s=bpy.context.scene
import os;os.makedirs('/home/claude/w/final',exist_ok=True)
rows=[]
for o in sorted(s.objects,key=lambda o:o.name):
  if o.type=='MESH' and o.name[:1]=='P' and o.name[1:3].isdigit():
    bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume());nm=sum(1 for e in bm.edges if not e.is_manifold);bm.free()
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    fn=o.name.replace('.','_')+'.stl';bpy.ops.wm.stl_export(filepath='/home/claude/w/final/'+fn,export_selected_objects=True)
    rows.append([fn,[round(x,1) for x in o.dimensions],round(v/1000,1),nm])
for r in rows:print(r)
json.dump(rows,open('/home/claude/w/final/parts_manifest.json','w'),ensure_ascii=False,indent=1)
