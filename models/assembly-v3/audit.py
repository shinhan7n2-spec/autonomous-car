import bpy,json
from mathutils import Vector
from pathlib import Path
r=Path.cwd();bpy.ops.wm.open_mainfile(filepath=str(r/'models/structure-preview-v2/20261029_자율주행자동차_몸체조립검토_v2.0_A.blend'))
a=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 a.append({'name':o.name,'lo':lo,'hi':hi})
(r/'outputs/20261029_assembly_v3_A/v2_bounds.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
