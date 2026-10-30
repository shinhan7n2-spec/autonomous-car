import bpy, math, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_assembly_v3_A';D=O/'STL_REVIEW_출력확정전';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/assembly-v3/20261029_자율주행자동차_한장차체조립_v3.1_A.blend'))
s=bpy.context.scene
# The second reference uses rotation only so its protruding hub faces inwards.
# This still does not manufacture the missing opposite-handed roller mesh.
bpy.data.objects['Wheel_Right_REFERENCE_ONLY'].rotation_euler.y=-math.pi/2
rename={'P04_BANK_着脱固定バー':'P04_보조배터리_고정가로대','P04_LIPO_着脱固定バー':'P05_리포배터리_고정가로대'}
for a,b in rename.items():bpy.data.objects[a].name=b
parts=[o for o in s.objects if o.type=='MESH' and o.name.startswith('P') and any(c.name.startswith('V3_') for c in o.users_collection)]
manifest=[]
for i,o in enumerate(sorted(parts,key=lambda o:o.name),1):
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.name='EXPORT_ONLY'
 bpy.context.view_layer.update();pts=[c.matrix_world@Vector(v) for v in c.bound_box];lo=Vector([min(p[k] for p in pts) for k in range(3)]);hi=Vector([max(p[k] for p in pts) for k in range(3)])
 c.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 bpy.ops.object.select_all(action='DESELECT');c.select_set(True);bpy.context.view_layer.objects.active=c
 fname=f'{i:02d}_{o.name}_REVIEW.stl'
 bpy.ops.wm.stl_export(filepath=str(D/fname),export_selected_objects=True,apply_modifiers=True,global_scale=1.0,use_scene_unit=False)
 manifest.append({'file':fname,'object':o.name,'bbox_mm':list(hi-lo),'status':'REVIEW ONLY - not cleared for printing','units':'mm; numeric STL coordinates unchanged, no automatic scale conversion'})
 bpy.data.objects.remove(c,do_unlink=True)
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
txt=bpy.data.texts.new('V3_2_출력파일주의');txt.write('개별 STL은 REVIEW 폴더에 있음. 모터 보어29mm는 스캔 외곽 회피치수로 실제22mm 모터를 단단히 잡는 최종 끼움이 아님. 캐스터 슬롯38x28은 추정. 카메라/보드 체결 상세 미완성. 최종 출력 승인 전. 우측 휠은 회전으로 허브를 안쪽으로 배치했으나 실제 우측 롤러형상 아님.')
path=R/'models/assembly-v3/20261029_자율주행자동차_한장차체조립_v3.2_A.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
def render(name):
 s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
d=Vector((1,1,.85)).normalized();s.camera.location=Vector((0,0,75))+d*1000;s.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=390
render('v3_assembled_final')
old={o:o.location.copy() for o in s.objects if o.type in ['MESH','CURVE']}
for o in list(s.objects):
 if o.name.startswith('P02_'):o.location.z+=65
 if o.name in ['라즈베리','L298N_43x43x27_SPEC_ENVELOPE']:o.location.z+=105
 if o.name.startswith(('P04_','P05_')):o.location.z+=35
 if o.name.startswith('P09_'):o.location.z+=45
 if o.name.startswith(('P06_','P07_')):o.location.z-=35 if o.name.startswith('P06_') else 60
 if o.name=='캐스터 휠':o.location.z-=65
 if o.type=='CURVE':o.hide_render=True
s.camera.data.ortho_scale=480;render('v3_exploded')
print('PACKAGED',len(manifest),'STL files; saved assembled file',str(path))
