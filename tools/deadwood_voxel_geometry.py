"""Load the reviewed, source-indexed deadwood voxel artwork.

The authoring stage lives in author_deadwood_voxels.py. Keeping the full grids
as artwork allows manual corrections and approved reference models to survive
normal package builds without optional sculpting dependencies.
"""
from pathlib import Path
import hashlib,json
import numpy as np

def geometry(p,w,h,left,name,palette,root=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parent.parent
    art=root/'tools/artwork/deadwood/voxel-sources'
    record=next(r for r in json.loads((art/'sources.json').read_text()) if r['name']==name)
    source=root/'tutnt/patches/deadwood'/f'{name}.lmp';grid=art/(name+'.npz')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=record['source_sha256']:
        raise ValueError('Deadwood source changed; review/regenerate artwork: '+name)
    if hashlib.sha256(grid.read_bytes()).hexdigest()!=record['grid_sha256']:
        raise ValueError('Unrecorded deadwood artwork change: '+name)
    with np.load(grid,allow_pickle=False) as a:
        xyz=a['xyz'].astype(int);colors=a['colors'].astype(int)
    if xyz.ndim!=2 or xyz.shape[1]!=3 or colors.shape!=(len(xyz),):raise ValueError('Invalid voxel grid '+name)
    if len(np.unique(xyz,axis=0))!=len(xyz):raise ValueError('Duplicate voxel coordinates '+name)
    if not ((xyz[:,0]>=0)&(xyz[:,0]<w)&(xyz[:,2]>=0)&(xyz[:,2]<h)).all():raise ValueError('Grid outside source bounds '+name)
    if not set(colors.tolist())<=set(p.values()):raise ValueError('Non-source palette indices '+name)
    projection={}
    for i in np.argsort(xyz[:,1],kind='stable'):
        x,y,z=xyz[i];projection.setdefault((int(x),int(z)),int(colors[i]))
    if projection!=p:raise ValueError('Voxel front differs from source '+name)
    ymin=int(xyz[:,1].min());ymax=int(xyz[:,1].max())
    # The engine's source-facing view reads the stored Y columns in reverse.
    vox={(int(x),ymax-int(y),int(z)):int(c) for (x,y,z),c in zip(xyz,colors)}
    return vox,(w,ymax-ymin+1,h),(left,ymax,h)
