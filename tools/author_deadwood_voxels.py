"""Author native-grid deadwood artwork from low-resolution indexed patches.

Requires numpy, scipy and scikit-image (see requirements-deadwood-artwork.txt).
Normal package builds consume the checked-in voxel grids and need only numpy.
Approved reference grids are authoritative artwork and are never regenerated.
"""
from pathlib import Path
from collections import deque
import argparse, hashlib, json, math
import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter, label
from scipy.spatial import cKDTree
from skimage.morphology import medial_axis
from build_voxels import patch

ROOT = Path(__file__).resolve().parent.parent
ART = Path('tools/artwork/deadwood/voxel-sources')

def sample_paths(paths):
    points=[]
    for tag,path in enumerate(paths):
        for a,b in zip(np.array(path,float)[:-1],np.array(path,float)[1:]):
            for t in np.linspace(0,1,max(2,int(np.linalg.norm(a-b)*2))):
                points.append((*((1-t)*a+t*b),tag))
    return np.array(points)

def weld(volume, mask):
    """Connect each source-connected component without adding a source ray."""
    source_labels,_=label(mask,np.ones((3,3)))
    for _ in range(160):
        xyz=np.array(list(volume));lo=xyz.min(0);occ=np.zeros(xyz.max(0)-lo+1,bool)
        occ[tuple((xyz-lo).T)]=True;labels,n=label(occ,np.ones((3,3,3)))
        own=labels[tuple((xyz-lo).T)];counts=np.bincount(own);counts[0]=0
        groups={}
        for i in range(1,n+1):
            component=xyz[own==i];q=component[0]
            groups.setdefault(int(source_labels[q[2],q[0]]),[]).append(i)
        pair=next((v for v in groups.values() if len(v)>1),None)
        if pair is None:return int(n)
        main=max(pair,key=lambda i:counts[i]);body=xyz[own==main]
        fragment=xyz[own==max((i for i in pair if i!=main),key=lambda i:counts[i])]
        dd,nn=cKDTree(body).query(fragment);k=int(dd.argmin());a=fragment[k];b=body[nn[k]]
        line=np.rint(np.linspace(a,b,int(max(abs(b-a)))+1)).astype(int)
        if all(mask[q[2],q[0]] for q in line):
            volume.update(map(tuple,line));continue
        target={(int(q[0]),int(q[2])) for q in body};start=(int(a[0]),int(a[2]))
        queue=deque([start]);parent={start:None};end=None
        while queue:
            u=queue.popleft()
            if u in target:end=u;break
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                v=(u[0]+dx,u[1]+dz)
                if 0<=v[0]<mask.shape[1] and 0<=v[1]<mask.shape[0] and mask[v[1],v[0]] and v not in parent:
                    parent[v]=u;queue.append(v)
        if end is None:raise ValueError('Disconnected source component has no legal path')
        path=[];u=end
        while u is not None:path.append(u);u=parent[u]
        path.reverse();candidates=body[(body[:,0]==end[0])&(body[:,2]==end[1])]
        by=int(candidates[np.argmin(abs(candidates[:,1]-a[1])),1]);previous=int(a[1])
        for j,(x,z) in enumerate(path):
            y=round(a[1]+(by-a[1])*j/max(1,len(path)-1))
            volume.update((x,v,z) for v in range(min(previous,y),max(previous,y)+1));previous=y
        volume.update((end[0],v,end[1]) for v in range(min(previous,by),max(previous,by)+1))
    raise ValueError('Quantized branches did not converge to source connectivity')

def sculpt(p,w,h,left,name,palette,plan):
    rgb=np.frombuffer(palette,np.uint8).reshape(256,3).astype(float)
    mask=np.zeros((h,w),bool);idx=np.zeros((h,w),np.uint8)
    for (x,z),c in p.items():mask[z,x]=True;idx[z,x]=c
    skeleton,dist=medial_axis(mask,return_distance=True,rng=0)
    axes=sample_paths(plan['paths']);zz,xx=np.mgrid[:h,:w]
    nn=cKDTree(axes[:,[2,0]]).query(np.stack((zz.ravel(),xx.ravel()),axis=1))[1]
    depth=gaussian_filter(axes[nn,1].reshape(h,w),1.7)
    volume=set()
    def stamp(cx,cy,cz,r,interior=False):
        for x in range(max(0,math.floor(cx-r)),min(w,math.ceil(cx+r)+1)):
            for z in range(max(0,math.floor(cz-r)),min(h,math.ceil(cz+r)+1)):
                if not mask[z,x] or (interior and dist[z,x]<2):continue
                rem=r*r-(x-cx)**2-(z-cz)**2
                if rem>=0:
                    dy=math.sqrt(rem)
                    volume.update((x,y,z) for y in range(math.ceil(cy-dy),math.floor(cy+dy)+1))
    for z,x in np.argwhere(skeleton):stamp(x,depth[z,x],z,max(.55,dist[z,x]-.22))
    occupied={(x,z) for x,y,z in volume}
    for x,z in p:
        if (x,z) not in occupied:volume.add((x,round(depth[z,x]),z))
    # Individual source guides govern bends; additional depth follows an existing
    # branch's projected course, keeping its attachment inside the same silhouette.
    tree='tree' in name
    if tree:
        for sign,path in zip((-1,1),plan['paths'][1:3]):
            a=np.array(path,float)
            for j in range(len(a)-1):
                for t in np.linspace(0,1,max(2,int(np.linalg.norm(a[j+1]-a[j])*2))):
                    cx,cy,cz=(1-t)*a[j]+t*a[j+1];u=(j+t)/max(1,len(a)-1)
                    x=int(np.clip(round(cx),0,w-1));z=int(np.clip(round(cz),0,h-1))
                    stamp(cx,cy+sign*30*math.sin(u*math.pi/2),cz,max(.6,dist[z,x]*.7),interior=True)
    for sign in (-1,1):
        path=[(left,0,h-11,7 if tree else 5),(left+sign*4,sign*13,h-6,4),(left+sign*9,sign*27,h-2,1)]
        for a,b in zip(np.array(path,float)[:-1],np.array(path,float)[1:]):
            for t in np.linspace(0,1,30):stamp(*((1-t)*a+t*b))
    # Continuous rounded cross-sections remove side terraces on the main trunk.
    rows={}
    for x,y,z in volume:rows.setdefault((x,z),[]).append(y)
    main=np.array(plan['paths'][0],float);main=main[np.argsort(main[:,2])]
    begin=plan.get('trunk_limit',round(h*.55)) if tree else 3
    end=h-15 if tree else h-5
    for z in range(begin,end):
        cx=np.interp(z,main[:,2],main[:,0]);cy=np.interp(z,main[:,2],main[:,1]);ic=int(np.clip(round(cx),0,w-1))
        if not mask[z,ic]:continue
        l=ic;r=ic
        while l>0 and mask[z,l-1]:l-=1
        while r<w-1 and mask[z,r+1]:r+=1
        rx=min(cx-l+.5,r-cx+.5);ry=max(2,rx*.95)
        if not tree:ry=min(15,ry)
        blend=min(1,(z-begin+1)/5,(end-z)/5)
        for x in range(l,r+1):
            ys=rows.get((x,z),[])
            if not ys:continue
            u=(x-cx)/max(1,cx-l+.6 if x<cx else r-cx+.6)
            d=ry*max(0,1-abs(u)**4)**.25
            low=round((1-blend)*min(ys)+blend*(cy-d));high=round((1-blend)*max(ys)+blend*(cy+d))
            volume.difference_update((x,y,z) for y in ys)
            volume.update((x,y,z) for y in range(low,high+1))
    if 'well' in plan:
        well=plan['well'];rays={}
        for x,y,z in volume:rays.setdefault((x,z),[]).append(y)
        for (x,z),ys in rays.items():
            cut=[y for y in ys if ((x-well['x'])/well['radius'])**2+((y-well['y'])/well['radius'])**2<1 and z<well['depth']]
            if len(cut)==len(ys):cut.remove(max(ys))
            volume.difference_update((x,y,z) for y in cut)
    components=weld(volume,mask)
    # Local native bark, with Y carrying the transverse pixel coordinate.
    snow_mask=(rgb.max(1)-rgb.min(1)<45)&(rgb.mean(1)>95)
    safe=mask&(dist>=2)
    if name.startswith('frozen'):safe &= ~snow_mask[idx]
    if 'well' in plan:
        well=plan['well'];safe &= ~(((xx-well['x'])/well['radius'])**2+((zz-9)/9)**2<1)
    if not safe.any():safe=mask.copy()
    fill=distance_transform_edt(~safe,return_distances=False,return_indices=True)
    filled=idx[tuple(fill)];albedo=rgb[filled];low=gaussian_filter(albedo,(3,3,0));grain=np.clip((albedo+4)/(low+4),.45,1.9)
    bark=rgb[idx[safe]];bark=bark[bark.mean(1)>15];base=np.median(bark,axis=0)
    available=np.array(sorted(set(p.values())))
    material_available=available[~snow_mask[available]] if name.startswith('frozen') else available
    ptree=cKDTree(rgb[material_available]);q=np.array(sorted(volume));palette_queries=[]
    for x,y,z in q:
        l=x;r=x
        while l>0 and mask[z,l-1]:l-=1
        while r<w-1 and mask[z,r+1]:r+=1
        cx=(l+r)/2;rad=max(2,(r-l)*.44);cy=depth[z,int(round(cx))]
        if tree and begin<=z<end:cy=np.interp(z,main[:,2],main[:,1])
        if not tree:
            candidates=np.flatnonzero(safe[z]&(np.arange(w)>=left))
            if len(candidates)>=3:
                strips=np.split(candidates,np.where(np.diff(candidates)>1)[0]+1);strip=max(strips,key=len)
                cx=(strip[0]+strip[-1])/2;rad=max(1,(strip[-1]-strip[0])*.46);cy=0
        v=((y-cy+rad)%(4*rad));v=v if v<=2*rad else 4*rad-v;v-=rad
        sx=int(np.clip(round(cx+v),0,w-1));sz=int(z)
        if not safe[sz,sx]:sz,sx=map(int,fill[:,sz,sx])
        side=rgb[idx[sz,sx]]
        # Rear grain retains local shading and avoids copying front cavities.
        bx=int(np.clip(x+2*math.sin((y-cy)/max(2,rad)),0,w-1));bz=int(z)
        local=np.clip(.5*low[bz,bx]+.5*base,base*.8,base*1.3)
        rear=local*grain[bz,bx]
        facing=abs(x-(l+r)/2)/max(1,(r-l)/2)
        sideweight=np.clip((facing-.25)*1.7,0,1)
        palette_queries.append(side*sideweight+rear*(1-sideweight))
    colors=material_available[ptree.query(np.array(palette_queries))[1]];vox={tuple(v):int(c) for v,c in zip(q,colors)}
    if name.startswith('frozen'):
        snow=np.array([c for c in available if snow_mask[c]])
        lo=q.min(0);occupancy=np.zeros(q.max(0)-lo+3,float);occupancy[tuple((q-lo+1).T)]=1
        gradients=np.array(np.gradient(gaussian_filter(occupancy,2.0)))
        near_snow=distance_transform_edt(~(mask & snow_mask[idx]))
        for x,y,z in volume:
            g=gradients[:,x-lo[0]+1,y-lo[1]+1,z-lo[2]+1]
            upward=g[2]/max(1e-6,np.linalg.norm(g))
            supported=sum((x+dx,y+dy,z+3) in volume for dx,dy in ((2,0),(-2,0),(0,2),(0,-2)))>=3
            if len(snow) and upward>.72 and supported and near_snow[z,x]<5 and (x,y,z-1) not in volume:
                vox[x,y,z]=int(snow[(x//3+y//4+z)%len(snow)])
    front={}
    for x,y,z in vox:front[x,z]=min(front.get((x,z),y),y)
    assert set(front)==set(p)
    for (x,z),y in front.items():vox[x,y,z]=p[x,z]
    return vox,components

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--names',nargs='*');args=parser.parse_args()
    root=args.root;art=root/ART;plans=json.loads((art/'plans.json').read_text());palette=(root/'tutnt/PLAYPAL.pal').read_bytes()[:768]
    records=[]
    for name,plan in plans.items():
        source=root/'tutnt/patches/deadwood'/f'{name}.lmp';raw=source.read_bytes();w,h,left,top,p=patch(raw)
        output=art/(name+'.npz')
        if not plan.get('approved_reference') and (not args.names or name in args.names):
            vox,components=sculpt(p,w,h,left,name,palette,plan)
            np.savez_compressed(output,xyz=np.array(list(vox),np.int16),colors=np.array(list(vox.values()),np.uint8))
            print(name,len(vox),'voxels;',components,'source-connected components',flush=True)
        if not output.exists():raise ValueError('Missing authored grid '+str(output))
        records.append({'name':name,'source_sha256':hashlib.sha256(raw).hexdigest(),'grid_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'palette_sha256':hashlib.sha256(palette).hexdigest(),'approved_reference':bool(plan.get('approved_reference'))})
    (art/'sources.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
