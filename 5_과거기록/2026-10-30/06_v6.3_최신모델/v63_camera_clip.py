import bpy,bmesh,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='/home/claude/w/out52/v62.blend');s=bpy.context.scene;O=bpy.data.objects
exec(open('/home/claude/w/v6_helpers.py').read())
P=O['P09_카메라_받침_일체'];CV=O['P10_들어올림덮개_v5.1']
# 1 remove rear press bar + side walls (y 68..78, z 151..163) -> blade only, like a monitor top
D(P,box(-40,40,66,77.999,150,164))
print('P09 nm',clean(P))
# 2 replace old clip guesses with a photo-based estimate: top plate 45 deep, front lip, rear flap 55 long angled onto blade back
for n in list(O.keys()):
    if n.startswith(('REF_카메라_뒤접이판','REF_뒤접이힌지','REF_카메라_힌지받침','REF_카메라_앞걸림턱','REF_본체힌지')): bpy.data.objects.remove(O[n])
refc=bpy.data.collections.get('V4_추정형상_출력제외') or s.collection
def ref(o,n):
    o.name=n
    for c in list(o.users_collection): c.objects.unlink(o)
    refc.objects.link(o); return o
ref(box(-24,24,41,90,177,181),'REF_클립_위판_사진추정')
ref(box(-24,24,86.2,90,160,181),'REF_클립_앞걸림턱_사진추정')
hy,hz=43,178; ty,tz=78.3,0
L=55.0; dy=ty-hy; dz=-math.sqrt(L*L-dy*dy); tz=hz+dz
fl=box(-24,24,-2,2,-L,0,'f'); ang=math.atan2(dy,-dz)
fl.matrix_world=Matrix.Translation((0,hy,hz))@Matrix.Rotation(ang,4,'X')
bpy.context.view_layer.objects.active=fl; fl.select_set(True); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
ref(fl,'REF_클립_뒤판_사진추정')
print('flap tip z',round(tz,1))
# 3 cover: open the roof further back for the clip (y from 30)
D(CV,box(-41,41,30,60,150,175)); print('P10 nm',clean(CV))
def tree(o):
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);t=BVHTree.FromBMesh(bm);bm.free();return t
M=[o for o in s.objects if o.type=='MESH' and not o.hide_viewport]
for n in ['REF_클립_위판_사진추정','REF_클립_앞걸림턱_사진추정','REF_클립_뒤판_사진추정']:
    t=tree(O[n]); print(n,'겹침',sorted(o.name for o in M if not o.name.startswith('REF_클립') and o.name!=n and t.overlap(tree(o))))
bm=bmesh.new();bm.from_mesh(CV.data);bm.transform(CV.matrix_world)
h=[]
for dz in range(2,131,3):
    b2=bm.copy();bmesh.ops.translate(b2,verts=b2.verts,vec=(0,0,dz));t=BVHTree.FromBMesh(b2);b2.free()
    x=[o.name for o in M if o is not CV and t.overlap(tree(o))]
    if x:h.append((dz,x))
print('cover lift',h[:3])
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/w/out52/v63.blend')
