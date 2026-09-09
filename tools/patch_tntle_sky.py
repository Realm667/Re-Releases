"""Append two isolated sky rooms; preserve the original gameplay geometry.
Input must be a pre-change TNTLE. Never applies twice to the same map.
"""
from pathlib import Path
import re,argparse,subprocess,tempfile,json
from build_utnt import read_wad,write_wad
PAT=r'\b(thing|vertex|linedef|sidedef|sector)\s*(?://[^\n]*\n\s*)?\{[^}]*\}'
def patch(source,dest,acc,zdbsp):
 magic,entries=read_wad(source);lumps={n.rstrip(b'\0'):d for n,d in entries}
 txt=lumps[b'TEXTMAP'].decode();counts={k:len(re.findall(r'\b'+k+r'\s*(?://[^\n]*\n\s*)?\{',txt)) for k in ['thing','vertex','linedef','sidedef','sector']}
 if 'ULCN' in txt:raise ValueError('TNTLE already has the new sky rooms')
 changed=[]
 def camera(m):
  b=m[0]
  if m[1]!='thing' or not re.search(r'\btype\s*=\s*9080\s*;',b):return b
  ident=re.search(r'\bid\s*=\s*(\d+)\s*;',b);tid=int(ident[1]) if ident else 0
  if tid not in (0,13):return b
  vals={'x':-24576 if tid==0 else -20480,'y':24576,'height':512}
  for k,v in vals.items():
   b,n=re.subn(r'(\b'+k+r'\s*=\s*)[^;]+;',lambda q:q[1]+str(v)+';',b)
   if not n:b=b[:-1]+f'{k}={v};\n}}'
  changed.append(tid);return b
 txt=re.sub(PAT,camera,txt);assert sorted(changed)==[0,13]
 extra=['\n// TNTLE private sky rooms. Shader room centers match these coordinates.\n']
 def block(kind,values):
  def val(v):return 'true' if v is True else 'false' if v is False else '"'+v+'"' if isinstance(v,str) else str(v)
  extra.append(kind+'\n{\n'+''.join(f'{k} = {val(v)};\n' for k,v in values.items())+'}\n')
 for j,(cx,prefix) in enumerate([(-24576,'ULC'),(-20480,'ULN')]):
  cy=24576;vi=counts['vertex']+4*j;si=counts['sector']+j;side=counts['sidedef']+4*j
  for x,y in [(cx-512,cy-512),(cx-512,cy+512),(cx+512,cy+512),(cx+512,cy-512)]:block('vertex',{'x':x,'y':y})
  # Clockwise perimeter: front/right side faces the inside of the room.
  for k,face in enumerate(['E','S','W','N']):
   block('sidedef',{'sector':si,'texturemiddle':prefix+face,'light':255,'lightabsolute':True,'nofakecontrast':True})
   block('linedef',{'v1':vi+k,'v2':vi+(k+1)%4,'sidefront':side+k,'blocking':True,'dontdraw':True})
  block('sector',{'special':90,'heightfloor':-512,'heightceiling':512,'texturefloor':prefix+'D','textureceiling':prefix+'U','lightlevel':255,'lightfloor':255,'lightfloorabsolute':True,'lightceiling':255,'lightceilingabsolute':True,'xpanningfloor':512,'ypanningfloor':512,'xpanningceiling':512,'ypanningceiling':512})
 txt+=''.join(extra)
 scripts=lumps[b'SCRIPTS'].decode('cp1252')
 pat=r'script\s+14\s+OPEN\s*//Light show for skybox number 2\s*\{[^}]*\}'
 scripts,n=re.subn(pat,'script 14 OPEN\n{\n\t// Retired sky room: private TNTLE materials now own the distant glow.\n}',scripts);assert n==1
 with tempfile.TemporaryDirectory(prefix='tntle-sky-') as temp:
  tmp=Path(temp);src=tmp/'tntle.acs';obj=tmp/'tntle.o';src.write_bytes(scripts.encode('cp1252'))
  p=subprocess.run([str(acc),'-i',str(acc.parent),str(src),str(obj)],capture_output=True)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
  changed={b'TEXTMAP':txt.encode(),b'SCRIPTS':scripts.encode('cp1252'),b'BEHAVIOR':obj.read_bytes()}
  raw=tmp/'input.wad';raw.write_bytes(write_wad(magic,[(n,changed.get(n.rstrip(b'\0'),d)) for n,d in entries]))
  dest.parent.mkdir(parents=True,exist_ok=True)
  p=subprocess.run([str(zdbsp),'-q','-X','-g','-r',str(raw),'-o',str(dest)],capture_output=True)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
  # ZDBSP strips blank lines. Restore the authoritative TEXTMAP only after
  # verifying it did not alter or reorder any structural block/field.
  bm,be=read_wad(dest);built=next(d for n,d in be if n.rstrip(b'\0')==b'TEXTMAP').decode()
  def normalized(t):
   return {k:[re.sub(r'\s+','',m[0][m[0].index('{'):]) for m in re.finditer(PAT,t) if m[1]==k] for k in counts}
  assert normalized(built)==normalized(txt),'node builder changed map topology'
  dest.write_bytes(write_wad(bm,[(n,txt.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in be]))
 print(json.dumps({'cameras':changed.keys().__str__(),'original_counts':counts,'appended':{'vertex':8,'linedef':8,'sidedef':8,'sector':2}}))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('dest',type=Path);p.add_argument('--acc',type=Path,required=True);p.add_argument('--zdbsp',type=Path,required=True)
 p.add_argument('--area-table',type=Path,help='Existing TNTLE area alignment table; update topology header only')
 a=p.parse_args()
 table=None
 if a.area_table:
  table=a.area_table.read_bytes()
  assert table.splitlines()[0]==b'H|15926|18259|31163|2984|7597','unexpected alignment table topology'
 patch(a.source,a.dest,a.acc,a.zdbsp)
 if table is not None:
  assert a.area_table.read_bytes()==table,'alignment table changed during map build'
  a.area_table.write_bytes(table.replace(b'H|15926|18259|31163|2984|7597',b'H|15934|18267|31171|2986|7597',1))
