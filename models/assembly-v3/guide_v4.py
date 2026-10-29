from pathlib import Path
import json,html,zipfile
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];O=R/'outputs/20261029_integrated_v4_A'
a=json.loads((O/'engineering_report.json').read_text(encoding='utf8'))
f=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
canvas=Image.new('RGB',(1600,1280),'white');d=ImageDraw.Draw(canvas)
for i,(name,label) in enumerate([('front','덮개 장착 · 카메라 외형 추정'),('rear','후면 · 지붕/측면 통풍구'),('inside','덮개 제거 · 제공 부품 원본 크기'),('exploded','덮개 분리 · 체결 위치 검토')]):
 im=Image.open(O/(name+'.png')).convert('RGB');im.thumbnail((800,600));x=(i%2)*800;y=(i//2)*640;canvas.paste(im,(x,y+40));d.text((x+20,y+8),label,fill='black',font=f)
canvas.save(O/'preview.png')
rows=''.join('<tr><td>'+html.escape(p['file'])+'</td><td>'+' × '.join(f'{x:.1f}' for x in p['size_mm'])+'</td></tr>' for p in a['parts'])
body='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>v4 통합 모델 검토 안내</title><style>body{font-family:Malgun Gothic,sans-serif;max-width:1080px;margin:40px auto;line-height:1.7;color:#21313b}img{width:100%}aside{background:#fff3d8;padding:20px}table{border-collapse:collapse;width:100%}td,th{padding:8px;border:1px solid #ccd5db}h2{margin-top:36px}</style>
<h1>자율주행 자동차 v4.0 · 통합 모델 검토</h1><p>2026-10-29 / A · PLA 설계 기준 · 3DWOX 1</p>
<aside>이 파일은 조립 순서와 추정 치수를 검토하는 자료입니다. 전체 출력 승인본이 아닙니다. 센서 뒤 고정띠의 체결 상세, 카메라 실제 고정 방식, 모터 축 정렬과 슬라이싱이 아직 확정되지 않았습니다. 메시가 닫혀 있고 베드에 들어간다는 검사만으로 출력·조립 성공을 보장하지 않습니다.</aside>
<img src="preview.png"><h2>랜카드 형상과 추정값</h2>
<p>부품표의 ipTIME A1000mini를 기준으로 내장 안테나형 USB 동글을 표현했습니다. A1000mini-UA 외장 안테나 제품과 구분합니다. 본체 24.6×16×8mm는 정확한 모델 치수로 검증하지 못한 임시값이며, USB 연결 후 돌출 공간은 30mm를 가정했습니다. 포트 위치도 제공된 라즈베리파이 외곽 STL을 기준으로 추정했습니다. 이 형상은 출력 대상이 아닙니다.</p>
<p><a href="https://contents.iptime.co.kr/~contents/link/diff_prd_180726.pdf">제조사 제품 비교표</a> · <a href="https://www.kwshop.co.kr/goods/view?no=6540">A1000mini 제품 자료</a></p>
<h2>조립 순서안</h2><ol>
<li>바닥판 아래에 모터 U자 받침을 고정하고 모터를 V홈에 놓습니다. 평판을 대고 양쪽 볼트를 조금씩 교대로 조입니다. 스캔의 축 기울기와 실제 끼움은 검증되지 않았으므로 억지로 조이지 않습니다.</li>
<li>지급 커플링과 두 휠을 장착합니다. 2개 구동휠과 1개 캐스터 구성으로, 4개 메카넘휠의 옆 이동을 전제로 하지 않습니다.</li>
<li>캐스터를 바닥판 슬롯에 고정합니다. 38×28mm 구멍 간격은 추정이며, 회전할 때 배선·모터와 닿지 않는지 실물에서 확인해야 합니다.</li>
<li>보조배터리와 리포배터리를 턱 안에 놓고 각 가로대로 빠짐을 막습니다. 가로대는 배터리를 찌그러뜨리는 압착구가 아닙니다. 스트랩·접착제는 추가하지 않았습니다.</li>
<li>배터리 전선을 먼저 통과시키고 M4 30mm 지지대 위에 선반을 조립합니다. 케이블 끝과 커넥터 치수는 아직 추정입니다.</li>
<li>라즈베리파이와 드라이버를 배치합니다. 위 고정편은 외곽 형상 기준의 빠짐 방지 시안이며 실제 보드 소자와 포트에 닿는지 별도 확인이 필요합니다.</li>
<li>전방 센서와 카메라를 설치합니다. 센서 뒤 고정띠는 체결 상세가 미완료입니다. 카메라 M6×20은 수업 제공 규격이며 카메라 자체에 M6 나사산이 있다는 뜻으로 확정하지 않았습니다.</li>
<li>랜카드와 USB 케이블을 연결한 뒤 덮개를 얹고 네 체결부를 맞춥니다. 덮개 체결은 M3×16 볼트·M3 너트 각4개 기준이며 지급 공용 세트의 실제 수량을 확인해야 합니다.</li></ol>
<h2>출력 파일 및 방향</h2><p>STL_슬라이서검사전 폴더는 새로 설계한 부품만 포함합니다. 수업 원본 STL은 포함하지 않았습니다. 단위 mm, 배율100%입니다. 아래 크기는 파일에 저장한 출력 방향의 외곽 크기입니다.</p>
<table><tr><th>파일 · 각1개</th><th>외곽 크기(mm)</th></tr>ROWS</table>
<p>바닥판·선반·평판은 넓은 면을 아래로, U받침은 옆면을 아래로 내보냈습니다. 덮개는 지붕이 아래인 후보 방향입니다. 경사면·개구·너트 포켓에는 지지대가 필요할 수 있어 슬라이서에서 층별 경로를 확인해야 합니다. 210×200×195mm 범위 검사는 브림과 노즐 이동 여유를 포함하지 않습니다.</p>
<h2>통신·발열 검사 범위</h2><p>랜카드 쪽 개구, 하부 흡기와 지붕/측면 통풍구를 모델링했습니다. 새 팬이나 별도 안테나를 추가하지 않았습니다. 전파 세기·실제 온도·팬 흡배기 방향·주행 성능은 시험하지 않았습니다.</p>
<h2>검사 근거와 남은 조건</h2><p>engineering_report.json: 원본파일6개와 참고 메시8개의 해시, 배율1, 출력부품 연결성·닫힘·외곽 크기. cover_interference_audit.json: 덮개 표면과 다른 메시의 교차 검사. 면 접촉도 검출되며 내부 포함과 회전 궤적을 판정하는 검사는 아닙니다.</p>
<p>실제 장비 카트리지·프린터 프로필과 슬라이서가 확인되지 않아 G-code는 없습니다. 본 ZIP의 STL은 검사 전 작업본입니다. 카메라·센서 체결 미완료 상태를 숨기고 바로 출력 가능한 최종본으로 표시하지 않았습니다.</p></html>'''.replace('ROWS',rows)
(O/'20261029_자율주행자동차_통합검토안내_v4.0_A.html').write_text(body,encoding='utf8')
with zipfile.ZipFile(O/'20261029_자율주행자동차_통합검토자료_v4.0_A.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file() and p.suffix in ['.stl','.json','.html','.png']:z.write(p,p.relative_to(O))
print('Guide, preview and review ZIP saved; not a print release.')
