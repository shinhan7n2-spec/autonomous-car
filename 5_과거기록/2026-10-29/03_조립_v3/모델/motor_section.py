import bpy,numpy as np
from pathlib import Path
r=Path.cwd();bpy.ops.wm.open_mainfile(filepath=str(r/'models/assembly-v3/20261029_자율주행자동차_한장차체조립_v3.2_A.blend'))
o=bpy.data.objects['Motor_Right'];a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);a=a.reshape(-1,3);M=np.array(o.matrix_world);a=a@M[:3,:3].T+M[:3,3]
for x in [35,45,53,60,70]:
 p=a[np.abs(a[:,0]-x)<1];y=p[:,1];z=p[:,2];A=np.c_[2*y,2*z,np.ones(len(p))];cy,cz,k=np.linalg.lstsq(A,y*y+z*z,rcond=None)[0];rad=np.sqrt((y-cy)**2+(z-cz)**2);print(x,'center',cy,cz,'r quantile',np.quantile(rad,[0,.5,.95,1]),'bounds',p.min(0),p.max(0))
