import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2]
O=R/'outputs/20261029_integrated_v4_A'
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_통합설계_v4.0_A.blend'))
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)]]
def tree(o):
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],all_triangles=False)
c=bpy.data.objects['P10_해치백덮개'];cb=bounds(c);ct=tree(c);result=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o==c or not (o.name.startswith(('P','REF_')) or o.name in ['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']):continue
 b=bounds(o)
 if any(b[1][k]<cb[0][k] or b[0][k]>cb[1][k] for k in range(3)):pairs=0
 else:pairs=len(ct.overlap(tree(o)))
 result.append({'object':o.name,'cover_surface_intersection_pairs':pairs,'bounds':b})
import bmesh
volumes={}
for name in ['P01_한장바닥판_190x185x5','P02_분리선반_150x130x4']:
 cp=c.copy();cp.data=c.data.copy();bpy.context.scene.collection.objects.link(cp);bpy.context.view_layer.objects.active=cp
 md=cp.modifiers.new('volume_test','BOOLEAN');md.operation='INTERSECT';md.solver='EXACT';md.object=bpy.data.objects[name];bpy.ops.object.modifier_apply(modifier=md.name)
 bm=bmesh.new();bm.from_mesh(cp.data);volumes[name]=abs(bm.calc_volume());bm.free();bpy.data.objects.remove(cp,do_unlink=True)
(O/'cover_interference_audit.json').write_text(json.dumps({'method':'world-coordinate triangle surface intersection; touching also counted; containment and motion not tested','cover_intersection_volume_mm3':volumes,'results':result},ensure_ascii=False,indent=2),encoding='utf8')
print('INTERSECTION_VOLUMES',volumes)
print(json.dumps([{'object':v['object'],'pairs':v['cover_surface_intersection_pairs']} for v in result],ensure_ascii=False))
