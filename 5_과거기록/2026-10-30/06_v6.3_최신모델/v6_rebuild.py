import bpy, bmesh, math
from mathutils import Vector
# v6.1: rebuild P01 base and P09 camera stand from an explicit feature list (no legacy leftovers); clean P10.
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v6.blend'); s=bpy.context.scene; O=bpy.data.objects
exec(open('/home/claude/w/v6_helpers.py').read())
Z0=79.484130859375; ZB=Z0-5; ZS=109.484130859375; ZT=113.484130859375
old=O['P01_한장바닥판_190x185x5']; mat=old.data.materials[0]
# ---- outline of the plate from a mid-thickness section of the old base (outer loop only) ----
bm=bmesh.new(); bm.from_mesh(old.data); bm.transform(old.matrix_world)
r=bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=(0,0,ZB+0.7),plane_no=(0,0,1))
cut=[e for e in r['geom_cut'] if isinstance(e,bmesh.types.BMEdge)]
# walk loops
adj={}
for e in cut:
    a,b=e.verts; adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
loops=[];seen=set()
for v in adj:
    if v in seen: continue
    loop=[v];seen.add(v);prev=None;cur=v
    while True:
        nx=[w for w in adj[cur] if w is not prev and w not in seen]
        if not nx: break
        prev,cur=cur,nx[0];seen.add(cur);loop.append(cur)
    loops.append([(p.co.x,p.co.y) for p in loop])
def area(L): return abs(sum(L[i][0]*L[(i+1)%len(L)][1]-L[(i+1)%len(L)][0]*L[i][1] for i in range(len(L))))/2
outer=max(loops,key=area); bm.free()
print('outline pts',len(outer),'area',round(area(outer)))
def prism(pts,z0,z1,name):
    me=bpy.data.meshes.new(name);b=bmesh.new()
    f=b.faces.new([b.verts.new((x,y,z0)) for x,y in pts])
    r=bmesh.ops.extrude_face_region(b,geom=[f]);vs=[e for e in r['geom'] if isinstance(e,bmesh.types.BMVert)]
    bmesh.ops.translate(b,verts=vs,vec=(0,0,z1-z0));bmesh.ops.recalc_face_normals(b,faces=list(b.faces))
    b.to_mesh(me);b.free();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);return o
def ring(inset,n=10):
    HX,Y0,Y1,RC=87.5,-91.0,92.0,18.0
    hx=HX-inset;y0=Y0+inset;y1=Y1-inset;r=RC-inset;pts=[]
    for cx,cy,a0 in [(hx-r,y1-r,0),(-hx+r,y1-r,90),(-hx+r,y0+r,180),(hx-r,y0+r,270)]:
        for k in range(n+1):
            a=math.radians(a0+90*k/n);pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return pts
bpy.data.objects.remove(old)
B=prism(outer,ZB,Z0,'P01_한장바닥판_190x185x5'); B.data.materials.append(mat)
def add(*b): U(B,box(*b))
def sub(*b): D(B,box(*b))
# 1 front pillars (sensor groove + camera-stand peg)
for sx in (-1,1):
    x0,x1=sorted([sx*20,sx*28]); add(x0,x1,74,87.5,Z0-0.01,125.484)
    U(B,cyl(3,125.47,129.484,sx*24,80))
    g0,g1=sorted([sx*19.5,sx*23.0]); sub(g0,g1,82.6,84.4,102.0,131.5)
    r0,r1=sorted([sx*19.5,sx*21.2]); sub(r0,r1,84.4,88.2,102.0,131.5)
# 2 shelf columns + pegs / M6 pilot
for x,y,k in [(8,-59,'screw'),(69,-59,'peg'),(-76,64,'peg'),(69,64,'peg')]:
    add(x-5,x+5,y-5,y+5,Z0-0.01,ZS)
    if k=='peg': U(B,cyl(4,ZS-0.01,ZS+3.6,x,y))
    else: D(B,cyl(2.5,ZS-18,ZS+0.01,x,y))
# 3 battery walls and front stops (rear open for sliding out)
add(-72.25,-70.25,-64,64,Z0-0.01,Z0+4); add(2.25,4.25,-64,64,Z0-0.01,Z0+4); add(-72.25,4.25,71,73,Z0-0.01,Z0+5)
add(18.5,20.5,-46,46,Z0-0.01,Z0+4); add(59.5,61.5,-46,46,Z0-0.01,Z0+4); add(18.5,61.5,53,55,Z0-0.01,Z0+5)
# 4 crossbar posts + 6 mm pegs
for x,top in ((-74,97),(6,97),(16,105.5),(64,105.5)):
    add(x-4,x+4,9,21,Z0-0.01,top); U(B,cyl(3,top-0.01,top+2.8,x,15))
# 5 gate channels (open-top slots)
for bx0,bx1,sx0,sx1,yc in [(-84,-75,-78,-75,-76),(7,16,7,10,-76),(6,15,12,15,-68),(65,74,65,68,-68)]:
    add(bx0,bx1,yc-4.2,yc+4.2,Z0-0.01,Z0+12.5); sub(sx0,sx1,yc-2.2,yc+2.2,Z0+0.001,Z0+14)
# 6 cover locating rim
rim=prism(ring(2.8),Z0-0.01,Z0+3,'rim'); D(rim,prism(ring(4.8),Z0-1,Z0+4,'rimin'))
for b in [(-100,-76,-104,8),(76,100,-104,8),(-42.5,42.5,70,100),(-70.5,-39,70,100),(-80.5,70.5,-100,-56.5)]:
    D(rim,box(b[0],b[1],b[2],b[3],Z0-2,Z0+5))
U(B,rim)
# 7 caster: slots +-2 mm along x, nut pockets from top
for x in (-27,27):
    for y in (38,62):
        sl=box(x-2,x+2,y-2.75,y+2.75,ZB-2,Z0+2); U(sl,cyl(2.75,ZB-2,Z0+2,x-2,y)); U(sl,cyl(2.75,ZB-2,Z0+2,x+2,y)); D(B,sl)
        sub(x-6.5,x+6.5,y-4.1,y+4.1,Z0-4,Z0+0.01)
# 8 motor-mount holes + head counterbores
for x in (-53,53):
    for y in (-70,-26): D(B,cyl(2.25,ZB-1,Z0+1,x,y)); D(B,cyl(4.25,Z0-3,Z0+0.01,x,y))
# 9 wire pass-through slots
for x,y in [(78,40),(-82,40)]:
    sl=box(x-2,x+2,y-4,y+4,ZB-2,Z0+2); U(sl,cyl(2,ZB-2,Z0+2,x,y-4)); U(sl,cyl(2,ZB-2,Z0+2,x,y+4)); D(B,sl)
print('P01 nm',clean(B))

# ---- P09 camera stand rebuilt ----
oldd=O['P09_카메라_받침_일체']; dm=oldd.data.materials[0] if oldd.data.materials else mat; bpy.data.objects.remove(oldd)
P=box(-39,39,64,94,125.484,129.484,'P09_카메라_받침_일체')
U(P,box(-37,37,78,86,129.47,177.0))                    # monitor-style blade
U(P,box(-37,37,68,72,151,163))                         # rear press bar (was P13)
for sx in (-1,1):
    U(P,box(*sorted([sx*25,sx*37]),71.99,78.01,151,163)) # side walls -> 6 mm pocket for the clip's back flap
    U(P,box(sx*24-5,sx*24+5,64.5,72,ZT,125.5))           # pads onto shelf
    U(P,cyl(3,ZS+0.6,ZT+0.01,sx*24,68))                  # pegs into shelf
    D(P,cyl(3.25,124,131,sx*24,80))                      # holes onto pillar pegs
P.data.materials.append(dm); print('P09 nm',clean(P))

# ---- P10: remove foot leftovers and floating slivers ----
cv=O['P10_들어올림덮개_v5.1']
for yy in ((72.0,89.55),(-88.55,-76.5)):
    for sx in (-1,1): D(cv,box(*sorted([sx*63.5,sx*85.05]),yy[0],yy[1],Z0-6,Z0+5.3))
b=bmesh.new(); b.from_mesh(cv.data); seen=set(); comps=[]
for v in b.verts:
    if v in seen: continue
    st=[v];c=[]
    while st:
        x=st.pop()
        if x in seen: continue
        seen.add(x);c.append(x);st.extend(e.other_vert(x) for e in x.link_edges)
    comps.append(c)
comps.sort(key=len)
for c in comps[:-1]: bmesh.ops.delete(b,geom=c,context='VERTS')
b.to_mesh(cv.data); b.free(); print('P10 removed islands',len(comps)-1,'nm',clean(cv))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/w/out52/v61.blend')
