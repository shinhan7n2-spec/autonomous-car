from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/20261029_structure_v2_A'
def font(n): return ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',n)
def board(filename,title,tiles,cols,notes):
    width=1800; tw=width//cols; th=620 if cols==2 else 480
    height=140+th*((len(tiles)+cols-1)//cols)+145
    im=Image.new('RGB',(width,height),'#f4f6fa'); d=ImageDraw.Draw(im)
    d.text((30,20),title,font=font(38),fill='#19364a')
    d.text((30,78),'구조·배치 검토용 제안 | 실제 제공 STL + 새 몸체 | 출력용 확정 모델 아님',font=font(24),fill='#536575')
    for i,(src,label) in enumerate(tiles):
        x=i%cols*tw;y=140+i//cols*th
        d.text((x+20,y),label,font=font(26),fill='#19364a')
        p=Image.open(OUT/(src+'.png')).convert('RGB');p.thumbnail((tw-16,th-50))
        im.paste(p,(x+(tw-p.width)//2,y+44))
    y=height-135
    for line in notes:
        d.text((30,y),line,font=font(23),fill='#435b6b');y+=33
    im.save(OUT/filename)
board('20261029_자율주행자동차_조립프리뷰_v2.0_A.png','둥근 몸체 A안 · 조립과 내부 구조',[
 ('front_iso','① 조립 상태 | 앞쪽 센서·카메라 받침'),
 ('exploded','② 분해도 | 조립 관계를 보이도록 벌림'),
 ('lower','③ 아래층 | 배터리·모터 드라이버 배치'),
 ('structure','④ 구조물만 | 바닥판·선반·고정대')],2,[
 '크림색: 둥근 바닥판 / 청록색: 선반·고정대 / 금색: 30mm 지지대 / 은색: 체결 위치 설명',
 '조립 구상: 하부 모터·캐스터 → 바닥판과 배터리 → 지지대·선반 → 보드·전방 센서·카메라',
 '카메라 본체 미포함. 볼트·받침은 개념 표시이며 구멍·끼움·배선·강도는 확정 전.'])
board('20261029_자율주행자동차_구조6면도_v2.0_A.png','둥근 몸체 A안 · 6면도',[
 ('top','위 | 앞쪽은 위'),('bottom','아래'),('front','앞'),('rear','뒤'),('left','왼쪽'),('right','오른쪽')],3,[
 '수업 자료 반영: 휠 Ø96 / 캐스터 높이 62 / 지지대 길이 30mm',
 '스캔 형상은 실물 치수 보증 아님. 좌우 바퀴 방향·축 결합·체결부는 추가 대조 필요.',
 '몸체와 고정대 치수는 검토용 제안. 프린터 조건 확인 후 출력 설계를 확정.'])
