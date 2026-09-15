"""Build TNT03A2's cosmetic cavern layer; never rewrite the source WAD.

Hand-authored placements are checked against the map. Generated sector bindings
include boundary coordinates so unrelated/reindexed maps cannot inherit the look.
"""
from pathlib import Path
import argparse, json, math
from build_lava_lips import parse, tex
from build_environment_fx import geometry, bounds, inside

ROOT = Path(__file__).resolve().parents[1]

def generate(root=ROOT, check=False):
    b=parse(root/'tutnt/maps/tnt03a2.wad'); geo=geometry(b)
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

    def add(name, verts, faces, origin, skin, kind):
        # World-space input -> Y-up OBJ. 1.2 model Z compensates Doom's aspect.
        out=['# Cosmetic cavern mesh; no collision.','s off']
        out += ['v %.6f %.6f %.6f'%(x-origin[0],z-origin[2],-(y-origin[1])) for x,y,z in verts]
        # Per-triangle planar UVs keep rock grain a consistent world size.
        uv=[]; ns=[]
        for face in faces:
            a,c,d=[verts[i] for i in face];u=[c[k]-a[k] for k in range(3)];v=[d[k]-a[k] for k in range(3)]
            n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);ln=math.sqrt(sum(q*q for q in n)) or 1
            ns.append((n[0]/ln,n[2]/ln,-n[1]/ln));axis=max(range(3),key=lambda k:abs(n[k]))
            for x,y,z in (a,c,d):uv.append(((y if axis==0 else x)/128,(y if axis==2 else z)/128))
        out+=['vt %.6f %.6f'%p for p in uv];out+=['vn %.6f %.6f %.6f'%n for n in ns]
        out+=['f '+' '.join(f'{v+1}/{j*3+k+1}/{j+1}' for k,v in enumerate(f)) for j,f in enumerate(faces)]
        outputs[f'tutnt/models/cavern/{name}.obj']='\n'.join(out)+'\n'
        cls='UTNTCavern_'+name;radius=math.ceil(max(math.hypot(x-origin[0],y-origin[1]) for x,y,z in verts)+16)
        state=' States { Spawn: SKED A -1 Bright; Stop; }' if kind==1 else ''
        classes.append(f'class {cls} : UTNTCavernScenery {{ Default {{ RenderRadius {radius}; }}{state} }}')
        models.append(f'Model {cls}\n{{\n Path "models/cavern/"\n Model 0 "{name}.obj"\n Skin 0 "{skin}"\n Scale 1 1 1.2\n DontCullBackfaces\n FrameIndex SKED A 0 0\n}}')
        sector=next((i for i,ee in geo.items() if inside(origin[:2],ee)),None)
        assert sector is not None, (name,origin)
        placements.append('|'.join(map(str,[cls,*origin,sector,kind])))

    def column(name,x,y,z,r,length,seed):
        # Broad buried root, offset asymmetric shoulders, sharp hanging tip.
        verts=[];rings=[(12,1.18),(0,1),(-length*.25,.76),(-length*.58,.43),(-length*.86,.18),(-length,.018)]
        for j,(h,scale) in enumerate(rings):
            for k in range(9):
                a=2*math.pi*k/9;w=1+.16*math.sin(k*2.7+seed)+.09*math.sin(j*3.1+k)
                verts.append((x+math.cos(a)*r*scale*w+j*3,y+math.sin(a)*r*scale*w-j*2,z+h))
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
        column(*args)

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
    outputs['tutnt/cavern/scenery.txt']='\n'.join(placements)+'\n'
    outputs['tutnt/zscript/cavern-generated.zc']='// Generated by tools/build_cavern.py\n'+'\n'.join(classes)+'\n'
    outputs['tutnt/modeldef/MODELDEF.cavern']='\n\n'.join(models)+'\n'
    for rel,data in outputs.items():
        path=root/rel
        if check:
            if not path.exists() or path.read_text()!=data: raise RuntimeError('Stale cavern output: '+rel)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data,encoding='utf-8')
    print(json.dumps({'sectors':len(rows),'models':len(placements),'haze':len(haze),'check':check}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();generate(check=a.check)
