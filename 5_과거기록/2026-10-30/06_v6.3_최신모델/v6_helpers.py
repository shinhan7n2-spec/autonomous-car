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
