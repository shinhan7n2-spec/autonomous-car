import bpy
from mathutils import Vector
from pathlib import Path
center=Vector((0,15,65))
q=Vector((1,-1,.9)).to_track_quat('Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active
   space.region_3d.view_location=center
   space.region_3d.view_distance=440
   space.region_3d.view_rotation=q
   space.region_3d.view_perspective='ORTHO'
   space.clip_end=10000
   space.shading.type='SOLID'; space.shading.color_type='MATERIAL'
   space.overlay.show_floor=False
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
