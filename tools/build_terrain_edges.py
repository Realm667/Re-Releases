"""Material-aware outdoor ledges and shallow wall-foot deposits.

The sky-edge builder owns output registration. These functions only inspect map
geometry and return cosmetic meshes; no source WAD or collision is changed.
"""
from pathlib import Path
import collections,math
from build_sky_edges import plane,wall_uv,connect,ridge
from build_lava_lips import tex,point,plus,sub,norm

NATURAL={'rock','grass','soil','gravel','snow','snowrock','ice'}

def kind(v):
    p=v.get('profile','')
    return 'snow' if p in ('snow','snowrock','ice') else p

def floor_mapping(root,mapname):
    path=Path(root)/'tutnt/areaalign'/f'{mapname.lower()}.txt'
    result={}
    if path.exists():
        for line in path.read_text().splitlines():
            r=line.split('|')
            if r[0]=='F' and r[2]=='0':result[int(r[1])]=r
    return result

def scrolling_floor(sec):
    # Hexen directional floor scrollers are material motion, not static terrain.
    special=int(sec.get('special',0)) & 255
    return 201<=special<=224 or any(abs(float(sec.get(k,0)))>1e-8 for k in ('scroll_floor_x','scroll_floor_y'))

def floor_uv(sec,index,variants,bindings):
    skin=tex(sec,'texturefloor');ox=float(sec.get('xpanningfloor',0));oy=float(sec.get('ypanningfloor',0))
    if index in bindings:
        r=bindings[index]
        if r[3]!=skin:raise ValueError('Stale terrain floor binding')
        skin=r[4];ox=float(r[5]);oy=float(r[6])
    w,h=variants[skin]['logical']
    return dict(skin=skin,width=w,height=h,sx=float(sec.get('xscalefloor',1)),sy=float(sec.get('yscalefloor',1)),ox=ox,oy=oy,angle=float(sec.get('rotationfloor',0)))

def floor_coord(c,p):
    # Same order as hw_SetPlaneTextureRotation: rotate, size, offset, scale.
    a=math.radians(c['angle']);co,si=math.cos(a),math.sin(a);x,y=p
    return ((x*co-y*si+c['ox'])*c['sx']/c['width'],(-x*si-y*co+c['oy'])*c['sy']/c['height'])

def detect_terrain(b,variants,wall_bindings=None,floor_bindings=None):
    wall_bindings=wall_bindings or {};floor_bindings=floor_bindings or {};edges=[]
    from build_environment_fx import geometry,inside
    geo=geometry(b)
    for index,l in enumerate(b['linedef']):
        # Moving/polyobject, horizon and portal edges need separate treatment.
        if int(l.get('special',0)) not in (0,181,118):continue
        for face,key in enumerate(('sidefront','sideback')):
            si=int(l.get(key,-1));oi=int(l.get(('sideback','sidefront')[face],-1))
            if si<0:continue
            side=b['sidedef'][si];front_id=int(side['sector']);front=b['sector'][front_id]
            if tex(front,'textureceiling')!='F_SKY1':continue
            back_id=int(b['sidedef'][oi]['sector']) if oi>=0 else -1
            back=b['sector'][back_id] if back_id>=0 else None
            part=1 if back is None else 2;texture=tex(side,'texturemiddle' if back is None else 'texturebottom')
            if variants.get(texture,{}).get('profile') not in NATURAL:continue
            a,z=(point(b['vertex'][int(l[k])]) for k in ('v1','v2'))
            if face:a,z=z,a
            length=math.dist(a,z)
            if length<16:continue
            n=norm((z[1]-a[1],a[0]-z[0]));mid=plus(a,sub(z,a),.5)
            if any(abs(float(side.get('scale'+axis+('_mid' if part==1 else '_bottom'),1)))<1e-6 for axis in ('x','y')):continue
            base=dict(line=index,face=face,part=part,front_id=front_id,a=a,b=z,length=length,normal=n,texture=texture,side=side,linedef=l,front=front,back=back)
            wu=wall_uv(base,variants,wall_bindings)
            drop=min(plane(back,p,'floor')-plane(front,p,'floor') for p in (a,z)) if back else math.inf
            # A genuine open plateau: the old closed sky boundary remains separate.
            ledge=back is not None and tex(back,'textureceiling')=='F_SKY1' and drop>=(4 if kind(variants.get(tex(back,'texturefloor'),{})) in ('grass','soil') else 16) and all(plane(back,p)-plane(back,p,'floor')>=56 for p in (a,z))
            floor_profile=variants.get(tex(back,'texturefloor'),{}).get('profile') if back else None
            if ledge and floor_profile in NATURAL and not scrolling_floor(back):
                fu=floor_uv(back,back_id,variants,floor_bindings)
                if abs(fu['sx']*fu['sy'])<1e-6:continue
                radius=min(8,drop*.16);family=variants[fu['skin']]['family'];surface_kind=kind(variants[fu['skin']])
                # Require room for the cap on the actual upper floor polygon.
                if not all(inside(plus(plus(a,sub(z,a),u),n,-radius*.85),geo[back_id]) for u in (.2,.5,.8)):continue
                for layer in (0,1):
                    e=base|dict(mode=1,layer=layer,top_id=back_id,top=back,top_part='floor',surface_id=back_id,surface=back,surface_kind=surface_kind,fu=fu,wu=wu,radius=radius,kind=surface_kind if layer else kind(variants[wu['skin']]),family=family if layer else variants[wu['skin']]['family'],uv=fu if layer else wu)
                    e.update(h0=plane(back,a,'floor'),h1=plane(back,z,'floor'));edges.append(e)
            low_profile=variants.get(tex(front,'texturefloor'),{}).get('profile')
            wall_height=min(plane(front,p)-plane(front,p,'floor') for p in (a,z)) if back is None else drop
            # Selected broad wall feet, not every step or narrow corridor.
            if length>=96 and wall_height>=64 and low_profile in NATURAL and not scrolling_floor(front) and ridge(mid[0]*.013+mid[1]*.021)>.35:
                fu=floor_uv(front,front_id,variants,floor_bindings)
                if abs(fu['sx']*fu['sy'])<1e-6:continue
                radius=7 if kind(variants[fu['skin']])=='snow' else 5
                if not all(inside(plus(plus(a,sub(z,a),u),n,radius+3),geo[front_id]) for u in (.2,.5,.8)):continue
                e=base|dict(mode=2,layer=1,top_id=front_id,top=front,top_part='floor',surface_id=front_id,surface=front,surface_kind=kind(variants[fu['skin']]),fu=fu,wu=wu,radius=radius,kind=kind(variants[fu['skin']]),family=variants[fu['skin']]['family'],uv=fu)
                e.update(h0=plane(front,a,'floor'),h1=plane(front,z,'floor'));edges.append(e)
    groups=collections.defaultdict(list)
    for e in edges:groups[(e['mode'],e['layer'],e['fu']['skin'],e['wu']['skin'],e['surface_id'])].append(e)
    for group in groups.values():connect(group)
    return edges

class HeightSampler:
    def __init__(self,root,variants):self.root=Path(root);self.variants=variants;self.cache={}
    def sample(self,skin,uv):
        from PIL import Image,ImageFilter
        if skin not in self.cache:
            p=self.root/'tutnt'/(self.variants[skin]['stem']+'-height.png')
            with Image.open(p) as source:
                im=source.convert('L');im=im.filter(ImageFilter.GaussianBlur(max(1,min(im.size)/64)))
                self.cache[skin]=im.copy()
        im=self.cache[skin];x=(uv[0]%1)*im.width;y=(uv[1]%1)*im.height;ix,iy=math.floor(x),math.floor(y);tx,ty=x-ix,y-iy
        value=sum(im.getpixel(((ix+dx)%im.width,(iy+dy)%im.height))*(tx if dx else 1-tx)*(ty if dy else 1-ty) for dx in (0,1) for dy in (0,1))
        # Decode the existing signed POM map. Bound macro influence deliberately.
        return max(-1,min(1,2*(value-127)/255*self.variants[skin]['depth']))

def terrain_mesh(e,sampler=None):
    mid=plus(e['a'],sub(e['b'],e['a']),.5);center=plus(mid,e['normal'],-.5 if e['mode']==1 and e['layer']==1 else .5);h=plane(e['top'],mid,'floor')
    steps=max(4,math.ceil(e['length']/(10 if e['surface_kind']=='grass' else 16)));verts=[];uv=[];faces=[]
    for j in range(steps+1):
        u=j/steps;p=plus(e['a'],sub(e['b'],e['a']),u);m=plus(e['ma'],sub(e['mb'],e['ma']),u)
        ramp=min(1,j/2,(steps-j)/2);r=(e['ra']*(1-u)+e['rb']*u)*(1-ramp)+e['radius']*ramp
        variation=.7+.30*ridge(p[0]*.057+p[1]*.043)+.18*ridge(p[0]*.13-p[1]*.091)
        if sampler:variation+=.12*sampler.sample(e['fu']['skin'],floor_coord(e['fu'],p))
        r=max(.04,r*variation)
        if e['mode']==2:
            pocket=max(.015,min(1,(ridge(p[0]*.017+p[1]*.023)-.18)*1.5))
            r*=pocket;rise=min(2.25,r*.32)
            controls=[(0,rise),(.18, rise*.92),(.48,rise*.55),(.78,rise*.17),(1,0)]
            rows=[(d*r,.045+z) for d,z in controls]
        else:
            # Both layers share the same material junction. Walkable cap rises <=1 unit.
            seam=(.83*r,-.78*r)
            if e['layer']==1:
                fringe=(.18*ridge(p[0]*.39+p[1]*.29) if e['kind']=='grass' else 0)
                rows=[(-.85*r,.045),(-.40*r,.10),(0,min(.65,r*.07)),(.50*r,-.12*r),(.90*r,-(.36+fringe)*r),seam]
            else:
                rows=[seam,(.86*r,-1.03*r),(.45*r,-1.43*r),(.10*r,-1.85*r),(0,-2.12*r)]
        for k,(d,z) in enumerate(rows):
            w=plus(p,m,d+.025);wz=plane(e['top'],w,'floor')+z
            if e['layer']==1:co=floor_coord(e['fu'],w)
            else:
                c=e['wu'];co=((u*e['length']*c['sx']+c['ox'])/c['width'],((c['ref']-wz)*c['sy']+c['oy'])/c['height'])
                if sampler and 0<k<len(rows)-1:
                    # Wall relief affects only interior facets; shared seams stay exact.
                    w=plus(w,m,.24*sampler.sample(c['skin'],co)*math.sin(math.pi*k/(len(rows)-1)))
            verts.append((w[0]-center[0],wz-h,-(w[1]-center[1])));uv.append((co[0],1-co[1]))
    count=len(rows)
    for j in range(steps):
        for k in range(count-1):
            a=j*count+k;b=a+count;faces.extend(((a,b,b+1),(a,b+1,a+1)))
    # Geometry-derived normals include authored slopes and longitudinal relief.
    normals=[[0.,0.,0.] for _ in verts];flat=[]
    for a,b,c in faces:
        v=verts[a];ab=[verts[b][k]-v[k] for k in range(3)];ac=[verts[c][k]-v[k] for k in range(3)]
        n=[ac[1]*ab[2]-ac[2]*ab[1],ac[2]*ab[0]-ac[0]*ab[2],ac[0]*ab[1]-ac[1]*ab[0]]
        size=math.sqrt(sum(x*x for x in n)) or 1;flat.append(tuple(x/size for x in n))
        for index in (a,b,c):normals[index]=[normals[index][k]+n[k] for k in range(3)]
    normals=[tuple(x/(math.sqrt(sum(y*y for y in n)) or 1) for x in n) for n in normals]
    faceted=e['kind'] in ('rock','gravel') and e['layer']==0
    out=['# Generated outdoor terrain edge; cosmetic only.','s 1']
    out+=['v %.6f %.6f %.6f'%v for v in verts];out+=['vt %.8f %.8f'%v for v in uv]
    out+=['vn %.6f %.6f %.6f'%v for v in (flat if faceted else normals)]
    out+=['f '+' '.join(f'{v+1}/{v+1}/{i+1 if faceted else v+1}' for v in f) for i,f in enumerate(faces)]
    return '\n'.join(out)+'\n',center,h,len(faces),verts
