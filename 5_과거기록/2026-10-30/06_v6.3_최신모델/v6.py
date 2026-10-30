import bpy, bmesh, math, os, json
from mathutils import Vector
# v6: kit fasteners only, fewer parts, no thin pins/hooks.
SRC=os.environ.get('SRC','/home/claude/w/out52/v53.blend'); DST=os.environ.get('DST','/home/claude/w/out52/v6.blend')
bpy.ops.wm.open_mainfile(filepath=SRC); s=bpy.context.scene
Z0=79.484130859375; ZS=109.484130859375; ZT=113.484130859375
O=bpy.data.objects
def cube(d,p,n='c'):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=d; bpy.ops.object.transform_apply(scale=True); return o
def box(x0,x1,y0,y1,z0,z1,n='c'): return cube((x1-x0,y1-y0,z1-z0),((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),n)
def cyl(r,z0,z1,x,y,v=40,axis='Z'):
    if axis=='Z':
        bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=z1-z0,location=(x,y,(z0+z1)/2))
    else:  # along Y: z0,z1 are y-range, x,y are x,z
        bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=z1-z0,location=(x,(z0+z1)/2,y),rotation=(math.pi/2,0,0))
    o=bpy.context.object; bpy.ops.object.transform_apply(rotation=True); return o
def op(a,b,k):
    bpy.context.view_layer.objects.active=a; m=a.modifiers.new('m','BOOLEAN'); m.operation=k; m.solver='EXACT'; m.object=b
    bpy.ops.object.modifier_apply(modifier=m.name); bpy.data.objects.remove(b)
U=lambda a,b: op(a,b,'UNION'); D=lambda a,b: op(a,b,'DIFFERENCE')
def clean(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.01)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.001)
    bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_edges],context='VERTS')
    bm.to_mesh(o.data); n=sum(1 for e in bm.edges if not e.is_manifold); bm.free(); return n
base=O['P01_한장바닥판_190x185x5']; shelf=O['P02_분리선반_150x130x4']; cover=O['P10_들어올림덮개_v5.1']
deck=O['P09_카메라_클립받침']; bar=O['P04_배터리_고정가로대_일체']; mat=base.data.materials[0] if base.data.materials else None
for o in list(s.objects):
    if o.name.startswith(('REF_M4_30','REF_M4x20','P11_','REF_M3x20_카메라','REF_볼트머리')): bpy.data.objects.remove(o)

# ---------- 1. motor mounts: self-tapping M4x20 (kit), no nuts; L/R joined ----------
PL=[]; PU=[]
for x,sd in [(-53,'L'),(53,'R')]:
    u=O['P06_'+sd+'_U받침_V홈']; p=O['P07_'+sd+'_평판']
    for z in (65,49): U(u,box(x-10,x+5,-72.1,-63.9,z-1.9,z+1.9)); U(u,box(x-10,x+5,-32.1,-23.9,z-1.9,z+1.9))
    U(u,box(x-10,x+10,-75,-70.9,43,Z0-5)); U(u,box(x-10,x+10,-25.1,-21,43,Z0-5))
    U(p,box(x-10,x+10,-75,-70.9,32.6,36.6)); U(p,box(x-10,x+10,-25.1,-21,32.6,36.6))
    for y in (-68,-28): U(u,cyl(2.6,43,Z0-5,x,y)); U(p,cyl(2.6,32.6,36.6,x,y))
    PU.append(u); PL.append(p)
# bridges
U(PU[0],box(-43.5,43.5,-75,-21,Z0-9,Z0-5)); U(PU[0],PU[1]); cradle=PU[0]; cradle.name='P06_모터받침_일체'
U(PL[0],box(-63,63,-75,-21,28.6,32.7)); U(PL[0],PL[1]); plate=PL[0]; plate.name='P07_모터하판_일체'
for x in (-53,53):
    for y in (-70,-26):
        D(cradle,cyl(1.7,40,Z0-4.9,x,y))          # M4 self-tap pilot 3.4
        D(plate,cyl(2.25,20,40,x,y))              # M4 clearance
# base: fill old motor holes+counterbores, new holes + counterbores
for x in (-53,53):
    for y in (-68,-28): U(base,cyl(4.35,Z0-5,Z0,x,y))
    for y in (-70,-26): D(base,cyl(2.25,Z0-6,Z0+1,x,y)); D(base,cyl(4.25,Z0-3,Z0+0.01,x,y))

# ---------- 2. shelf on printed base columns; M6x20 (kit camera bolt) at rear-left ----------
cols=[(8,-59,'screw'),(69,-59,'peg'),(-76,64,'peg'),(69,64,'peg')]
for x,y,k in cols:
    U(base,box(x-5,x+5,y-5,y+5,Z0-0.01,ZS))
    if k=='peg': U(base,cyl(4,ZS-0.01,ZS+3.6,x,y)); D(shelf,cyl(4.2,ZS-1,ZT+1,x,y))
    else: D(base,cyl(2.5,ZS-18,ZS+0.01,x,y)); D(shelf,cyl(3.25,ZS-1,ZT+1,x,y))
# remove old board posts/guides/pad on shelf top, then rails
D(shelf,box(-78,72,-52,58,ZT-0.002,175))
def add(o,x0,x1,y0,y1,z0,z1): U(o,box(x0,x1,y0,y1,(ZT-0.01 if abs(z0-ZT)<1e-6 else z0),z1))
# Pi (case x -62..-6, y -34..54, top 137.5): side rails with lips, front corner stops, key slot at rear
add(shelf,-66.5,-63,-40,51,ZT,139.6); add(shelf,-63.01,-60.5,-40,51,138.1,139.6)
add(shelf,-5,-1.5,-40,51,ZT,139.6);   add(shelf,-7.5,-4.99,-40,51,138.1,139.6)
add(shelf,-62,-58,54.6,57.6,ZT,121.5); add(shelf,-10,-6,54.6,57.6,ZT,121.5)
D(shelf,box(-67,-1,-38.4,-34.6,ZT-0.001,141))
# driver (PCB x16.5..59.5, y -46.5..-3.5, PCB bottom 116.48): corner pads, corner clips with lips, front stops, rear key posts
for x0,x1 in ((16.5,22.5),(53.5,59.5)):
    for y0,y1 in ((-46.5,-40.5),(-9.5,-3.5)): add(shelf,x0,x1,y0,y1,ZT,116.48)
for wx0,wx1,lx0,lx1 in ((13,16,15.99,18.5),(60,63,57.5,60.01)):
    add(shelf,wx0,wx1,-51,-39.5,ZT,120.3); add(shelf,lx0,lx1,-46.5,-39.5,118.6,120.3)
    add(shelf,wx0,wx1,-10.5,-3.5,ZT,120.3); add(shelf,lx0,lx1,-10.5,-3.5,118.6,120.3)
add(shelf,16.5,22.5,-3.0,0,ZT,121); add(shelf,53.5,59.5,-3.0,0,ZT,121)
D(shelf,box(12,64,-50.4,-47.0,ZT-0.001,124))
# board key: one drop-in part (Pi rear + driver rear joined)
key=box(-66.4,-1.6,-38.2,-34.8,ZT,126,'P15_보드_뒤막대')
U(key,box(-1.61,-1.3,-38.2,-34.8,ZT,117)); U(key,box(-1.4,13.0,-50.2,-34.8,ZT,117)); U(key,box(12.99,63.9,-50.2,-47.2,ZT,123))
if mat: key.data.materials.append(mat)
# camera deck <-> shelf: pegs instead of M3
for x in (-24,24):
    D(shelf,cyl(3.25,ZS-1,ZT+1,x,68)); U(deck,cyl(1.8,ZT,ZT+12,x,68)); U(deck,cyl(3,ZS+0.6,ZT+0.01,x,68))
# pillar pegs 4.6 -> 6 ; deck holes 6.5
for x in (-24,24):
    U(base,cyl(3,125.48,129.48,x,80)); D(deck,cyl(3.25,124,131,x,80))

# ---------- 3. crossbar on 6 mm pegs, thick link; fill old M3 holes and nut slots ----------
for x,top in ((-74,97),(6,97),(16,105.5),(64,105.5)):
    U(base,cyl(2.1,Z0,top,x,15)); slotz=(92.48 if top==97 else 100.98)
    U(base,box(x-4,x+4,9.01,20.99,slotz-1.5,slotz+1.5))
    U(base,cyl(3,top-0.01,top+2.8,x,15)); U(bar,cyl(2.05,top,top+3,x,15)); D(bar,cyl(3.3,top-1,top+4,x,15))
D(bar,box(11.9,12.4,9.9,20.1,96.9,105.45)); U(bar,box(4,11.95,10,20,99.9,108.5))

# ---------- 4. camera press plate joined to deck (P13 removed); fill M3 holes ----------
p13=O['P13_カメラ_뒤클립누름판']
pb=[p13.matrix_world@Vector(c) for c in p13.bound_box]; z0=min(q.z for q in pb); z1=max(q.z for q in pb)
db=[deck.matrix_world@Vector(c) for c in deck.bound_box]
for x in (-31,31):
    U(p13,cyl(2.1,67.9,72.1,x,(z0+z1)/2,axis='Y')); U(deck,cyl(2.1,77.9,86.1,x,(z0+z1)/2,axis='Y'))
    U(deck,box(x-3.6,x+3.6,83.0,86.0,(z0+z1)/2-3.6,(z0+z1)/2+3.6))
for sx in (-1,1): U(p13,box(*sorted([sx*25,sx*37]),71.99,78.01,z0,z1))
U(deck,p13); deck.name='P09_카메라_받침_일체'

# ---------- 5. cover: remove pin feet; base rim; fill old pin holes ----------
for yy in ((73.5,89.5),(-88.5,-78.0)):
    for sx in (-1,1): D(cover,box(*sorted([sx*65.5,sx*80.5]),yy[0],yy[1],Z0-6,Z0+5.1))
for x in (-73,73):
    for y in (-82,83): U(base,cyl(2.1,Z0-5,Z0,x,y))
def ring(inset,n=10):
    HX,Y0,Y1,RC=87.5,-91.0,92.0,18.0
    hx=HX-inset;y0=Y0+inset;y1=Y1-inset;r=RC-inset;pts=[]
    for cx,cy,a0 in [(hx-r,y1-r,0),(-hx+r,y1-r,90),(-hx+r,y0+r,180),(hx-r,y0+r,270)]:
        for k in range(n+1):
            a=math.radians(a0+90*k/n);pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return pts
def prism(pts,z0,z1,name):
    me=bpy.data.meshes.new(name);bm=bmesh.new()
    f=bm.faces.new([bm.verts.new((x,y,z0)) for x,y in pts]);bmesh.ops.recalc_face_normals(bm,faces=[f])
    if f.normal.z>0: f.normal_flip()
    r=bmesh.ops.extrude_face_region(bm,geom=[f]);vs=[e for e in r['geom'] if isinstance(e,bmesh.types.BMVert)]
    bmesh.ops.translate(bm,verts=vs,vec=(0,0,z1-z0));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);return o
rim=prism(ring(2.8),Z0-0.01,Z0+3,'rim'); D(rim,prism(ring(4.8),Z0-1,Z0+4,'rimin'))
for b in [(-100,-76,-104,8),(76,100,-104,8),(-42.5,42.5,70,100),(-70.5,-39,70,100),(-80.5,70.5,-100,-56.5)]:
    D(rim,box(b[0],b[1],b[2],b[3],Z0-2,Z0+5))
U(base,rim)

# ---------- 6. sensor pillar front lip 1.6 -> 3.1 ----------
for sx in (-1,1):
    U(base,box(*sorted([sx*20,sx*28]),85.99,87.5,Z0,125.48))
    D(base,box(*sorted([sx*19.5,sx*21.2]),84.4,88.2,102.0,131.5))

res={o.name:clean(o) for o in [base,shelf,cover,deck,bar,cradle,plate,key]}
print('non_manifold',res)
bpy.ops.wm.save_as_mainfile(filepath=DST)
