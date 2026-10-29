import bpy,bmesh,json,hashlib,array
from pathlib import Path
r=Path.cwd();out=r/'outputs/20261029_assembly_v3_A'
names=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
def digest(o):
 a=array.array('f',[0.0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(r/'models/assembly-v3/20261029_자율주행자동차_원본배율검토_v3.0_A.blend'));old={n:digest(bpy.data.objects[n]) for n in names}
bpy.ops.wm.open_mainfile(filepath=str(r/'models/assembly-v3/20261029_자율주행자동차_한장차체조립_v3.1_A.blend'))
checks={'full_vertex_hash_matches':{n:old[n]==digest(bpy.data.objects[n]) for n in names},'structure_meshes':[]}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not any(c.name.startswith('V3_') for c in o.users_collection):continue
 bm=bmesh.new();bm.from_mesh(o.data);checks['structure_meshes'].append({'name':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':abs(bm.calc_volume()),'dimensions':list(o.dimensions)});bm.free()
(out/'mesh_validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(checks,ensure_ascii=False))
