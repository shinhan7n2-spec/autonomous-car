import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v61.blend');s=bpy.context.scene;O=bpy.data.objects
exec(open('/home/claude/w/v6_helpers.py').read())
Z0=79.484130859375;ZS=109.484130859375;ZT=113.484130859375;ROOF_IN=159.6
B=O['P01_한장바닥판_190x185x5'];SH=O['P02_분리선반_150x130x4'];CV=O['P10_들어올림덮개_v5.1']
X,Y=8,-59
U(B,cyl(2.6,ZS-19,ZS+0.01,X,Y))                 # fill old M6 pilot
U(B,box(X-6,X+6,Y-6,Y+6,Z0-0.01,ZS))            # wider seat for the shelf
U(B,cyl(4.8,ZS-0.01,159.0,X,Y))                  # column up to just under the roof
D(B,cyl(2.5,141.0,159.1,X,Y))                    # M6 self-tap pilot (5.0)
D(SH,cyl(5.1,ZS-1,ZT+1,X,Y))                     # shelf hole 10.2
tube=cyl(8,ZT+0.3,ROOF_IN+0.5,X,Y); D(tube,cyl(5.1,ZT,ROOF_IN+1,X,Y)); U(CV,tube)   # press tube under the roof
D(CV,cyl(3.3,150,170,X,Y))                       # roof hole 6.6 for M6
for o in (B,SH,CV): print(o.name,'nm',clean(o))
def tree(o,dz=0):
  bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
  if dz:bmesh.ops.translate(bm,verts=bm.verts,vec=(0,0,dz))
  t=BVHTree.FromBMesh(bm);bm.free();return t
M=[o for o in s.objects if o.type=='MESH']
for p in (B,SH,CV):
  tp=tree(p);print(p.name,'touch',sorted(o.name for o in M if o is not p and tp.overlap(tree(o))))
h=[]
for dz in range(2,131,3):
  t=tree(CV,dz);x=[o.name for o in M if o is not CV and t.overlap(tree(o))]
  if x:h.append((dz,x))
print('cover lift',h[:3])
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/w/out52/v62.blend')
