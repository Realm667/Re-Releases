"""Map-fitted cliff skirts, corner ribs and lava-foot rock fans for TNT03A2."""
import math
from build_lava_lips import tex
from build_environment_fx import inside
from build_sky_edges import plane


def generate_details(b, geo, lava, add):
    walls={}; counts={'rims':0,'corners':0,'feet':0}; checks=[]
    for si in sorted(lava):
        for a,c,li,side in geo[si]:
            line=b['linedef'][li]
            oi=int(line.get('sideback' if int(line['sidefront'])==side else 'sidefront',-1))
            if oi<0 or li==4876:continue # lava-fall mouth stays open
            other=b['sector'][int(b['sidedef'][oi]['sector'])]
            span=math.dist(a,c)
            if span<100 or not -800<=float(other.get('heightfloor',0))<=0:continue
            if tex(b['sidedef'][side],'texturebottom')!='IKWALL44':continue
            tangent=((c[0]-a[0])/span,(c[1]-a[1])/span)
            normal=(tangent[1],-tangent[0])
            walls[li]=(a,c,other,span,tangent,normal)

    def emit(name,verts,faces,origin,limit,outward):
        # The whole cosmetic mesh stays below the adjacent walkable surface.
        assert all(z<=limit(x,y)-7.9 for x,y,z in verts),name
        for j,f in enumerate(faces):
            a,c,d=[verts[i] for i in f]
            u=[c[k]-a[k] for k in range(3)];v=[d[k]-a[k] for k in range(3)]
            n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            assert sum(q*q for q in n)>1e-10,('Degenerate cavern face',name,j)
            if sum(n[k]*outward[k] for k in range(3))<0:faces[j]=(f[0],f[2],f[1])
        checks.append((name,len(verts),len(faces),min(limit(x,y)-z for x,y,z in verts)))
        add(name,verts,faces,origin,'IKWALL44',3)

    def grid_faces(rows,cols):
        faces=[]
        for j in range(rows-1):
            for k in range(cols-1):
                a=j*cols+k;faces.extend([(a,a+cols,a+1),(a+1,a+cols,a+cols+1)])
        return faces

    for li,(a,c,s,span,t,n) in sorted(walls.items()):
        if span<170:continue
        # Folded edge: it starts behind the cliff, curls outward below its top,
        # and returns into the rock. End taper avoids seams at neighbouring faces.
        verts=[];steps=max(5,math.ceil(span/42))
        for j in range(steps+1):
            u=j/steps;px=a[0]+(c[0]-a[0])*u;py=a[1]+(c[1]-a[1])*u
            taper=math.sin(math.pi*u)**.6
            variation=1+.18*math.sin(j*2.1+li)+.10*math.cos(j*3.7)
            for depth,drop in [(-10,8),(18,24),(42,66),(28,122),(-14,186)]:
                offset=-10+(depth+10)*taper*variation
                x=px+n[0]*offset;y=py+n[1]*offset
                verts.append((x,y,plane(s,(x,y),'floor')-8-(drop-8)*variation))
        mid=((a[0]+c[0])/2,(a[1]+c[1])/2)
        origin=(mid[0]+n[0]*12,mid[1]+n[1]*12,plane(s,mid,'floor')-88)
        emit(f'rim_{li}',verts,grid_faces(steps+1,5),origin,lambda x,y:plane(s,(x,y),'floor'),(*n,0))
        counts['rims']+=1

        # Sparse, partly submerged talus at the cliff foot. Group three unequal
        # mounds in one mesh/actor; they never imply safe islands in the lava.
        if span<190 or li%3==0:continue
        verts=[];faces=[]
        for mound in range(3):
            u=.26+mound*.23;cx=a[0]+(c[0]-a[0])*u;cy=a[1]+(c[1]-a[1])*u
            width=min(64,span*.20)*(1+.14*math.sin(li+mound*3))
            reach=54+mound*17+(li%4)*7;height=65+(li%5)*13+mound*19
            base=len(verts)
            for row in range(4):
                along=row/3
                for k in range(7):
                    across=(k/6-.5)*2
                    x=cx+t[0]*across*width+n[0]*(along*reach-14)
                    y=cy+t[1]*across*width+n[1]*(along*reach-14)
                    z=-1520+height*math.sin(math.pi*(1-along)*.5)*max(0,1-across*across)
                    verts.append((x,y,z))
            faces.extend(tuple(base+i for i in f) for f in grid_faces(4,7))
        emit(f'foot_{li}',verts,faces,(mid[0]+n[0]*18,mid[1]+n[1]*18,-1460),lambda x,y:plane(s,(x,y),'floor'),(0,0,1))
        counts['feet']+=1

    junctions={}
    for li,w in walls.items():
        for endpoint in w[:2]:junctions.setdefault(endpoint,[]).append(li)
    for point,ids in sorted(junctions.items()):
        if len(ids)!=2:continue
        first,second=(walls[i] for i in ids);n1=first[5];n2=second[5]
        dot=sum(x*y for x,y in zip(n1,n2))
        if not .25<dot<.94:continue # retain straight stretches and tight openings
        nx=n1[0]+n2[0];ny=n1[1]+n2[1];length=math.hypot(nx,ny);nx/=length;ny/=length
        if not any(inside((point[0]+nx*32,point[1]+ny*32),geo[si]) for si in lava):continue
        limit=lambda x,y:min(plane(w[2],(x,y),'floor') for w in (first,second))
        top=limit(*point)
        if abs(plane(first[2],point,'floor')-plane(second[2],point,'floor'))>160:continue
        arms=[]
        for w in (first,second):
            other=w[1] if w[0]==point else w[0];scale=min(100,w[3]*.38)/w[3]
            arms.append((point[0]+(other[0]-point[0])*scale,point[1]+(other[1]-point[1])*scale))
        verts=[];seed=min(ids)
        for j in range(9):
            down=j/8;bulge=math.sin(math.pi*down)**.65*(65+seed%29)
            for k in range(7):
                u=k/6
                # Two wall shoulders meet in a faceted, tapered corner spine.
                left=arms[0] if u<=.5 else arms[1];q=1-abs(u-.5)*2
                x=left[0]*(1-q)+point[0]*q+nx*(bulge*q-12)
                y=left[1]*(1-q)+point[1]*q+ny*(bulge*q-12)
                z=limit(x,y)-110-down*(top+1500-200)
                verts.append((x,y,z))
        origin=(point[0]+nx*20,point[1]+ny*20,(top-1500)/2)
        emit('corner_'+'_'.join(map(str,sorted(ids))),verts,grid_faces(9,7),origin,limit,(nx,ny,0))
        counts['corners']+=1
    assert counts['rims']>=16 and counts['corners']>=8 and counts['feet']>=6,counts
    return counts,checks
