"""Native wall skyboxes for three TNT03A2 fissures, applied only to package bytes."""
import hashlib,json,math,re,struct
from build_lava_lips import tex
from build_environment_fx import inside
from build_sky_edges import plane

MARKER='// UTNT_CAVERN_SKYROOMS_V1'
# One eighth camera travel represents scenery at eight times its model distance.
# Shrink texture features to one eighth of their normal map-unit size as well.
SKY_TEXTURE_SCALE=4.0 # rock is now twice its original foreground size
SKY_LAVA_SCALE=8.0

def textmap_digest(data):
    # Fingerprint the topology and placement inputs, normalizing editor number
    # formatting. Unrelated midtexture collision flags do not affect the recesses.
    _,count,offset=struct.unpack_from('<4sII',data)
    raw=None
    for i in range(count):
        start,size,name=struct.unpack_from('<II8s',data,offset+i*16)
        if name.rstrip(b'\0')==b'TEXTMAP':raw=data[start:start+size].decode('utf-8')
    if raw is None:raise ValueError('Missing TEXTMAP')
    raw=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',lambda m:m[0] if m[0].startswith('"') else '',raw,flags=re.S)
    canonical={}
    for kind in ('vertex','sector','sidedef','linedef'):
        rows=[]
        for i,body in enumerate(re.findall(r'\b'+kind+r'\s*\{([^}]*)\}',raw)):
            fields=dict(re.findall(r'(\w+)\s*=\s*([^;]+);',body))
            if kind=='linedef' and i not in (4783,4729,4969):
                fields={k:v for k,v in fields.items() if k in ('v1','v2','sidefront','sideback','id','special','arg0','arg1','arg2','arg3','arg4')}
            for key,value in fields.items():
                try:fields[key]=float(value)
                except ValueError:fields[key]=value.strip()
            rows.append(fields)
        canonical[kind]=rows
    return hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def generate(b,geo,add,source):
    positions=[(float(v['x']),float(v['y'])) for v in b['vertex']]
    counts={k:len(v) for k,v in b.items()};blocks=[];changes={'linedef':{},'sidedef':{}};windows=[];sky_sectors=set()
    def block(kind,**fields):
        index=counts.get(kind,0);counts[kind]=index+1
        blocks.append(kind+' { '+' '.join(k+'='+str(v)+';' for k,v in fields.items())+' }')
        return index
    def vertex(x,y):
        positions.append((x,y))
        return block('vertex',x=f'{x:.6f}',y=f'{y:.6f}')
    def side(sector,texture='IKWALL44'):
        scale={axis+'_'+part:SKY_TEXTURE_SCALE for axis in ('scalex','scaley') for part in ('top','mid','bottom')} if sector in sky_sectors else {}
        rock='IKWALL44' if sector in sky_sectors else 'UCAVROCK'
        return block('sidedef',sector=sector,texturemiddle=json.dumps(rock if texture=='IKWALL44' else texture),texturetop=json.dumps(rock),texturebottom=json.dumps(rock),**scale)
    def line(a,c,sector,**fields):return block('linedef',v1=a,v2=c,sidefront=side(sector),blocking='true',**fields)
    def sector(floor,ceiling,light=150,fade=0x302a24,floor_texture="QLAVA",fog=10,**fields):
        return block('sector',heightfloor=floor,heightceiling=ceiling,texturefloor=json.dumps(floor_texture),textureceiling=json.dumps('IKWALL44' if floor_texture=='UCAVSLAV' else 'UCAVROCK'),lightlevel=light,fadecolor=fade,fogdensity=fog,**fields)
    used={int(s.get('id',0)) for kind in ('sector','linedef') for s in b[kind]}
    assert not used.intersection(range(65200,65500)),'Reserved cavern skybox tags are in use'
    for j,li in enumerate((4783,4729,4969)):
        l=b['linedef'][li];assert 'sideback' not in l and int(l.get('special',0))==0
        sd=int(l['sidefront']);si=int(b['sidedef'][sd]['sector']);s=b['sector'][si]
        a=tuple(float(b['vertex'][int(l['v1'])][k]) for k in ('x','y'))
        c=tuple(float(b['vertex'][int(l['v2'])][k]) for k in ('x','y'))
        span=math.dist(a,c);t=((c[0]-a[0])/span,(c[1]-a[1])/span);n=(t[1],-t[0]);mid=tuple((a[k]+c[k])/2 for k in range(2))
        assert tex(b['sidedef'][sd],'texturemiddle')=='IKWALL44'
        # Pockets lie behind existing boundary walls and cannot consume another room.
        for u in (.05,.25,.5,.75,.95):
            for depth in (8,48,96):
                p=(a[0]+(c[0]-a[0])*u-n[0]*depth,a[1]+(c[1]-a[1])*u-n[1]*depth)
                assert not any(inside(p,ee) for ee in geo.values()),('Occupied skybox pocket',li,p)
        bottom=max(plane(s,mid,'floor')+48,-920);top=min(plane(s,mid)-48,bottom+(900 if j==2 else 540))
        assert top-bottom>=300
        pocket=sector(round(bottom),round(top),138,0x363029)
        backside=side(pocket,'-')
        changes['linedef'][str(li)]={'sideback':str(backside),'twosided':'true','blocking':'true'}
        changes['sidedef'][str(sd)]={'texturemiddle':'"-"','texturetop':'"IKWALL44"','texturebottom':'"IKWALL44"'}
        af=vertex(a[0]-n[0]*96,a[1]-n[1]*96);cf=vertex(c[0]-n[0]*96,c[1]-n[1]*96)
        line(int(l['v1']),af,pocket)
        portal=line(af,cf,pocket,id=65400+j,special=57,arg0=0,arg1=5,arg3=65200+j)
        line(cf,int(l['v2']),pocket)
        windows.append({'line':li,'portal_line':portal,'sector':si,'pocket':pocket,'center':[*mid,(bottom+top)/2],'normal':n,'bottom':bottom,'top':top})

        # A deep irregular rock frame masks the rectangular engine aperture.
        inner=[(-.08,-.46),(.17,-.42),(.30,-.28),(.24,-.04),(.40,.14),(.30,.30),(.08,.46),(-.08,.47),(-.26,.30),(-.20,.1),(-.36,-.1),(-.27,-.29),(-.24,-.41)]
        outer=[(0,-.5),(.5,-.5),(.5,-.3),(.5,-.05),(.5,.15),(.5,.5),(.2,.5),(-.5,.5),(-.5,.3),(-.5,.1),(-.5,-.1),(-.5,-.5),(-.2,-.5)]
        # Four samples per original contour segment, seven radial bands. The
        # exterior sinks well into the wall and never ends at a visible rectangle.
        contour=[]
        for k in range(len(inner)):
            for q in range(4):
                f=q/4;u,v=inner[k];nu,nv=inner[(k+1)%len(inner)]
                ou,ov=outer[k];no,nv2=outer[(k+1)%len(outer)]
                jitter=math.sin(q*math.pi/4)*math.sin(k*3.7+j)*.015
                contour.append((u+(nu-u)*f+jitter,v+(nv-v)*f+jitter,ou+(no-ou)*f,ov+(nv2-ov)*f))
        verts=[];faces=[];height=top-bottom;zmid=(top+bottom)/2;count=len(contour)
        for ring in range(7):
            f=ring/6
            for k,(u,v,ou,ov) in enumerate(contour):
                x=ou*(span+220)*(1-f)+u*span*f
                z=ov*(height+240)*(1-f)+v*height*f
                ridge=(math.sin(k*.77+j)*12+math.sin(k*1.81+ring*.8)*7)*math.sin(math.pi*f)
                depth=-48*(1-f)+72*math.sin(math.pi*f)+22*f+ridge
                verts.append((mid[0]+t[0]*x+n[0]*depth,mid[1]+t[1]*x+n[1]*depth,zmid+z))
        for ring in range(6):
            for k in range(count):
                a0=ring*count+k;c0=ring*count+(k+1)%count;d=a0+count;e=c0+count
                faces.extend(((a0,c0,d),(c0,e,d)))
        for k,f in enumerate(faces):
            v0,v1,v2=[verts[q] for q in f];u=[v1[q]-v0[q] for q in range(3)];v=[v2[q]-v0[q] for q in range(3)]
            normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2])
            if normal[0]*n[0]+normal[1]*n[1]<0:faces[k]=(f[0],f[2],f[1])
        add(f'fissure_{j}',verts,faces,(mid[0]+n[0]*12,mid[1]+n[1]*12,zmid),'IKWALL44',4)

        # Two large connected halls per skybox. Each has independent native
        # perspective, depth testing and fog, with a client-local parallax viewpoint anchored to SkyCamCompat.
        ox,oy=((-11000,-23000),(1000,-23000),(-11000,-12000))[j]
        windows[-1]['view_origin']=[ox-1200,oy+(-350,350,-150)[j],-450]
        room=sector(-650,2200,128,0x363029,floor_texture="UCAVSLAV",fog=6,lightfloor=112,lightfloorabsolute='true',lightceiling=96,lightceilingabsolute='true',id=65300+j,
                    **{axis+'scale'+plane:(SKY_LAVA_SCALE if plane=='floor' else SKY_TEXTURE_SCALE) for axis in ('x','y') for plane in ('floor','ceiling')})
        sky_sectors.add(room)
        outline=[(-2400,-1400),(-2600,800),(-1300,2100),(1600,2200),(2800,900),(3300,600),(3900,1100),(5400,1700),(7200,1400),(7800,0),(7200,-1800),(4900,-1900),(3600,-800),(2900,-700),(2000,-2200),(-1000,-2200)]
        vv=[vertex(ox+x,oy+y) for x,y in outline]
        for k in range(len(vv)):
            extra={'special':57,'arg0':65200+j,'arg1':2,'arg2':1} if k==0 else {}
            line(vv[k],vv[(k+1)%len(vv)],room,**extra)
        yaw=math.degrees(math.atan2(-n[1],-n[0]))
        block('thing',x=ox-1200,y=oy+(-350,350,-150)[j],height=200,type=9083,id=65200+j,angle=round(-yaw+(-8,10,0)[j])%360,skill1='true',skill2='true',skill3='true',skill4='true',skill5='true',single='true',coop='true',dm='true')
        # Void pillars are real occluders; their unequal sizes expose the second hall.
        for k,(x,y,radius) in enumerate(((-850,-1450,190),(-200,-1900,230),(700,-1150,430),(1700,1350,540),(4800,-1050,510),(6200,850,460))):
            vv=[]
            for q in range(9):
                angle=q*math.tau/9;rr=radius*(1+.13*math.sin(q*2.1+k+j))
                vv.append(vertex(ox+x+math.cos(angle)*rr,oy+y+math.sin(angle)*rr))
            for q in range(9):line(vv[q],vv[(q+1)%9],room)
        # Hanging rock silhouettes make the high roof readable at a distance.
        for k,(x,y,radius,length) in enumerate(((400,950,230,1300),(2500,-1100,300,1500),(4600,900,260,1700))):
            verts=[];faces=[]
            for ring in range(5):
                scale=(1.2,.85,.55,.22,.015)[ring]
                for q in range(9):
                    angle=q*math.tau/9;rr=radius*scale*(1+.14*math.sin(q*2.7+k+j))
                    verts.append((ox+x+math.cos(angle)*rr+ring*21,oy+y+math.sin(angle)*rr-ring*14,2240-length*ring/4))
            for ring in range(4):
                for q in range(9):
                    a0=ring*9+q;c0=ring*9+(q+1)%9;d=a0+9;e=c0+9;faces.extend(((a0,d,c0),(c0,d,e)))
            add(f'skyrock_{j}_{k}',verts,faces,(ox+x,oy+y,2100),'IKWALL44',5,sector_override=room,uv_scale=SKY_TEXTURE_SCALE)
    assert all(max(p[k] for p in positions)-min(p[k] for p in positions)<32760 for k in (0,1)), 'Cavern skybox BSP extent exceeded'
    return {'version':1,'textmap_sha256':textmap_digest(source),'counts':{k:len(v) for k,v in b.items()},'changes':changes,'append':MARKER+'\n'+'\n'.join(blocks)+'\n','windows':windows,'models':12}


def apply(data,spec):
    """Preserve original lumps and indices; rebuild BSP nodes in the engine."""
    magic,count,offset=struct.unpack_from('<4sII',data);entries=[]
    for i in range(count):
        a,n,name=struct.unpack_from('<II8s',data,offset+i*16);key=name.rstrip(b'\0');raw=data[a:a+n]
        if key in (b'ZNODES',b'BLOCKMAP',b'REJECT'):continue
        if key==b'TEXTMAP':
            text=raw.decode('utf-8');assert MARKER not in text,'Skybox map patch applied twice'
            assert textmap_digest(data)==spec['textmap_sha256'],'Cavern skybox source changed; regenerate the map patch'
            for kind,expected in spec['counts'].items():
                assert len(re.findall(r'\b'+kind+r'\s*(?://[^\n]*\n\s*)?\{',text))==expected,('Skybox source topology changed',kind)
            for kind,edits in spec['changes'].items():
                index=-1
                def replace(m):
                    nonlocal index
                    index+=1;body=m[0]
                    for key,value in edits.get(str(index),{}).items():
                        pattern=r'\b'+key+r'\s*=\s*[^;]+;'
                        if re.search(pattern,body):body=re.sub(pattern,key+' = '+value+';',body)
                        else:body=body[:-1]+' '+key+' = '+value+';\n}'
                    return body
                text=re.sub(r'\b'+kind+r'\s*(?://[^\n]*\n\s*)?\{[^}]*\}',replace,text)
            raw=(text+'\n'+spec['append']).encode('utf-8')
        entries.append((name,raw))
    body=bytearray();directory=bytearray()
    for name,raw in entries:
        directory+=struct.pack('<II8s',12+len(body),len(raw),name);body+=raw
    return struct.pack('<4sII',magic,len(entries),12+len(body))+body+directory


def package_skyrooms(payload):
    key='cavern/skyrooms.json'
    if key in payload:payload['maps/tnt03a2.wad']=apply(payload['maps/tnt03a2.wad'],json.loads(payload[key]))
    return payload
