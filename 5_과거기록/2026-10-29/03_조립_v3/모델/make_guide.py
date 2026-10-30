from pathlib import Path
import json,html,zipfile
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_assembly_v3_3_A'
a=json.loads((O/'manufacturing_checks.json').read_text(encoding='utf8'))
parts=''.join(f'<tr><td>{html.escape(p["file"])}</td><td>{" × ".join(f"{v:.1f}" for v in p["export_bbox_mm"])}</td><td>1</td></tr>' for p in a['parts'])
body='''<h1>자율주행 자동차 v3.3 — PLA 기준 조립·출력 준비</h1>
<p>2026-10-29 / 기기 A · 제공 부품 STL 원본 크기 유지</p>
<aside><b>출력 확정 전 자료입니다.</b> STL 9개와 U자 받침 형상은 생성·검사했습니다. 하지만 실제 모터 끼움, 캐스터 구멍, 보드·카메라 고정 상세와 슬라이서 검사가 남았습니다. 재료를 PLA로 선택했지만 예약 장비의 실제 카트리지는 미확인입니다. 이 자료만으로 전체 부품을 바로 출력하도록 권하지 않습니다. G-code는 포함하지 않습니다.</aside>
<img src="assembly.png" alt="전체 조립 모습">
<h2>1. 출력 부품과 크기</h2><p>아래 크기는 STL에 저장한 출력 방향 기준입니다. 각 1개씩, 총 9개입니다. 바닥판 두께는5mm이지만 기둥을 포함한 출력 높이는45mm입니다. STL 단위는mm, 배율100%를 유지합니다. 지급품 STL은 출력 대상에 포함하지 않았습니다.</p>
<table><tr><th>파일</th><th>가로×세로×높이(mm)</th><th>수량</th></tr>PARTS</table>
<h2>2. 금속 부품 준비표</h2>
<table><tr><th>용도</th><th>예상 부품</th><th>상태</th></tr>
<tr><td>모터 받침2세트</td><td>M4×20 볼트8개, M4너트8개</td><td>설계상 예상. 머리·와셔·물림 길이 대조 필요</td></tr>
<tr><td>배터리 가로대2개</td><td>M3×10 볼트4개, M3너트4개</td><td>추정. 측면 포켓에 너트 삽입</td></tr>
<tr><td>선반</td><td>M4×30mm 지지대4개, 체결 볼트</td><td>지지대 수/암 형식과 암나사 깊이로 볼트 길이 결정</td></tr>
<tr><td>캐스터</td><td>M5 볼트·너트 각4개</td><td>수업 제공 M5×10이 바닥판과 실제 장착판을 통과할 길이인지 확인</td></tr>
<tr><td>휠·커플링</td><td>지급 M4×12 및 M3×8, 커플링2개</td><td>수업 부품 사용. 모터 고정용 볼트와 구분</td></tr>
<tr><td>카메라</td><td>지급 M6×20</td><td>카메라 내부 나사산과 유효 깊이는 별도 확인</td></tr></table>
<p>공용 세트에 있는 규격이라고 해서 수량까지 확보됐다고 판단하지 않았습니다. 인쇄한 볼트는 사용하지 않습니다.</p>
<h2>3. 모터 받침 조립</h2><img src="motor_exploded.png" alt="모터 받침 분해 모습">
<ol><li>U자 받침의 열린 홈을 위로 향하게 놓습니다. 그림은 차체 장착 방향이라 홈이 아래를 향합니다.</li><li>측면 너트 포켓에 M4너트를 넣습니다. 모터 하나당 상부 체결2개, 하부 평판 체결2개입니다.</li><li>모터 원통을 V홈에 놓고 평판을 덮습니다. 평판 양쪽 M4×20을 번갈아 조여 한쪽만 기울지 않게 합니다.</li><li>평판이 모터를 잡기 전에 받침에 닿거나, 모터가 돌아가거나, 과도한 힘이 필요한 경우 고정 치수가 맞지 않는 것입니다. 현재 끼움은 실측 확정 전입니다.</li><li>받침을 바닥판 아래에 대고 위에서 M4×20으로 고정합니다. 볼트 머리와 배터리 밑면 간섭을 확인해야 합니다.</li><li>커플링과 좌L·우R 휠을 장착합니다. 모터 축선과 휠 중심이 맞는지 확인합니다. Blender의 반대편 휠은 복제 STL이므로 실제 좌우 롤러 방향을 나타내지 못합니다.</li></ol>
<h2>4. 자동차 조립 순서</h2><ol>
<li>바닥판 아래 모터 받침과 캐스터를 먼저 장착합니다. 캐스터 슬롯 중심38×28mm는 추정값이므로 실제 구멍과 대조합니다.</li>
<li>손으로 바퀴와 캐스터를 돌려 차체·볼트에 걸리는지 확인합니다. 현재 캐스터 회전 전체 범위는 미검증입니다.</li>
<li>배터리 가로대 기둥의 측면 포켓에 M3너트를 넣고, 배터리를 옆턱·앞뒤 턱 안에 놓습니다. 가로대는 배터리를 압착하지 않도록1mm 여유를 둔 제안입니다.</li>
<li>지지대4개와 상부 선반을 설치합니다. 배터리를 교체할 때는 선반을 먼저 분리한 뒤 가로대를 풉니다.</li>
<li>라즈베리파이와 드라이버를 배치합니다. 측면 가이드·장착 슬롯은 있지만 탈락을 방지하는 보드 체결 상세는 아직 미완성입니다. 올려놓기만 한 상태로 주행하지 않습니다.</li>
<li>전방 센서·카메라를 고정합니다. 카메라 본체는 모델에 없고 받침만 있습니다. 센서 커넥터·카메라 고정 구멍 대조 전입니다.</li>
<li>배선을 통로로 정리합니다. 주황색 선은 공간 검토용 경로이며 전기 회로도가 아닙니다. 실제 전기 연결은 수업 회로를 따릅니다.</li></ol>
<h2>5. 3DWOX1 / PLA 출력 준비</h2><p>3DWOX1 출력 한계210×200×195mm. 바닥판190×185mm는 크기상 들어갑니다. 브림5mm를 사방에 추가하면 약200×195mm이지만 실제 슬라이서의 금지 영역·서포트·시작선을 포함해 확인해야 합니다.</p>
<ul><li>바닥판·선반·평판·가로대: 넓고 평평한 면이 바닥에 닿도록 STL을 내보냈습니다.</li><li>U자 받침: 옆면이 바닥에 닿도록 회전한 STL입니다. 막힌 수평 원형 구멍을 없앴지만 너트 포켓 내부의 지지 필요성은 별도 확인해야 합니다.</li><li>슬라이서에서 3DWOX1과 실제 PLA 카트리지를 선택합니다. 2X의 카트리지 번호 주의사항을 그대로 적용하는 모델은 아닙니다.</li><li>층0.2mm·벽4줄·상하5층·채움30%는 검토 시작값 제안일 뿐 검증된 출력 프로필이 아닙니다. 온도·냉각·속도는 장비의 공식 PLA 프로필과 실제 필라멘트에 맞춥니다.</li><li>레이어 미리보기에서 떠 있는 첫 층, 너트 자리의 천장, 서포트 제거 접근성, 출력 시간을 확인한 뒤 G-code를 생성합니다.</li></ul>
<h2>6. 추정과 검사 범위</h2><p>모터 명목 지름22mm 참고, V홈90°, M4관통5mm, 너트 포켓8.2×3.8mm. 형상·배치 추정이므로 실제 끼움 보증이 아닙니다. 원본 STL은 수정하지 않았습니다.</p><p>9개 출력부품 모두 열린/비다양체 모서리0, 연결체1개, 개별 출력 크기 범위 내. 참고 STL8개 객체 전체 정점 해시 일치. 실제 강도·축 정렬·정밀 간섭·주행·슬라이싱 검증을 의미하지 않습니다.</p>
<h2>다음 확정에 필요한 항목</h2><p>① 실제 PLA 및 슬라이서 확인 ② 모터 축·끼움과 캐스터 고정 패턴 확인 ③ 카메라·보드의 탈락 방지 고정 완성 ④ 전체 배선·볼트 접근 검사. 이 항목이 끝나야 출력 확정본으로 안내할 수 있습니다.</p>
'''.replace('PARTS',parts)
style='body{font-family:Malgun Gothic,sans-serif;color:#203746;line-height:1.75;max-width:1040px;margin:32px auto;padding:20px}h1,h2{color:#145764}aside{padding:18px;background:#fff0d0;border-left:5px solid #bd8221}img{width:100%;max-height:650px;object-fit:contain}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #bacbd2;padding:8px;text-align:left}@media print{body{font-size:10pt;margin:0}img{max-height:95mm}h2{break-after:avoid}tr{break-inside:avoid}}'
(O/'20261029_자율주행자동차_조립안내_v3.3_A.html').write_text('<!doctype html><meta charset="utf-8"><title>v3.3 조립·출력 준비</title><style>'+style+'</style>'+body,encoding='utf8')
(O/'출력전_확인.txt').write_text('PLA 기준 조립·출력 준비 자료. G-code 없음. 슬라이싱과 모터/캐스터/보드/카메라 체결 확정 미완료. 최종 출력 승인본이 아닙니다. HTML 설명서를 먼저 읽으세요.',encoding='utf8')
with zipfile.ZipFile(O/'20261029_자율주행자동차_STL조립자료_v3.3_A.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file() and p.suffix!='.zip':z.write(p,p.relative_to(O))
print('Guide and archive saved; files:',len(a['parts']))
