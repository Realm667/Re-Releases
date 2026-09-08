"""Add an isolated TNT02 sky chamber, cool exterior sectors and replace old ACS thunder.
Only the default sky camera moves. Secondary viewpoints and all gameplay
geometry/specials remain intact. Inputs are never overwritten by this tool.
"""
import argparse,re,subprocess,json
from pathlib import Path
from build_utnt import read_wad,write_wad
PATTERN=r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}'
def block(k,f):return k+'\n{\n'+''.join(f'{a} = {b};\n' for a,b in f.items())+'}\n'
def patch(source,output,acc,zdbsp):
 magic,lumps=read_wad(source);text=next(d for n,d in lumps if n.rstrip(b'\0')==b'TEXTMAP').decode()
 groups={k:[] for k in ('vertex','linedef','sidedef','sector','thing')}
 for m in re.finditer(PATTERN,text):groups[m[1]].append(m)
 fields=lambda m:dict(re.findall(r'(\w+)\s*=\s*([^;]+);',m[2]))
 assert len(groups['sector'])==5046,'Require original TNT02 baseline'
 edits=[];outside=[]
 for i,m in enumerate(groups['sector']):
  f=fields(m)
  if f.get('textureceiling')!='"F_SKY1"':continue
  f.update(lightcolor=0xb9c9dc,desaturation=.16,lightlevel=max(160,int(f.get('lightlevel','160'))))
  edits.append((m.start(),m.end(),block('sector',f)));outside.append(i)
 m=groups['thing'][0];f=fields(m);assert f['type']=='9080' and 'id' not in f
 f.update(x=28000,y=-28000,height=128);edits.append((m.start(),m.end(),block('thing',f)))
 for start,end,s in sorted(edits,reverse=True):text=text[:start]+s+text[end:]
 v=len(groups['vertex']);sd=len(groups['sidedef']);sec=len(groups['sector'])
 points=[(27488,-28512),(27488,-27488),(28512,-27488),(28512,-28512)]
 for x,y in points:text+=block('vertex',dict(x=x,y=y))
 text+=block('sector',dict(heightfloor=-128,heightceiling=512,texturefloor='"F_SKY1"',textureceiling='"F_SKY1"',lightlevel=255))
 for i in range(4):
  text+=block('sidedef',dict(sector=sec,texturemiddle='"-"'))
  text+=block('linedef',dict(v1=v+i,v2=v+(i+1)%4,sidefront=sd+i,blocking='true'))
 script=next(d for n,d in lumps if n.rstrip(b'\0')==b'SCRIPTS').decode()
 start=script.index('// Thunder and Storm');end=script.index('//Ambient Sounds',start)
 script=script[:start]+'// Thunder and Storm: synchronized by UTNTThunderHandler.\n// Script 2 retained as a harmless entry for existing map references.\nscript 2 OPEN { terminate; }\n\n'+script[end:]
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 acs=output.with_suffix('.acs');obj=output.with_suffix('.o');raw=output.with_suffix('.raw.wad')
 acs.write_text(script,encoding='utf-8',newline='\n')
 p=subprocess.run([str(acc),'-i',str(acc.parent),str(acs),str(obj)],capture_output=True,timeout=60)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 changed={b'TEXTMAP':text.encode(),b'SCRIPTS':script.encode(),b'BEHAVIOR':obj.read_bytes()}
 raw.write_bytes(write_wad(magic,[(n,changed.get(n.rstrip(b'\0'),d)) for n,d in lumps if n.rstrip(b'\0') not in [b'ZNODES',b'BLOCKMAP',b'REJECT']]))
 p=subprocess.run([str(zdbsp),'-q','-X','-g','-r','-o',str(output),str(raw)],capture_output=True,timeout=120)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 for p in [acs,obj,raw]:p.unlink()
 return dict(outside_sectors=outside,counts_before={k:len(v) for k,v in groups.items()},default_sky_camera=[28000,-28000,0])
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['input','output','acc','zdbsp']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();print(json.dumps(patch(a.input,a.output,a.acc,a.zdbsp),indent=2))
