import bpy,json
from pathlib import Path
r=Path.cwd();bpy.ops.wm.open_mainfile(filepath=str(r/'models/structure-preview-v2/20261029_자율주행자동차_몸체조립검토_v2.0_A.blend'))
names=['라즈베리','리포배터리','보조배터리','모터','Motor_Right','메카넘휠','Wheel_Right_REFERENCE_ONLY','캐스터 휠']
report=[]
for n in names:
 o=bpy.data.objects[n];old=list(o.scale);o.scale=(1,1,1);o['scale_policy']='Original STL size only. Translation and rotation allowed. No reference rescaling.'
 report.append({'object':n,'previous_scale':old,'scale':list(o.scale)})
t=bpy.data.texts.new('v3_원본배율_복원_검사중');t.write('사용자 지시로 제공 STL 배율을 모두 1로 복원. v2 원본 보존. 위치/회전 유지. 이 파일은 원본 크기로 되돌린 검사 시작점이며 기존 받침과 높이가 맞지 않음. 출력 금지. 체결 설계 및 간섭 수정 미완료.')
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/assembly-v3/20261029_자율주행자동차_원본배율검토_v3.0_A.blend'))
(r/'outputs/20261029_assembly_v3_A/scale_restoration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('All reference scales restored:',all(tuple(bpy.data.objects[n].scale)==(1,1,1) for n in names))
