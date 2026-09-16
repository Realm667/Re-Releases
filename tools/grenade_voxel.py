"""Author the small Quake-inspired grenade from an editable octagonal profile.
Run tools/build_voxels.py explicitly to regenerate the committed KVX and fallback.
"""
from pathlib import Path
import json, math, struct

def geometry(root):
    source=Path(root)/'tutnt/voxels/source/grenade.json'
    spec=json.loads(source.read_text())
    palette=(Path(root)/'tutnt/PLAYPAL.pal').read_bytes()[:768]
    colors=[tuple(palette[i:i+3]) for i in range(0,768,3)]
    def color(rgb):
        return min(range(1,256),key=lambda i:sum((colors[i][k]-rgb[k])**2 for k in range(3)))
    dims=spec['dimensions']; vox={}; profile=spec['profile']
    for z in range(dims[2]):
        lo,hi=next((a,b) for a,b in zip(profile,profile[1:]) if a[0]<=z<=b[0])
        radius=lo[1]+(hi[1]-lo[1])*(z-lo[0])/(hi[0]-lo[0])
        red=any(a<=z<=b for a,b in spec['bands'])
        for x in range(dims[0]):
            for y in range(dims[1]):
                dx=x+0.5-dims[0]/2; dy=y+0.5-dims[1]/2
                if max(abs(dx),abs(dy))+0.41421356*min(abs(dx),abs(dy))>radius: continue
                # Broad facets, narrow worn longitudinal edges, restrained pixel variation.
                shade=0.88+0.12*math.cos(math.atan2(dy,dx)+1.3)
                if not red and 14<=z<=34 and abs(abs(dx)-abs(dy))<0.65: shade+=0.20
                shade+=(((x*17+y*11+z*3)%7)-3)*0.012
                rgb=[min(255,round(c*shade)) for c in spec['red' if red else 'metal']]
                vox[x,y,z]=color(rgb)
    return vox,tuple(dims),tuple(spec['pivot']),palette,source

def fallback(vox,dims):
    # Native indexed Doom patch, centered like the voxel; also works without voxels.
    w,_,h=dims; columns=[]
    for x in range(w):
        pixels={z:vox[x,min(y for xx,y,zz in vox if xx==x and zz==z),z]
                for z in range(h) if any(xx==x and zz==z for xx,y,zz in vox)}
        column=bytearray();z=0
        while z<h:
            if z not in pixels: z+=1;continue
            first=z;run=[]
            while z<h and z in pixels:run.append(pixels[z]);z+=1
            column.extend(bytes([first,len(run),0])+bytes(run)+b'\0')
        columns.append(bytes(column)+b'\xff')
    head=struct.pack('<hhhh',w,h,w//2,h//2);offset=8+4*w;table=[]
    for col in columns:table.append(offset);offset+=len(col)
    return head+struct.pack('<'+'I'*w,*table)+b''.join(columns)
