from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'outputs/20261029_layout_v1_A'
FONT='C:/Windows/Fonts/malgun.ttf'
def f(n): return ImageFont.truetype(FONT,n)
def board(name,title,tiles,cols,footer):
 w=1800; tilew=w//cols; tileh=490 if cols==3 else 610
 rows=(len(tiles)+cols-1)//cols
 im=Image.new('RGB',(w,145+rows*tileh+120),'#f4f6fa'); d=ImageDraw.Draw(im)
 d.text((35,20),title,font=f(38),fill='#1c3149')
 d.text((35,78),'제공 STL 배치 검토 · 위치는 제안 · 몸체/고정대 미생성 · 실물 및 단위 대조 전',font=f(23),fill='#4b5e74')
 for i,(file,label) in enumerate(tiles):
  x=(i%cols)*tilew; y=145+(i//cols)*tileh
  d.text((x+22,y+5),label,font=f(26),fill='#1c3149')
  pic=Image.open(OUT/(file+'.png')).convert('RGB'); pic.thumbnail((tilew-20,tileh-58))
  im.paste(pic,(x+(tilew-pic.width)//2,y+50))
 y=145+rows*tileh
 for j,line in enumerate(footer): d.text((35,y+10+j*32),line,font=f(22),fill='#45576b')
 im.save(OUT/name)
board('20261029_자율주행자동차_6면도_v1.0_A.png','부품 배치 A안 · 6면도', [('top','위 | 앞쪽은 위'),('bottom','아래 | 하부에서 본 모습'),('front','앞 | 카메라·센서 방향'),('rear','뒤'),('left','왼쪽'),('right','오른쪽')],3,['초록: 라즈베리 STL / 파랑: 보조배터리 / 주황: 리포배터리 / 보라: 캐스터 / 회색: 모터·바퀴','빨강: 드라이버 외곽 43×43×27 / 청록: 센서 기판 45×21만 표시 / 카메라 형상은 미포함'])
board('20261029_자율주행자동차_층별프리뷰_v1.0_A.png','부품 배치 A안 · 층별 프리뷰',[('isometric','전체 | 사선 보기'),('lower_top','하부 | 상부 보드 숨김·위에서'),('lower_iso','하부 | 상부 보드 숨김·사선'),('upper_top','상부 | 보드와 센서 기판만')],2,['카메라 예정 위치: 앞쪽 위. 외형 크기·받침 치수 확보 후 추가 / 센서는 깊이 없는 기판 면만 표시','프리뷰의 층 높이·배치는 검토용이며, 30mm 지지대 설치 가능성·구멍·간섭·지상고는 미검증'])
