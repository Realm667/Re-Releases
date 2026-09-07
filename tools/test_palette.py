"""Check that Doom assets follow PLAYPAL while an independent PNG retains its colors.
Set UTNT_ENGINE / UTNT_IWAD. Requires Pillow for read-only screenshot comparisons.
Writes isolated test palettes and engine output below logs/palette-restore.
"""
import argparse,json,os,pathlib,shutil
from PIL import Image
from check_engine import ROOT,run_case


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mod',type=pathlib.Path,default=ROOT/'tutnt.pk3')
    parser.add_argument('--label',default='palette')
    args=parser.parse_args()
    output=ROOT/'logs/palette-restore';output.mkdir(exist_ok=True)
    palette=(ROOT/'tutnt/PLAYPAL.pal').read_bytes()
    variants={'project':palette,'swapped':bytes(255-v for v in palette)}
    results=[];comparisons=[]
    for renderer in ['0','1']:
        for name,data in variants.items():
            addon=output/name;addon.mkdir(exist_ok=True)
            for filename in ['MAPINFO','ZSCRIPT']:shutil.copy2(ROOT/'tools/palette-tests'/filename,addon/filename)
            (addon/'PLAYPAL.lmp').write_bytes(data)
            label=f'{args.label}-{name}-{renderer}'
            r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=args.mod,
                mapname='TNT01',addon=addon,renderer=renderer,label=label,regression=True,
                settings=[('con_notifytime',0)],commands=f'wait 180; screenshot logs/{label}.png; echo UTNT_TEST_END; wait 5; quit\n')
            results.append(r)
        before=Image.open(ROOT/'logs'/f'{args.label}-project-{renderer}.png').convert('RGB')
        after=Image.open(ROOT/'logs'/f'{args.label}-swapped-{renderer}.png').convert('RGB')
        assert before.size==after.size==(960,540)
        for i in range(13):
            x=8+(i%4)*236;y=8+(i//4)*128+20
            box=(x,y,x+224,y+94)
            a=before.crop(box).tobytes();b=after.crop(box).tobytes()
            changed=sum(a[j:j+3]!=b[j:j+3] for j in range(0,len(a),3))
            ok=changed==0 if i==12 else changed>100
            comparisons.append({'renderer':renderer,'tile':i,'changed_pixels':changed,'ok':ok,'independent_png':i==12})
    report={'runtime':results,'comparisons':comparisons}
    (output/f'{args.label}-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if all(x['ok'] for x in results+comparisons) else 1)

if __name__=='__main__':main()
