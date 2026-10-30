import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/20261029_layout_v1_A'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=0.001
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=900; scene.render.resolution_y=700; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
sh=scene.display.shading
sh.light='STUDIO'; sh.color_type='MATERIAL'; sh.show_shadows=True; sh.show_cavity=True
sh.cavity_type='BOTH'; sh.background_type='WORLD'; sh.background_color=(0.92,0.94,0.97)
scene.world.color=(0.92,0.94,0.97)
sh.show_specular_highlight=True
parts={}
colors={'라즈베리':(.24,.58,.32,1),'리포배터리':(.85,.42,.20,1),'보조배터리':(.25,.42,.70,1),'모터':(.55,.60,.65,1),'메카넘휠':(.22,.25,.29,1),'캐스터 휠':(.56,.47,.70,1)}
def material(name,color):
 m=bpy.data.materials.new(name); m.diffuse_color=color; return m
for name,col in colors.items():
 bpy.ops.wm.stl_import(filepath=str(ROOT/'references/parts/stl'/f'{name}.stl'))
 obj=bpy.context.object; obj.name=name
 lo=Vector([min(v.co[i] for v in obj.data.vertices) for i in range(3)])
 hi=Vector([max(v.co[i] for v in obj.data.vertices) for i in range(3)])
 mid=(lo+hi)/2
 for v in obj.data.vertices: v.co-=mid
 obj.data.materials.append(material(name,col)); parts[name]=obj
cam_data=bpy.data.cameras.new('PreviewCamera'); cam=bpy.data.objects.new('PreviewCamera',cam_data); scene.collection.objects.link(cam); scene.camera=cam
cam_data.type='ORTHO'; cam_data.clip_end=10000
def bounds(objects):
 bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
 lo=Vector([min(v[i] for v in pts) for i in range(3)]); hi=Vector([max(v[i] for v in pts) for i in range(3)])
 return (lo+hi)/2,hi-lo
def render(name,objects,direction):
 for o in scene.objects:
  if o.type=='MESH': o.hide_render=o not in objects
 center,size=bounds(objects)
 d=Vector(direction).normalized(); cam.location=center+d*1000
 cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
 if tuple(direction)==(0,0,1): cam.rotation_euler=(0,0,0)
 if tuple(direction)==(0,0,-1): cam.rotation_euler=(math.pi,0,0)
 cam_data.ortho_scale=max(size)*1.45 if name.startswith('part_') else 430
 scene.render.filepath=str(OUT/f'{name}.png'); bpy.ops.render.render(write_still=True)
if '--parts' in __import__('sys').argv:
 for n,o in parts.items(): render('part_'+n,[o],(1,-1,0.8))
else:
 # Reference-only arrangement. Numeric positions are layout proposals, not approved design dimensions.
 wheel=parts['메카넘휠']; wheel.scale=(96/97.63753509521484,)*3; wheel.rotation_euler[1]=math.pi/2; wheel.location=(-91,-80,48)
 wr=wheel.copy(); wr.data=wheel.data; scene.collection.objects.link(wr); wr.name='Wheel_Right_REFERENCE_ONLY'; wr.location.x=91
 # Duplicate geometry is not an assertion that handed L/R roller patterns match.
 motor=parts['모터']; motor.rotation_euler[2]=-math.pi/2; motor.location=(-37,-80,48)
 mr=motor.copy(); mr.data=motor.data; scene.collection.objects.link(mr); mr.name='Motor_Right'; mr.location.x=37; mr.rotation_euler[2]=math.pi/2
 parts['캐스터 휠'].scale=(62/74.484130859375,)*3; parts['캐스터 휠'].location=(0,124,31)
 parts['보조배터리'].location=(-25,10,71.25)
 parts['리포배터리'].location=(33,10,75.5)
 parts['라즈베리'].location=(-20,10,107)
 def box(name,dims,loc,color):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material(name,color)); return o
 driver=box('L298N_43x43x27_SPEC_ENVELOPE',(43,43,27),(27,-115,76.5),(.80,.25,.28,1))
 # Sensor PCB is a surface only: known 45 x 21 mm, depth explicitly unmodelled.
 bpy.ops.mesh.primitive_plane_add(size=1,location=(0,148,90),rotation=(math.pi/2,0,0))
 sensor=bpy.context.object; sensor.name='HY_SRF05_PCB_45x21_NO_DEPTH'; sensor.scale=(45,21,1); sensor.data.materials.append(material('Sensor',(.2,.7,.7,1)))
 allparts=list(parts.values())+[wr,mr,driver,sensor]
 render('isometric',allparts,(1,-1,.9))
 for name,d in [('top',(0,0,1)),('bottom',(0,0,-1)),('front',(0,1,0)),('rear',(0,-1,0)),('left',(-1,0,0)),('right',(1,0,0))]: render(name,allparts,d)
 lower=[o for o in allparts if o not in [parts['라즈베리'],sensor]]
 render('lower_top',lower,(0,0,1)); render('lower_iso',lower,(1,-1,.9))
 render('upper_top',[parts['라즈베리'],sensor],(0,0,1))
 # Save with all reference geometry visible. No chassis, holes, supports or camera dimensions invented.
 for o in allparts: o.hide_render=False
 center,size=bounds(allparts)
 report={'status':'reference placement only; no chassis; not print ready','units':'STL raw units interpreted as mm provisionally; wheel uniformly scaled to nominal 96mm radial envelope; caster uniformly scaled to nominal 62mm height; not a verified mesh calibration','axis':'X left/right; +Y front; +Z up','envelope_raw_mm_assumption':list(size),'notes':['Wheel right duplicates left mesh; handedness not verified','Motor and caster orientation must be reviewed visually','Camera location is annotated on composed image only; no size invented','HY-SRF05 shown as known PCB surface only','L298N is an outer size box, not detailed geometry','All placement coordinates are proposed arrangement, not approved dimensions']}
 (OUT/'placement_notes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/layout-preview-v1/20261029_자율주행자동차_부품배치_v1.0_A.blend'))
