"""Pixel-scale solid geometry for UTNT's original low-resolution pickup/prop art.

Coordinates in Sculpt are x/right, y/back, z/up. No image resampling or hires
replacement is used. Each builder describes the object's actual construction.
"""
import math

class Sculpt:
    def __init__(self, pixels, width, height, palette):
        self.v={};self.p=pixels;self.w=width;self.h=height;self.pal=palette
    def sample(self,x,z):
        x=max(0,min(self.w-1,round(x)));z=max(0,min(self.h-1,round(z)))
        if (x,z) not in self.p:
            x,z=min(self.p,key=lambda p:(p[0]-x)**2+(p[1]-z)**2)
        return self.p[x,z]
    def box(self,x0,x1,y0,y1,z0,z1,c):
        for x in range(round(x0),round(x1)+1):
            for y in range(round(y0),round(y1)+1):
                for z in range(round(z0),round(z1)+1):self.v[x,y,z]=c(x,y,z) if callable(c) else c
    def packed(self):
        lo=[min(p[k] for p in self.v) for k in range(3)];hi=[max(p[k] for p in self.v) for k in range(3)]
        dims=[hi[k]-lo[k]+1 for k in range(3)]
        vox={(x-lo[0],y-lo[1],hi[2]-z):c for (x,y,z),c in self.v.items()}
        # All sculpted objects stand on the authored floor. Runtime actor defaults
        # still define collision, scaling, pickup handling and float-bob.
        return vox,tuple(dims),(dims[0]/2,dims[1]/2,dims[2])

def lathe_part(s,x0,x1,z0,z1,cy,depthscale=1):
    """Revolve a source silhouette: actual round canisters, caps and metal rings."""
    for z in range(z0,z1+1):
        row=[x for x,zz in s.p if zz==z and x0<=x<=x1]
        if not row:continue
        center=(min(row)+max(row))/2;rx=(max(row)-min(row)+1)/2
        ry=rx*depthscale
        for x in row:
            d=math.sqrt(max(0,1-((x-center)/rx)**2))*ry
            for y in range(math.ceil(cy-d),math.floor(cy+d)+1):
                c=s.p[x,z]
                # Image contains original material bands; sample across the round
                # section instead of stretching the front into a rectangular slab.
                if abs(y-cy)<d-1:c=s.sample(center+(x-center)*.7,z)
                s.v[x,y,s.h-1-z]=c

def profile(s,kind):
    """Assemblies with cylindrical barrels/tanks, thin rails, hoses and grips."""
    if kind=='gas':lathe_part(s,0,s.w-1,0,s.h-1,0)
    elif kind=='biggas':
        lathe_part(s,0,10,0,s.h-1,0);lathe_part(s,12,s.w-1,0,s.h-1,0)
        for (x,z),c in s.p.items():
            if x==11:s.box(x,x,-2,2,s.h-1-z,s.h-1-z,c)
    else:
        for (x,z),c in s.p.items():
            if kind=='flamer':
                if x<17:continue
                r=2 if z<15 or z>25 else 5
                if x<25:r=4
            elif kind=='pyro':
                if x<27 and z>=6:continue
                r=1.5 if z<12 else 5.5
                if z>27:r=2
            else: # lowres minigun: receiver, open stock, ammo belt and barrel cluster
                r=2 if x<20 else 4
                if z>s.h*.60:r=1.5
            column=[zz for xx,zz in s.p if xx==x]
            center=(min(column)+max(column))/2
            if kind=='minigun' and x>28:
                # Vary circular section through the main six-barrel assembly.
                rr=max(2,(max(column)-min(column)+1)/2)
                r=max(1,r*math.sqrt(max(0,1-((z-center)/rr)**2)))
            for y in range(-round(r),round(r)+1):s.v[x,y,s.h-1-z]=c
        if kind=='flamer':lathe_part(s,0,16,0,s.h-1,0)
        if kind=='pyro':
            lathe_part(s,0,12,6,s.h-1,0);lathe_part(s,14,26,6,s.h-1,0)
        if kind=='minigun':
            # The source shows the assembly from the side. Put real axial bores
            # in the muzzle: these remain holes when viewed along the barrel.
            xs=sorted({x for x,y,z in s.v if x>=s.w-4})
            for x in xs:
                for y in (-2,0,2):
                    for z in (s.h//2-2,s.h//2+1):s.v.pop((x,y,z),None)
    return s.packed()

def heart(s):
    def is_red(c):
        r,g,b=s.pal[c*3:c*3+3];return r>g*2+12 and r>b*2+12
    rows={}
    for (x,z),c in s.p.items():
        if not is_red(c):rows.setdefault(z,[]).append(x)
    for (x,z),c in s.p.items():
        if z<12:r=1
        else:
            row=rows.get(z,[])
            if not row or x<min(row) or x>max(row):continue
            rx=max(1,(max(row)-min(row)+1)/2);cx=(max(row)+min(row))/2
            r=max(1,round(7*math.sqrt(max(0,1-((x-cx)/rx)**2))*min(1,(s.h-z)/9)))
        for y in range(-r,r+1):
            color=c
            if z>=12 and abs(y)<r and is_red(c):color=s.sample(sum(rows[z])/len(rows[z]),z)
            s.v[x,y,s.h-1-z]=color
    return s.packed()

def candelabra(s):
    for z in range(s.h):
        xs=sorted(x for x,zz in s.p if zz==z)
        if not xs:continue
        groups=[]
        for x in xs:
            if not groups or x>groups[-1][-1]+1:groups.append([])
            groups[-1].append(x)
        for g in groups:
            cx=(g[0]+g[-1])/2;rx=(g[-1]-g[0]+1)/2
            # Wax candles, branching metal tubes and a wider solid foot.
            depth=min(2.2,rx) if z<s.h-10 else min(7,rx*.7)
            for x in g:
                r=max(.7,depth*math.sqrt(max(0,1-((x-cx)/rx)**2)))
                for y in range(-round(r),round(r)+1):s.v[x,y,s.h-1-z]=s.p[x,z]
    return s.packed()

BUILDERS={'gas':lambda s:profile(s,'gas'),'biggas':lambda s:profile(s,'biggas'),
 'flamer':lambda s:profile(s,'flamer'),'pyro':lambda s:profile(s,'pyro'),
 'minigun':lambda s:profile(s,'minigun'),'heart':heart,
 'barrel':lambda s:(lathe_part(s,0,s.w-1,0,s.h-1,0),s.packed())[1],
 'candelabra':candelabra}

def build(kind,pixels,width,height,palette):
    return BUILDERS[kind](Sculpt(pixels,width,height,palette))
