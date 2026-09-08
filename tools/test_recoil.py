"""Exercise every UTNT weapon, measuring pitch peaks, per-tic motion and recovery."""
from pathlib import Path
import json, sys, struct, argparse, os

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO/'tools'))
from check_engine import run_case

WEAPONS = ['UTNTPistol','UTNTShotgun','UTNTSuperShotgun','UTNTChaingun',
           'UTNTMinigun','UTNTRocketLauncher','UTNTPlasmaRifle','UTNTBFG9000',
           'UTNTPyroCannon','UTNTFist','UTNTChainsaw','UTNTFlamer']
LIMITS = [0.15,0.5,0.75,0.175,0.175,1.2,0.175,1.75,1.875,0,0,0]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mod',type=Path,default=REPO/'tutnt.pk3')
    parser.add_argument('--output',type=Path,default=REPO/'logs/recoil-tests')
    parser.add_argument('--engine',default=os.environ.get('UTNT_ENGINE',str(REPO/'engine/uzdoom.exe')))
    parser.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'))
    a=parser.parse_args(); out=a.output.resolve(); addon=out/'fixture'
    if not a.iwad: parser.error('set UTNT_IWAD or pass --iwad')
    (addon/'maps').mkdir(parents=True,exist_ok=True)
    source='namespace="ZDoom";\n'
    for x,y in [(-4096,-4096),(-4096,4096),(4096,4096),(4096,-4096)]:
        source+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
    for i in range(4):
        source+=f'sidedef {{ sector=0; texturemiddle="STARTAN3"; }}\nlinedef {{ v1={i}; v2={(i+1)%4}; sidefront={i}; blocking=true; }}\n'
    source+='sector { heightfloor=0; heightceiling=512; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=192; }\n'
    source+='thing { x=0.0; y=0.0; type=1; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }\n'
    body=bytearray(); directory=bytearray()
    for name,data in [(b'RECOIL',b''),(b'TEXTMAP',source.encode()),(b'ENDMAP',b'')]:
        directory+=struct.pack('<II8s',12+len(body),len(data),name); body+=data
    (addon/'maps/recoil.wad').write_bytes(struct.pack('<4sII',b'PWAD',3,12+len(body))+body+directory)
    (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="RecoilProbe" }\nmap RECOIL "Recoil test" { }\n')
    (addon/'ZSCRIPT').write_text('''version "5.0.0"
class RecoilProbe : EventHandler
{
    bool measuring;
    double peak, step, previous;
    override void WorldTick()
    {
        let p=players[0].mo;
        if (!p) return;
        p.bInvulnerable=true;
        if (measuring) {
            peak=max(peak,abs(p.Pitch));
            step=max(step,abs(p.Pitch-previous));
            previous=p.Pitch;
        }
    }
    override void NetworkProcess(ConsoleEvent e)
    {
        let p=players[0].mo;
        if(e.Name=="recoilbegin") {
            p.Pitch=0; peak=0; step=0; previous=0; measuring=true;
        }
        if(e.Name=="recoilend") {
            measuring=false;
            Console.Printf("RECOIL_SAMPLE %s %.9f %.9f %.9f",p.player.ReadyWeapon.GetClassName(),peak,step,p.Pitch);
            bool ok=abs(p.Pitch)<0.00001 && peak<=e.Args[0]/1000.0+0.00001;
            if(e.Args[0]>0) ok=ok && peak>0.001;
            Console.Printf("UTNT_ASSERT %s: recoil bound and balanced recovery",ok ? "PASS" : "FAIL");
        }
    }
}
''')
    commands=['unbindall','wait 35','give weapons','give ammo']
    for weapon,limit in zip(WEAPONS,LIMITS):
        commands += [f'give {weapon}','give ammo','wait 2',f'use {weapon}','wait 50','netevent recoilbegin','wait 2',
                     '+attack','wait 70','-attack','wait 100',f'netevent recoilend {round(limit*1000)}','wait 3']
    commands += ['echo UTNT_REGRESSION_COMPLETE','echo UTNT_TEST_END','quit']
    result=run_case(a.engine,a.iwad,
        root=out,mod=a.mod,addon=addon,mapname='RECOIL',label='recoil',timeout=130,regression=True,
        commands='; '.join(commands)+'\n',settings=[('use_mouse',False),('use_joystick',False),
        ('i_pauseinbackground',False),('sv_infiniteammo',True),('motionblur',False)])
    samples=[line for line in Path(result['log']).read_text().splitlines() if line.startswith('RECOIL_SAMPLE')]
    result['samples']=samples
    result['ok']=(result['ok'] and result['assertions']==len(WEAPONS)
                  and [s.split()[1] for s in samples]==WEAPONS)
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result['ok']:
        print(Path(result['log']).read_text()[-6000:]); raise SystemExit(1)

if __name__=='__main__': main()
