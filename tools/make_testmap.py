from pathlib import Path
from build_utnt import write_wad
root=Path(__file__).resolve().parent.parent/'tools/runtime-tests/maps';root.mkdir(exist_ok=True)
s='namespace="ZDoom";\n'
for x,y in [(-512,-512),(-512,512),(512,512),(512,-512)]:s+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
s+='sector { heightfloor=0; heightceiling=192; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=192; }\n'
for i in range(4):
 s+='sidedef { sector=0; texturemiddle="STARTAN3"; }\n'
 s+=f'linedef {{ v1={i}; v2={(i+1)%4}; sidefront={i}; blocking=true; }}\n'
for i in range(8):s+=f'thing {{ x={-200+i*40}.0; y=-64.0; angle=0; type={i+1 if i<4 else 4001+i-4}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }}\n'
(root/'utnttest.wad').write_bytes(write_wad(b'PWAD',[(b'UTNTTEST',b''),(b'TEXTMAP\0',s.encode()),(b'ENDMAP\0\0',b'')]))
