import sys, time, numpy as np, trimesh, torch, warnings
warnings.filterwarnings("ignore")
from pytorch3d.renderer import MeshRasterizer, RasterizationSettings, PerspectiveCameras, look_at_view_transform
from pytorch3d.structures import Meshes
def load(p):
    s=trimesh.load(p, force="scene"); m=s.to_geometry() if hasattr(s,"to_geometry") else s.dump(concatenate=True)
    return np.asarray(m.vertices,np.float32), np.asarray(m.faces,np.int64)
def sil(v,f,R,T,res=512,fov=30):
    cam=PerspectiveCameras(R=R,T=T,focal_length=1/np.tan(np.radians(fov/2)))
    ras=MeshRasterizer(cameras=cam,raster_settings=RasterizationSettings(image_size=res,blur_radius=0,faces_per_pixel=1,bin_size=None,max_faces_per_bin=30000))
    m=Meshes(verts=[torch.tensor(v)],faces=[torch.tensor(f)])
    return (ras(m).pix_to_face[0,...,0]>=0).numpy()
rng=np.random.default_rng(0)
views=[look_at_view_transform(dist=6.0,elev=rng.uniform(-80,80),azim=rng.uniform(0,360)) for _ in range(16)]
v0,f0=load(sys.argv[1]); print("orig faces",len(f0),flush=True)
t=time.time(); ref=[sil(v0,f0,R,T) for R,T in views]; print("orig 16 sil %.1fs"%(time.time()-t),flush=True)
for p in sys.argv[2:]:
    v,f=load(p); ious=[]; xo=[]
    t=time.time()
    for (R,T),r in zip(views,ref):
        s=sil(v,f,R,T); ious.append((s&r).sum()/(s|r).sum()); xo.append((s^r).sum())
    print("%-22s faces=%6d (%5.1f%%)  IoU min=%.4f mean=%.4f  xor px max=%d mean=%.0f  t=%.1fs"%(p.split("/")[-1],len(f),100*len(f)/len(f0),min(ious),np.mean(ious),max(xo),np.mean(xo),time.time()-t),flush=True)
