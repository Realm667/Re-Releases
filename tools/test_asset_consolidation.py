"""Pixel/size regression for all textures affected by asset consolidation.

Pass immutable --before and --after PK3s. Writes only under tutnt/.codex.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
from check_engine import ROOT, run_case


def run(before, after, engine, iwad):
    names=json.loads((ROOT/'tools/fixtures/asset-consolidation/textures.json').read_text())
    addon=ROOT/'tutnt/.codex/work/size-audit/texture-gallery'
    addon.mkdir(parents=True,exist_ok=True)
    (addon/'MAPINFO').write_text('GameInfo { AddEventHandlers = "UTNTAssetGallery" }\n')
    script='''version "5.0.0"
class UTNTAssetGallery : StaticEventHandler
{
 ui bool Reported;
 ui void Tile(String name, int i)
 {
  let tex=TexMan.CheckForTexture(name,TexMan.Type_Any);
  if(!Reported) Console.Printf("UTNT_ASSERT %s: asset %s",tex.isValid()?"PASS":"FAIL",name);
  if(!tex.isValid()) return;
  let [w,h]=TexMan.GetSize(tex);
  if(!Reported) Console.Printf("UTNT_ASSET_SIZE %s %d %d",name,w,h);
  Screen.DrawTexture(tex,true,4+(i%40)*38,4+(i/40)*38,DTA_DestWidth,34,DTA_DestHeight,34,DTA_LeftOffset,0,DTA_TopOffset,0);
 }
 override void RenderOverlay(RenderEvent e)
 {
  Screen.Dim(0x000000,1,0,0,Screen.GetWidth(),Screen.GetHeight());
'''
    script+=''.join('  Tile('+json.dumps(n)+','+str(i)+');\n' for i,n in enumerate(names))
    script+='  if(!Reported) Console.Printf("UTNT_REGRESSION_COMPLETE");\n  Reported=true;\n }\n}\n'
    (addon/'ZSCRIPT').write_text(script)
    if len(names)>40*20: raise ValueError('Expand gallery before adding more than 800 textures')
    results=[]; sizes=[]
    for stage,package in [('before',before),('after',after)]:
        label='size-audit-gallery-'+stage
        result=run_case(engine,iwad,root=ROOT/'tutnt/.codex',mod=package,
            addon=addon,mapname='INTERMAP',label=label,timeout=70,regression=True,
            settings=[('con_notifytime',0),('screenblocks',12),('vid_maxfps',60),('gl_texture_filter',0)],
            commands=f'vid_setsize 1600 800; wait 180; screenshot logs/{label}.png; echo UTNT_TEST_END; wait 5; quit\n')
        results.append(result)
        if not result['ok'] or result['assertions']!=len(names): raise RuntimeError(result)
        sizes.append([line for line in Path(result['log']).read_text().splitlines() if line.startswith('UTNT_ASSET_SIZE ')])
    images=[Image.open(ROOT/f'tutnt/.codex/logs/size-audit-gallery-{stage}.png').convert('RGB') for stage in ('before','after')]
    if any(im.size!=(1600,800) for im in images): raise RuntimeError('Unexpected gallery dimensions')
    a,b=[im.tobytes() for im in images]
    changed=sum(a[i:i+3]!=b[i:i+3] for i in range(0,len(a),3))
    report={'runtime':results,'compared_resources':len(names),'image_size':[1600,800],
            'changed_pixels':changed,'same_texture_sizes':sizes[0]==sizes[1] and len(sizes[0])==len(names)}
    (ROOT/'tutnt/.codex/validation/size-audit-gallery.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if changed or not report['same_texture_sizes']: raise RuntimeError('Texture appearance or size changed')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',type=Path,required=True)
    parser.add_argument('--after',type=Path,required=True)
    parser.add_argument('--engine',type=Path,required=True)
    parser.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    args=parser.parse_args();run(**vars(args))
