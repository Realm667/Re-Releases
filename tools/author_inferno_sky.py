"""One-time explicit authoring of the TNT04B fire sky room; never run at build.
Preserves gameplay geometry, camera bindings and all original actors.
"""
from pathlib import Path
import subprocess,json
from build_utnt import read_wad,write_wad,atomic_write
from test_caldera_structure import parse
from author_cavern import edit_text
ROOT=Path(__file__).resolve().parents[1]
def author(root=ROOT):
 path=root/'tutnt/maps/tnt04b.wad';magic,entries=read_wad(path);l,g=parse(path)
 if b'Authored TNT04B inferno' in l['TEXTMAP']:raise ValueError('Already authored; edit production map directly.')
 assert g['thing'][466]['type']=='9080' and g['thing'][466]['id']=='3'
 changes={'sector':{},'sidedef':{},'linedef':{}}
 for i in (1449,1450):
  assert g['sector'][i]['id']=='23'
  changes['sector'][i]=dict(texturefloor='"UFID"',textureceiling='"UFIU"',lightcolor=0xffffff,fadecolor=0,special=90,xscalefloor=4,yscalefloor=4,xscaleceiling=4,yscaleceiling=4)
 for i,lne in enumerate(g['linedef']):
  side=int(lne.get('sidefront',-1))
  if side<0 or int(g['sidedef'][side]['sector']) not in (1449,1450):continue
  if 'sideback' in lne:
   for k in ('sidefront','sideback'):changes['sidedef'][int(lne[k])]=dict(texturemiddle='"-"')
  else:
   a,b=[g['vertex'][int(lne[k])] for k in ('v1','v2')];mx=(float(a['x'])+float(b['x']))/2;my=(float(a['y'])+float(b['y']))/2
   face='E' if mx==-1408 else 'W' if mx==-1152 else 'N' if my==128 else 'S'
   changes['sidedef'][side]=dict(texturemiddle=json.dumps('UFI'+face),scalex_mid=4,scaley_mid=8)
   changes['linedef'][i]=dict(special=0)
 text=edit_text(l['TEXTMAP'].decode(),changes,'\n// Authored TNT04B inferno. Textures and room fields remain editable in UDB.\n')
 script=l['SCRIPTS'].decode();script=script.replace('Sector_SetCeilingScale(23, 0, 64, 0, 64);','// Inferno sky room uses authored texture scales.').replace('Sector_SetFloorScale(23, 3, 0, 3, 0);','').replace('sector_setfade(23, 255, 120, 0);','// Inferno colors are authored in their materials; no orange sector fog.')
 work=root/'tutnt/.codex/work/tnt04b-second-fire-sky';src=work/'tnt04b.acs';obj=work/'tnt04b.o';src.write_text(script,encoding='utf-8')
 acc=Path('F:/DoomDev/Tools/UltimateDoombuilder/Compilers/ZDoom/acc.exe')
 result=subprocess.run([str(acc),'-i',str(acc.parent),str(src),str(obj)],capture_output=True);assert result.returncode==0,(result.stdout+result.stderr).decode(errors='replace')
 repl={b'TEXTMAP':text.encode(),b'SCRIPTS':script.encode(),b'BEHAVIOR':obj.read_bytes()}
 atomic_write(path,write_wad(magic,[(n,repl.get(n.rstrip(b'\0'),d)) for n,d in entries]))
 print(json.dumps({k:len(v) for k,v in changes.items()}))
if __name__=='__main__':author()
