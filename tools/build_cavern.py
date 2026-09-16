"""Build TNT03A2's cosmetic cavern layer; never rewrite the source WAD.

Hand-authored placements are checked against the map. Generated sector bindings
include boundary coordinates so unrelated/reindexed maps cannot inherit the look.
"""
from pathlib import Path
import argparse, json, math
from build_lava_lips import parse, tex
from build_environment_fx import geometry, bounds, inside
from build_sky_edges import resolve_slopes, plane

ROOT = Path(__file__).resolve().parents[1]

def generate(root=ROOT, check=False):
    map_path=root/'tutnt/maps/tnt03a2.wad'
    b=parse(map_path);resolve_slopes(b,map_path);geo=geometry(b)
    outputs={}; rows=[]; models=[]; classes=[]; placements=[]
    for i,s in enumerate(b['sector']):
        if i not in geo or s.get('fadecolor')!='6439197': continue
        box=bounds(geo[i])
        in_room=3700<=box[0] and box[2]<=8000 and -6800<=box[1] and box[3]<=-3180
        cave_sky=s.get('id')=='23' and tex(s,'textureceiling')=='F_SKY1'
        if not (in_room or cave_sky): continue
        a,c,line,side=geo[i][0]
        face=0 if int(b['linedef'][line]['sidefront'])==side else 1
        rows.append('|'.join(map(str,[i,line,face,*a,*c,s.get('id',0)])))
    assert len(rows)>400, 'Cavern selection changed; inspect map before rebuilding'
    outputs['tutnt/cavern/sectors.txt']='\n'.join(rows)+'\n'
    cavern_tags={int(row.split('|')[-1]) for row in rows}
    caps=[]
    for li,l in enumerate(b['linedef']):
        if l.get('special')!='160' or int(l.get('arg0',0)) not in cavern_tags:continue
        si=int(b['sidedef'][int(l['sidefront'])]['sector'])
        if tex(b['sector'][si],'textureceiling')=='IKTKPN4':caps.append(f'{si}|{li}|{l["arg0"]}')
    assert len(caps)==7, 'Review platform control-sector changes'
    outputs['tutnt/cavern/platforms.txt']='\n'.join(caps)+'\n'

    # Join adjoining lava sectors before measuring shoreline clearance. Internal
    # sector splits must not punch holes in the atmospheric layer.
    from build_local_heat import distance_edge
    lava={int(r.split('|')[0]) for r in rows if tex(b['sector'][int(r.split('|')[0])],'texturefloor')=='QLAVA'}
    edges={}
    for si in sorted(lava):
        for a,c,li,side in geo[si]:edges.setdefault(li,[]).append((a,c))
    shore=[v[0] for v in edges.values() if len(v)==1]
    haze=[]
    for y in range(-6740,-3200,224):
        for x in range(3810,7900,224):
            si=next((i for i in sorted(lava) if inside((x,y),geo[i])),None)
            if si is None:continue
            clearance=min(distance_edge((x,y),a,c) for a,c in shore)
            if clearance<56:continue
            floor=float(b['sector'][si]['heightfloor'])
            assert floor==-1500, 'Review lava atmosphere elevation'
            haze.append(f'{x}|{y}|{floor+2:g}|{min(320,clearance-8):.3f}|{si}')
    outputs['tutnt/cavern/haze.txt']='\n'.join(haze)+'\n'

    def add(name, verts, faces, origin, skin, kind, sector_override=None, uv_scale=1.0):
        assert f'tutnt/models/cavern/{name}.obj' not in outputs, ('Duplicate cavern mesh',name)
        # World-space input -> Y-up OBJ. 1.2 model Z compensates Doom's aspect.
        out=['# Cosmetic cavern mesh; no collision.','s off']
        out += ['v %.6f %.6f %.6f'%(x-origin[0],z-origin[2],-(y-origin[1])) for x,y,z in verts]
        # Per-triangle planar UVs keep rock grain a consistent world size.
        uv=[]; ns=[]
        for face in faces:
            a,c,d=[verts[i] for i in face];u=[c[k]-a[k] for k in range(3)];v=[d[k]-a[k] for k in range(3)]
            n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);ln=math.sqrt(sum(q*q for q in n)) or 1
            ns.append((n[0]/ln,n[2]/ln,-n[1]/ln));axis=max(range(3),key=lambda k:abs(n[k]))
            for x,y,z in (a,c,d):uv.append(((y if axis==0 else x)*uv_scale/128,(y if axis==2 else z)*uv_scale/128))
        out+=['vt %.6f %.6f'%p for p in uv]
        if kind in (2,3,4):
            # Shared vertex normals make the finer ridges read as continuous stone
            # and prevent the world projection from changing at every triangle.
            smooth=[[0.,0.,0.] for _ in verts]
            for face,n in zip(faces,ns):
                for index in face:
                    for axis in range(3):smooth[index][axis]+=n[axis]
            smooth=[tuple(q/max(1e-9,math.sqrt(sum(v*v for v in n))) for q in n) for n in smooth]
            out+=['vn %.6f %.6f %.6f'%n for n in smooth]
            out+=['f '+' '.join(f'{v+1}/{j*3+k+1}/{v+1}' for k,v in enumerate(f)) for j,f in enumerate(faces)]
        else:
            out+=['vn %.6f %.6f %.6f'%n for n in ns]
            out+=['f '+' '.join(f'{v+1}/{j*3+k+1}/{j+1}' for k,v in enumerate(f)) for j,f in enumerate(faces)]
        outputs[f'tutnt/models/cavern/{name}.obj']='\n'.join(out)+'\n'
        if skin=='IKWALL44' and kind!=5:skin='UCAVROCK'
        cls='UTNTCavern_'+name;radius=math.ceil(max(math.hypot(x-origin[0],y-origin[1]) for x,y,z in verts)+16)
        state=' States { Spawn: SKED A -1 Bright; Stop; }' if kind==1 else ''
        classes.append(f'class {cls} : UTNTCavernScenery {{ Default {{ RenderRadius {radius}; }}{state} }}')
        models.append(f'Model {cls}\n{{\n Path "models/cavern/"\n Model 0 "{name}.obj"\n Skin 0 "{skin}"\n Scale 1 1 1.2\n DontCullBackfaces\n FrameIndex SKED A 0 0\n}}')
        sector=sector_override if sector_override is not None else next((i for i,ee in geo.items() if inside(origin[:2],ee)),None)
        assert sector is not None, (name,origin)
        placements.append('|'.join(map(str,[cls,*origin,sector,kind])))

    def column(name,x,y,z,r,length,seed,sector):
        # Broad buried root, offset asymmetric shoulders, sharp hanging tip.
        verts=[];rings=[(12,1.18),(0,1),(-length*.25,.76),(-length*.58,.43),(-length*.86,.18),(-length,.018)]
        for j,(h,scale) in enumerate(rings):
            for k in range(9):
                a=2*math.pi*k/9;w=1+.16*math.sin(k*2.7+seed)+.09*math.sin(j*3.1+k)
                vx=x+math.cos(a)*r*scale*w+j*3;vy=y+math.sin(a)*r*scale*w-j*2
                vz=plane(sector,(vx,vy))+h if j<=1 else z+h
                verts.append((vx,vy,vz))
        faces=[]
        for j in range(len(rings)-1):
            for k in range(9):
                a=j*9+k;c=j*9+(k+1)%9;d=a+9;e=c+9;faces.extend([(a,d,c),(c,d,e)])
        add(name,verts,faces,(x,y,z),'IKWALL44',0)

    # Suspended above the peripheral lava, away from the jumping platforms.
    for args in [('stalactite_a',5280,-4400,632,120,380,1),('stalactite_b',5160,-3790,632,88,290,2),
                 ('stalactite_c',7060,-4590,632,110,430,3),('stalactite_d',4590,-6340,632,108,360,4)]:
        name,x,y,z,r,h,seed=args
        sec=next(i for i,ee in geo.items() if inside((x,y),ee))
        assert float(b['sector'][sec]['heightceiling'])==z and tex(b['sector'][sec],'texturefloor')=='QLAVA',(name,sec)
        column(name,x,y,plane(b['sector'][sec],(x,y)),r,h,seed,b['sector'][sec])

    # Lava emerges from the existing east cliff of the first chamber. Its
    # convex sheet and rocky cheeks sit outside the original collision wall.
    verts=[];faces=[]
    for j in range(18):
        t=j/17;z=-244-t*1258
        for k in range(9):
            u=k/8;y=-4040+(u-.5)*(150+24*math.sin(t*3.7))
            x=5476-16*math.sin(math.pi*u)-t*8+3*math.sin(t*11+k*1.7)
            verts.append((x,y,z))
    for j in range(17):
        for k in range(8):
            a=j*9+k;faces.extend([(a,a+9,a+1),(a+1,a+9,a+10)])
    add('lavafall',verts,faces,(5450,-4040,-860),'UCAVFALL',1)

    def rib(name,y,seed):
        verts=[];faces=[]
        for j in range(10):
            z=-210-j*146;cy=y+12*math.sin(j*.73+seed)
            for k in range(5):
                u=k/4;verts.append((5484-43*math.sin(math.pi*u)*(1+.15*math.sin(j*2+seed)),cy+(u-.5)*90,z))
        for j in range(9):
            for k in range(4):
                a=j*5+k;faces.extend([(a,a+5,a+1),(a+1,a+5,a+6)])
        add(name,verts,faces,(5460,y,-865),'IKWALL44',0)
    rib('fall_cheek_a',-4145,1);rib('fall_cheek_b',-3935,2)
    # A shallow protruding lip conceals the upper edge of the curtain.
    verts=[(5488,-4140,-252),(5438,-4120,-252),(5430,-4035,-253),(5440,-3960,-252),(5488,-3940,-252),
           (5488,-4140,-218),(5448,-4120,-232),(5442,-4035,-239),(5450,-3960,-230),(5488,-3940,-218)]
    faces=[(0,1,6),(0,6,5),(1,2,7),(1,7,6),(2,3,8),(2,8,7),(3,4,9),(3,9,8)]
    add('fall_lip',verts,faces,(5450,-4040,-240),'IKWALL44',0)

    def rock_patch(name, center, axis_u, axis_v, normal, width, length, depth, seed):
        # An irregular convex rock face. The outer ring is buried behind its
        # supporting plane, so models merge into the authored wall/ceiling.
        verts=[tuple(center[k]+normal[k]*depth for k in range(3))];faces=[]
        for ring in range(1,9):
            r=ring/8
            for j in range(25):
                angle=j*math.tau/25
                wobble=1+.09*math.sin(j*2.7+seed)+.06*math.cos(j*4.1-seed)
                u=math.cos(angle)*r*width*wobble;v=math.sin(angle)*r*length*wobble
                bump=depth*max(0,1-r*r)**.7*(1+.19*math.sin(j*1.3+seed)+.12*math.sin(j*2.3+seed+ring*.7))
                if ring==8:bump=-28
                verts.append(tuple(center[k]+axis_u[k]*u+axis_v[k]*v+normal[k]*bump for k in range(3)))
        for j in range(25):faces.append((0,1+j,1+(j+1)%25))
        for ring in range(7):
            for j in range(25):
                a=1+ring*25+j;c=1+ring*25+(j+1)%25;d=a+25;e=c+25
                faces.extend([(a,d,c),(c,d,e)])
        # Consistent outward normals matter even with backface culling disabled.
        for j,f in enumerate(faces):
            a,c,d=[verts[n] for n in f];u=[c[k]-a[k] for k in range(3)];v=[d[k]-a[k] for k in range(3)]
            n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            if sum(n[k]*normal[k] for k in range(3))<0:faces[j]=(f[0],f[2],f[1])
        origin=tuple(center[k]+normal[k]*16 for k in range(3))
        add(name,verts,faces,origin,'IKWALL44',2)

    # Break up tall cliff faces below their walkable tops. No model raises the
    # surface of a ledge, spans a doorway or supplies a fake stepping stone.
    wall_count=0
    for si in sorted(lava):
        for a,c,li,side in geo[si]:
            l=b['linedef'][li]
            oi=int(l.get('sideback' if int(l['sidefront'])==side else 'sidefront',-1))
            if oi<0:continue
            other=b['sector'][int(b['sidedef'][oi]['sector'])];top=float(other.get('heightfloor',0))
            span=math.dist(a,c)
            if span<170 or not -800<=top<=0 or tex(b['sidedef'][side],'texturebottom')!='IKWALL44':continue
            if li==4876:continue # reserved for the framed lava fall
            top=min(plane(other,p,'floor') for p in (a,c,((a[0]+c[0])/2,(a[1]+c[1])/2)))
            tangent=((c[0]-a[0])/span,(c[1]-a[1])/span,0);normal=(tangent[1],-tangent[0],0)
            center=((a[0]+c[0])/2,(a[1]+c[1])/2,(-1500+top)/2-60)
            rock_patch(f'wall_{li}',center,tangent,(0,0,1),normal,min(220,span*.43),(top+1500)*.31,72+(li%4)*12,li)
            if span>=240:
                for q in (-1,1):
                    offset=span*.23*q
                    ribcenter=(center[0]+tangent[0]*offset,center[1]+tangent[1]*offset,center[2]-90)
                    rock_patch(f'wall_rib_{li}_{q+1}',ribcenter,tangent,(0,0,1),normal,min(86,span*.16),(top+1500)*.24,100+(li%3)*16,li+q*17)
            wall_count+=1

    from cavern_rock_details import generate_details
    details,detail_checks=generate_details(b,geo,lava,add)
    outputs['tutnt/cavern/detail-clearance.txt']='\n'.join('|'.join(map(str,row)) for row in detail_checks)+'\n'

    from cavern_skyrooms import generate as generate_skyrooms
    skyrooms=generate_skyrooms(b,geo,add,map_path.read_bytes())
    outputs['tutnt/cavern/skyrooms.json']=json.dumps(skyrooms,indent=2)+'\n'
    outputs['tutnt/cavern/portal-atmosphere.txt']='\n'.join('|'.join(map(str,[w['line'],w['sector'],w['pocket'],65200+j,w['portal_line']])) for j,w in enumerate(skyrooms['windows']))+'\n'
    # The lava material deliberately ignores flat UV scaling. Generate a local
    # variant from the shared source, scaling its physical pattern but not fog.
    lava=(root/'tutnt/shaders/lava-surface.fp').read_text()
    for before,after in (
        ('vec2 world=LavaWorldPosition();','vec2 world=LavaWorldPosition()*8.0;'),
        ('vec2 current=world+LavaFloorPanning();','vec2 current=world+LavaFloorPanning()*8.0;'),
        ('length(world-uCameraPos.xz)','length(LavaWorldPosition()-uCameraPos.xz)')):
        assert lava.count(before)==1, ('Sky lava source changed',before)
        lava=lava.replace(before,after)
    outputs['tutnt/shaders/cavern-lava.fp']='// Generated by tools/build_cavern.py from lava-surface.fp: 1:8 skybox scale.\n'+lava

    outputs['tutnt/cavern/skyviews.txt']='\n'.join('|'.join(map(str,[65200+j,*w['center'],*w['view_origin']])) for j,w in enumerate(skyrooms['windows']))+'\n'

    fall_sources=[]
    for j,(x,y) in enumerate([(4840,-4030),(5170,-4460),(6840,-3920),(6960,-4500),
                              (4780,-5980),(5050,-6420),(6600,-5910),(6400,-6250)]):
        si=next(i for i,ee in geo.items() if inside((x,y),ee));s=b['sector'][si]
        assert tex(s,'texturefloor')=='QLAVA' and float(s['heightceiling'])==632,('roof',j,si)
        depth=128+(j%3)*20
        ceiling=plane(s,(x,y));dx=plane(s,(x+1,y))-ceiling;dy=plane(s,(x,y+1))-ceiling
        rock_patch(f'roof_{j}',(x,y,ceiling+6),(1,0,dx),(0,1,dy),(0,0,-1),230+(j%3)*35,170+(j%2)*55,depth,j+3)
        fall_sources.append(f'{x}|{y}|{ceiling+6-depth-14:.3f}|{si}')
    outputs['tutnt/cavern/fall-sources.txt']='\n'.join(fall_sources)+'\n'
    outputs['tutnt/cavern/scenery.txt']='\n'.join(placements)+'\n'
    outputs['tutnt/zscript/cavern-generated.zc']='// Generated by tools/build_cavern.py\n'+'\n'.join(classes)+'\n'
    outputs['tutnt/modeldef/MODELDEF.cavern']='\n\n'.join(models)+'\n'
    for rel,data in outputs.items():
        path=root/rel
        if check:
            if not path.exists() or path.read_text()!=data: raise RuntimeError('Stale cavern output: '+rel)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data,encoding='utf-8')
    print(json.dumps({'sectors':len(rows),'models':len(placements),'wall_models':wall_count,'details':details,'haze':len(haze),'check':check}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();generate(check=a.check)
