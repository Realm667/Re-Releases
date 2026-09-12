"""Native rollout coverage and neutral/periodic data checks. Fixtures stay in .codex."""
from pathlib import Path
import argparse,collections,hashlib,json,re,shutil,sys
import numpy as np
from PIL import Image
from build_organic_materials import ROOT,STRUCTURE_PRESETS,relief,height_depth,validate_compatibility
from check_engine import run_case
import test_metal_materials as room
C=ROOT/'tutnt/.codex'


def data_checks():
    config=json.loads((ROOT/'tools/organic-materials/materials.json').read_text())
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    validate_compatibility(config)
    tested=[]
    for profile in STRUCTURE_PRESETS:
        for value in [0,24,100,255]:
            h,n=relief(np.full((32,32,3),value,np.uint8),profile,3,(32,32))
            assert np.all(h==127),(profile,value,'flat surface moved')
            assert np.all(n[:,:,:2]==127) and np.all(n[:,:,2]==255)
        rgb=np.random.default_rng(667).integers(0,120,(40,48,3),dtype=np.uint8)
        h,n=relief(rgb,profile,3,(48,40));hh,nn=relief(np.tile(rgb,(2,3,1)),profile,3,(144,80))
        assert np.array_equal(hh,np.tile(h,(2,3))) and np.array_equal(nn,np.tile(n,(2,3,1))),profile
        # A remote decoration cannot change the shared interior's height.
        altered=rgb.copy();altered[:5]=255
        bh,bn=relief(altered,profile,3,(48,40))
        assert np.array_equal(h[17:25],bh[17:25]),profile
        tested.append(profile)
    # A top-lit convex body has a bright upper slope and a dark lower slope.
    yy=np.arange(40,dtype=np.float32)
    shape=np.exp(-((yy-20)/5)**2)
    lighting=np.clip(.35+.9*np.gradient(shape),0,1)
    image=np.uint8(np.tile(lighting[:,None,None],(1,32,3))*255)
    field,_=relief(image,'technical',3,(32,40),dict(kind='surface-structure',model='toplit'))
    assert field[18,16]>127 and field[22,16]>127,'Lit and shaded slopes must form one raised body'
    assert 17<=int(field[:,16].argmax())<=23,'Top-lit reconstructed peak is misplaced'
    # Printed variants share exactly the same physical crate body.
    def height(name):
        v=manifest['variants'][name]
        return np.asarray(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png')))
    assert np.array_equal(height('QCRATE1'),height('QCRATE2'))
    # Shared top rails stay on the wall plane across their painted shadows.
    caps=[height(name)[8:24,16:120] for name in ['QTECH20','QTECH21','QTECH25','QTECH26','QTECH33']]
    assert all(np.array_equal(caps[0],cap) for cap in caps[1:])
    assert np.all(caps[0]==127)
    from test_material_geometry import check as geometry_check
    geometry_check()
    decisions=json.loads((ROOT/'tools/organic-materials/rollout.json').read_text())['decisions']
    assert all(d['status'] in ('accepted','rejected') for d in decisions)
    assert {d['name'] for d in decisions if d['status']=='accepted'}=={m['name'] for m in config['materials'] if m.get('rollout_category')}
    details=[]
    for m in config['materials']:
        if not m.get('rollout_category'):continue
        for name in next(r for r in manifest['materials'] if r['name']==m['name'])['variants']:
            v=manifest['variants'][name];h=np.asarray(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png')))
            n=np.asarray(Image.open(ROOT/'tutnt'/(v['stem']+'-normal.png')))
            assert h.shape==n.shape[:2] and np.all(n[:,:,2]>127)
            d=height_depth(h)*v['depth'];span=float(d.max()-d.min())
            assert span>0, 'Ineffective relief binding: '+name
            assert span<=m['depth']+.001 and m['depth']<=(12 if m['profile']=='authored' else 8)
            assert float(d.min())>=-6.001 and float(d.max())<=6.001
            assert abs(v['trace_top']*v['depth'])<=6 and abs(v['trace_bottom']*v['depth'])<=6
            assert v['neutral']==127 and np.count_nonzero(h==127)>0
            details.append(dict(name=name,base=m['name'],span=span,neutral_fraction=float((h==127).mean())))
    assert manifest['variants']['XA09TEX']['edge_mode']=='tile'
    assert manifest['variants']['XB09TEX']['edge_mode']=='band'
    text=(ROOT/'tutnt/gldefs/GLDEFS.organic').read_text()
    assert 'Define ORGANIC_TILE_EDGE' in text and 'Define ORGANIC_BAND_EDGE' in text
    return dict(ok=True,profiles=tested,variants=len(details),materials=len({e['base'] for e in details}),data=details)


def cases(provisional=False):
    config=json.loads((ROOT/'tools/organic-materials/materials.json').read_text())
    groups=collections.defaultdict(list)
    for m in config['materials']:
        if m.get('rollout_category'):groups['main-'+m['profile']].append(m['name'])
    if provisional:
        for n,m in json.loads((C/'work/material-rollout/provisional/manifest.json').read_text()).items():groups['trial-'+m['profile']].append(n)
    result=[]
    for group,names in groups.items():
        names=sorted(names)
        for i in range(0,len(names),4):
            walls=names[i:i+4];walls+=walls[-1:]*(4-len(walls))
            floor=next((n for n in walls if any(k in n for k in ['FLOOR','FLAT','CITYF','WOODF','TECHF'])),walls[0])
            result.append((group+'-'+str(i//4),walls,floor))
    if not provisional:
        result=json.loads((ROOT/'tools/organic-materials/rollout.json').read_text())['fixture_cases']
        covered={n for _,walls,floor in result for n in walls+[floor]}
        assert {m['name'] for m in config['materials'] if m.get('rollout_category')}<=covered
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    aliases=[n for n,base in manifest['environment_bindings'].items() if base in ('XA09TEX','XB09TEX')]
    assert len(aliases)>=2
    result.append(('expanded-edge',['XA09TEX','XB09TEX',aliases[0],aliases[-1]],'XA09TEX'))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',type=Path);p.add_argument('--renderer',default='1',choices=['0','1'])
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--baseline',action='store_true');p.add_argument('--provisional',action='store_true');p.add_argument('--live',action='store_true');p.add_argument('--data-only',action='store_true')
    p.add_argument('--cases',nargs='*');p.add_argument('--poses',type=int,nargs='*',default=[0,1,2])
    a=p.parse_args();dest=C/'validation/material-rollout';dest.mkdir(exist_ok=True)
    report=data_checks();(dest/'data.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='data'}),flush=True)
    if a.data_only:return
    if not a.engine:p.error('--engine is required')
    room.CASES=cases(a.provisional);manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    mode='baseline' if a.baseline else 'relief';path=C/'work/material-rollout'/('fixture-'+mode+('-trial' if a.provisional else '')+('-live' if a.live else '-package'))
    room.fixture(path,False,manifest)
    if a.live:
        for f in list(manifest['outputs'])+['tutnt/shaders/organic/relief.glsl','tutnt/shaders/environment/surface.glsl']:
            rel=Path(f).relative_to('tutnt');rel=Path('GLDEFS') if rel.as_posix()=='gldefs/GLDEFS.organic' else rel
            target=path/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f,target)
    if a.provisional:
        trial=C/'work/material-rollout/provisional'
        for f in (trial/'materials').rglob('*.png'):
            target=path/f.relative_to(trial);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
        with (path/'GLDEFS').open('a') as f:f.write('\n'+(trial/'GLDEFS').read_text())
    if a.baseline:
        (path/'flat.fp').write_text('void SetupMaterial(inout Material mat){mat.Base=getTexel(vTexCoord.st);mat.Normal=normalize(vWorldNormal.xyz);mat.Specular=vec3(0);mat.SpecularLevel=0;}\n')
        names={n for _,w,f in room.CASES for n in w+[f]}
        edge_names={'XA09TEX','XB09TEX'}|{n for n,base in manifest['environment_bindings'].items() if base in ('XA09TEX','XB09TEX')}
        names-=edge_names
        with (path/'GLDEFS').open('a') as f:f.write('\n'+'\n'.join(f'Material "{n}" {{ Shader "flat.fp" Normal "materials/environment/normal.png" Specular "materials/organic/black.png" }}' for n in sorted(names)))
    chosen=[i for i,c in enumerate(room.CASES) if (not a.cases or c[0] in a.cases) and not (a.baseline and c[0]=='expanded-edge')];assert chosen
    logs=C/'logs/material-rollout';logs.mkdir(exist_ok=True);results=[]
    for batch in range(0,len(chosen),6):
        selected=chosen[batch:batch+6];label=f'rollout-{mode}-r{a.renderer}-{selected[0]}'
        cfg='wait 90;screenblocks 12;';expected={}
        for i in selected:
            for pose in a.poses:
                view=i*3+pose;name=room.CASES[i][0]
                cfg+=f'netevent metalview {view};wait 8;netevent metalview {view};wait 24;screenshot "logs/material-rollout/{mode}-r{a.renderer}-{name}-{pose}.png";wait 2;'
                expected.update({(view,s):n for s,n in enumerate(room.CASES[i][1],1)});expected[(view,0)]=room.CASES[i][2]
        cfg+='save rollout-check;wait 3;load rollout-check;wait 6;echo UTNT_TEST_END;wait 3;quit\n';assert len(cfg.encode())<4000
        settings=[('cl_capfps',True),('vid_scalemode',5),('vid_scale_customwidth',960),('vid_scale_customheight',540),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),('use_mouse',False),('use_joystick',False),('r_drawplayersprites',False),('crosshair',0),('con_notifytime',0),('gl_texture_filter',0),('screenblocks',12)]
        r=run_case(a.engine,a.iwad,root=C,mod=a.mod,addon=path,mapname='METTEST',renderer=a.renderer,label=label,timeout=55,commands=cfg,settings=settings,quiet=True)
        output=Path(r['log']).read_text(encoding='utf-8');found={(int(v),int(s)):n for v,s,n in re.findall(r'METAL_SURFACE\|(\d+)\|(\d+)\|(\S+)',output)}
        if found!=expected:r['ok']=False;r['errors'].append('Material assignment mismatch')
        if 'ERROR:' in output or 'Failed to compile' in output:r['ok']=False;r['errors'].append('Shader compile error')
        r.update(surfaces=len(found),cases=[room.CASES[i][0] for i in selected],live=a.live,provisional=a.provisional);results.append(r);(dest/(label+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
        if not r['ok']:print(output[-4000:]);break
    tag=('subset-'+hashlib.sha256('|'.join(a.cases).encode()).hexdigest()[:10]) if a.cases else 'all';(dest/f'native-{mode}-r{a.renderer}-{tag}.json').write_text(json.dumps(results,indent=2))
    (dest/'cases.json').write_text(json.dumps(room.CASES,indent=2))
    raise SystemExit(0 if all(r['ok'] for r in results) else 1)

if __name__=='__main__':main()
