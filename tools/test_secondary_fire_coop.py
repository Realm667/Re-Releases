"""Two-peer secondary-fire network regression using the current integration package."""
from pathlib import Path
import argparse,json,os,subprocess,time,zipfile
from build_utnt import write_wad
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE',str(ROOT/'engine/uzdoom.exe')));p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--port',type=int,default=15327)
p.add_argument('--compile-only',action='store_true');p.add_argument('--extended',action='store_true');p.add_argument('--overlay',action='store_true')
a=p.parse_args();local=ROOT/'tutnt/.codex';out=local/('logs/secondary-fire/coop-extended' if a.extended else 'logs/secondary-fire/coop');out.mkdir(parents=True,exist_ok=True)
reports=local/'validation/secondary-fire';reports.mkdir(parents=True,exist_ok=True)
fixture=local/('builds/utnt-secondary-coop-extended.pk3' if a.extended else 'builds/utnt-secondary-coop.pk3')
text='namespace="ZDoom";\n'
for x,y in [(-1536,-1536),(-1536,1536),(1536,1536),(1536,-1536)]:text+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
text+='sector { heightfloor=0; heightceiling=256; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=192; }\n'
for i in range(4):text+=f'sidedef {{ sector=0; texturemiddle="METAL2"; }}\nlinedef {{ v1={i}; v2={(i+1)%4}; sidefront={i}; blocking=true; }}\n'
for i in range(2):text+=f'thing {{ x={i*100}.0; y=0.0; angle=0; type={i+1}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }}\n'
with zipfile.ZipFile(fixture,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('ZSCRIPT','version "5.0.0"\n#include "tests.zc"\n#include "'+('extended-coop.zc' if a.extended else 'coop.zc')+'"\n')
 if a.overlay:
  for f in ['zscript/UTNT_SecondaryFire.zc','actors/weapons.txt','zscript/UTNT_Presentation.zc','zscript/UTNT_BurnDeath.zc','shaders/pressure-wave.fp','zscript/UTNT_PickupFeedback.zc','zscript/UTNT_EffectGlow.zc','LANGUAGE.txt','TEXTURES.txt','sounds/UGRBOUNC.ogg']:z.write(ROOT/'tutnt'/f,f)
  z.writestr('GLDEFS',(ROOT/'tutnt/gldefs/GLDEFS.secondary-fire').read_bytes())
  z.writestr('SNDINFO','weapons/grenadebounce UGRBOUNC\n')
 for f in ['tests.zc','coop.zc','extended-coop.zc']:z.write(ROOT/'tools/fixtures/secondary-fire'/f,f)
 z.writestr('MAPINFO','gameinfo { AddEventHandlers="'+('ExtendedSecondaryCoopTest' if a.extended else 'SecondaryCoopTest')+'" }\nmap SECCOOP "Secondary coop test" {}\n')
 z.writestr('maps/SECCOOP.wad',write_wad(b'PWAD',[(b'SECCOOP',b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')]))
if a.compile_only:
 from check_engine import run_case
 result=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=fixture,label='coop-compile')
 raise SystemExit(0 if result['ok'] else 1)
children=[];results=[];checksums=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
 for i in range(2):
  config=out/f'peer-{i}.ini';config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\n')
  cfg=out/f'peer-{i}.cfg';cfg.write_text(('wait 125; +altattack; wait 1; -altattack'+('; wait 255; +altattack; wait 1; -altattack' if a.extended else '')+'\n') if i==0 else '')
  args=[a.engine,'-iwad',a.iwad,'-file',str(a.mod.resolve()),str(fixture),'-config',str(config),'-noautoload','-nosound','-stdout','-noidle','-rngseed','667','+playerclass','Marine','+vid_fullscreen','false','+vid_preferbackend','1','+use_mouse','false','+i_pauseinbackground','false','+UTNT_fxquality',str(0 if i==0 and a.extended else 3),'+map','SECCOOP','+exec',str(cfg)]
  args+=['-host','2','-port',str(a.port)] if i==0 else ['-join',f'127.0.0.1:{a.port}']
  f=(out/f'peer-{i}.log').open('wb');child=subprocess.Popen(args,cwd=out,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW);children.append((child,f,i))
  if i==0:time.sleep(1)
 deadline=time.monotonic()+65
 while time.monotonic()<deadline:
  outputs=[(out/f'peer-{i}.log').read_text(errors='replace') for _,_,i in children]
  if all('SECONDARY_COOP_COMPLETE' in s for s in outputs) or any(c.poll() is not None for c,_,_ in children):break
  time.sleep(.2)
 for child,f,i in children:
  if child.poll() is None:child.terminate()
  child.wait(timeout=5);f.close();s=(out/f'peer-{i}.log').read_text(errors='replace')
  checksum=next((line for line in s.splitlines() if line.startswith('SECONDARY_COOP_CHECKSUM')),None);checksums.append(checksum)
  result={'peer':i,'ok':'SECONDARY_COOP_COMPLETE' in s and 'UTNT_ASSERT FAIL' not in s and 'VM execution aborted' not in s,'assertions':s.count('UTNT_ASSERT PASS'),'checksum':checksum};results.append(result)
  if not result['ok']:print(s[-6000:])
finally:
 for child,f,_ in children:
  if child.poll() is None:child.kill();child.wait()
  if not f.closed:f.close()
ok=len(results)==2 and all(x['ok'] for x in results) and checksums[0] is not None and checksums[0]==checksums[1]
report={'ok':ok,'peers':results};(reports/('coop-extended.json' if a.extended else 'coop.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if ok else 1)
