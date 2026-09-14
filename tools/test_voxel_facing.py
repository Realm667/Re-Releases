"""Validate angle-only WAD edits and inspect native voxel facing in every changed map.

Generated fixture/addon and reports stay in tutnt/.codex. Map geometry, ACS,
flags, IDs, positions, other thing fields and all non-map lumps must match base.
"""
from pathlib import Path
import argparse, json, struct, subprocess, sys, zipfile
from build_utnt import read_wad
from orient_voxel_items import BLOCK, FIELD, ANGLE, TYPES, process, FRONT_OFFSET
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent


def compare(before, after):
    # Use the WAD directory directly so the baseline can remain in memory.
    def lumps(raw):
        _,n,o=struct.unpack_from('<4sII',raw)
        return [(name.rstrip(b'\0'),raw[pos:pos+size]) for pos,size,name in (struct.unpack_from('<II8s',raw,o+i*16) for i in range(n))]
    old=lumps(before);new=lumps(after)
    assert [n for n,d in old]==[n for n,d in new], 'Lump order changed'
    udmf=any(n==b'TEXTMAP' for n,d in old)
    changed=0
    for (name,a),(_,b) in zip(old,new):
        if a==b:continue
        if udmf:
            assert name==b'TEXTMAP', f'Non-TEXTMAP lump changed: {name}'
            aa=a.decode();bb=b.decode()
            at=list(BLOCK.finditer(aa));bt=list(BLOCK.finditer(bb))
            assert len(at)==len(bt), 'Thing count changed'
            def remove_angles(text):
                return BLOCK.sub(lambda m:'thing{'+ANGLE.sub('',m[1]).strip()+'}',text)
            assert remove_angles(aa)==remove_angles(bb), 'Non-angle TEXTMAP data changed'
            for x,y in zip(at,bt):
                if x[1]==y[1]:continue
                xf=dict(FIELD.findall(x[1]));yf=dict(FIELD.findall(y[1]))
                assert int(xf['type']) in TYPES
                assert xf.pop('angle','0')!=yf.pop('angle','0')
                assert xf==yf
                changed+=1
        else:
            assert name==b'THINGS', f'Non-THINGS binary lump changed: {name}'
            stride=20 if any(n==b'BEHAVIOR' for n,d in old) else 10
            angleoff=8 if stride==20 else 4;typeoff=10 if stride==20 else 6
            assert len(a)==len(b)
            for i in range(0,len(a),stride):
                x=a[i:i+stride];y=b[i:i+stride]
                if x==y:continue
                assert x[:angleoff]==y[:angleoff] and x[angleoff+2:]==y[angleoff+2:]
                assert struct.unpack_from('<H',x,typeoff)[0] in TYPES
                changed+=1
    return changed


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',default='HEAD')
    p.add_argument('--engine',type=Path,default=Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe'))
    p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--maps',nargs='*')
    p.add_argument('--static-only',action='store_true')
    p.add_argument('--report',default='voxel-facing.json')
    args=p.parse_args()
    work=ROOT/'tutnt/.codex/work/voxel-facing';work.mkdir(parents=True,exist_ok=True)
    actors={a['actor']:a for a in json.loads((ROOT/'tools/artwork/voxels/manifest.json').read_text())['actors']}
    report=[]
    for path in sorted((ROOT/'tutnt/maps').glob('*.wad')):
        _,items,kind=process(path,actors)
        report.append(dict(map=path.stem,placements=len(items),items=items))
    static=[];samples={};checks={};addon=ROOT/'tutnt/.codex/builds/voxel-facing-review.pk3'
    for entry in report:
        path=ROOT/'tutnt/maps'/(entry['map']+'.wad')
        before=subprocess.check_output(['git','show',args.base+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
        count=compare(before,path.read_bytes())
        static.append(dict(map=entry['map'],angle_changes=count))
        if args.maps and entry['map'] not in args.maps:continue
        if not entry['placements']:continue
        marker=read_wad(path)[1][0][0].rstrip(b'\0').decode()
        checks[marker]=entry['items']
        # TNT01's four wall-facing shell rows are the original reported area.
        if entry['map']=='tnt01':
            samples[marker]=[next(i for i in entry['items'] if i['thing']==t) for t in (4,5,6,7)]
        else:
            changed=[i for i in entry['items'] if i.get('walls')]
            picked=[];seen=set()
            for i in changed:
                if i['actor'] not in seen: picked.append(i);seen.add(i['actor'])
                if len(picked)==3:break
            samples[marker]=picked
    output=dict(static=static,total_changes=sum(r['angle_changes'] for r in static),runtime=[])
    if Path(args.report).name!=args.report:p.error('--report must be a filename')
    resultpath=ROOT/'tutnt/.codex/validation'/args.report
    resultpath.write_text(json.dumps(output,indent=2))
    if args.static_only:print(json.dumps(output));return
    code='version "5.0.0"\nclass UTNTVoxelFacingTest : EventHandler { Actor Cam; int Found, Missing;\n'
    code+="""Actor Locate(class<Actor> type, double x, double y) {
        let it=ThinkerIterator.Create(type); Actor a=null;
        while(a=Actor(it.Next())) if(abs(a.Pos.X-x)<0.1 && abs(a.Pos.Y-y)<0.1) return a;
        return null;
    }
    void Check(class<Actor> type,double x,double y,int angle) {
        let a=Locate(type,x,y);if(!a){Missing++;return;}Found++;
        Console.Printf("UTNT_ASSERT %s %s at %.0f %.0f angle %.0f expected %d",
            (abs(a.Angle-angle)<0.1 || abs(abs(a.Angle-angle)-360)<0.1) ? "PASS":"FAIL",a.GetClassName(),x,y,a.Angle,angle);
    }
    void View(class<Actor> type,double x,double y,int angle) {
        let a=Locate(type,x,y);if(!a)return;
        if(!Cam)Cam=Actor.Spawn('MapSpot',a.Pos);
        Cam.SetOrigin(a.Pos+(cos(angle)*128,sin(angle)*128,52),false);
        Cam.Angle=angle+180;Cam.Pitch=15;players[0].camera=Cam;
    }
    override void WorldTick(){if(Cam)players[0].camera=Cam;}
    override void NetworkProcess(ConsoleEvent e) {
      if(e.Name=="vfcheck") { Found=Missing=0;
    """
    for marker,items in checks.items():
        code+=f'if(level.MapName=="{marker}") {{\n'
        for i in items: code+=f"Check('{i['actor']}',{i['x']},{i['y']},{i['after']});\n"
        code+='}\n'
    code+='Console.Printf("UTNT_ASSERT %s placement coverage %d active, %d unspawned",Found>0?"PASS":"FAIL",Found,Missing); }\n'
    code+='if(e.Name=="vfview") {\n'
    for marker,items in samples.items():
        code+=f'if(level.MapName=="{marker}") {{\n'
        for n,i in enumerate(items):code+=f"if(e.Args[0]=={n})View('{i['actor']}',{i['x']},{i['y']},{(i['after']+FRONT_OFFSET.get(i['actor'],0))%360});\n"
        code+='}\n'
    code+='} } }\n'
    (work/'ZSCRIPT').write_text(code)
    with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('ZSCRIPT',code);z.writestr('MAPINFO','gameinfo { AddEventHandlers="UTNTVoxelFacingTest" }')
        for f in (ROOT/'tutnt/maps').glob('*.wad'):z.write(f,'maps/'+f.name)
    compiled=run_case(args.engine,args.iwad,root=ROOT/'tutnt/.codex',mod=ROOT/'tutnt.pk3',addon=addon,label='voxel-facing-compile',timeout=45)
    if not compiled['ok']: print(Path(compiled['log']).read_text()[-6500:]);raise SystemExit(1)
    for marker in checks:
        label='voxel-facing-'+marker.lower()
        commands=['vid_setsize 1280 720','god','notarget','crosshair 0','wait 60']
        if marker=='TNT04A':commands+=['+use','wait 5','-use','wait 35']
        commands+=['netevent vfcheck','wait 3']
        for n in range(len(samples[marker])):
            commands += [f'netevent vfview {n}','wait 8',f'screenshot logs/{label}-{n}.png']
        if marker=='TNT01':commands+=['save voxel-facing','wait 8','load voxel-facing','wait 70','netevent vfcheck','wait 3']
        commands+=['echo UTNT_TEST_END','quit']
        result=run_case(args.engine,args.iwad,root=ROOT/'tutnt/.codex',mod=ROOT/'tutnt.pk3',addon=addon,mapname=marker,label=label,timeout=75,
            settings=[('developer',1),('vid_activeinbackground',True),('vid_lowerinbackground',False),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites',False),('i_pauseinbackground',False),('vid_maxfps',60)],commands='; '.join(commands))
        output['runtime'].append(result);resultpath.write_text(json.dumps(output,indent=2))
        if not result['ok']:print(Path(result['log']).read_text()[-6500:]);raise SystemExit(1)

if __name__=='__main__':main()
