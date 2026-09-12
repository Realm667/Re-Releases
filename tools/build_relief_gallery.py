"""Build the walkable RELTEST addon from every registered organic relief variant.

The addon contains geometry, signs and navigation only. Load it AFTER tutnt.pk3.
Test packages and local launchers stay under tutnt/.codex; no campaign map changes.
"""
from pathlib import Path
import argparse,json,math,struct,zipfile,hashlib,collections
from build_utnt import read_wad,write_wad
ROOT=Path(__file__).resolve().parent.parent
C=ROOT/'tutnt/.codex'
COLS=15;PITCH=384;ROW=512


def build(iwad=Path('F:/DoomDev/DOOM2.WAD'),engine=Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe')):
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    names=[n for m in sorted(manifest['materials'],key=lambda m:m['name']) for n in m['variants']]
    assert len(names)==len(set(names)) and set(names)==set(manifest['variants'])
    total=len(names);rows=math.ceil(total/COLS);width=COLS*PITCH
    work=C/'work/relief-gallery';work.mkdir(parents=True,exist_ok=True)
    (work/'saves').mkdir(exist_ok=True);(C/'builds').mkdir(exist_ok=True)
    vertices=[];vertex_ids={};sides=[];lines=[];sectors=[];cells={};rooms=[]
    def sec(floor,ceiling=192,height=0,light=208):
        i=len(sectors);sectors.append(dict(texturefloor=floor,textureceiling='CEIL5_1',heightfloor=height,heightceiling=ceiling,lightlevel=light));return i
    corridor=sec('FLOOR4_8',light=184)
    for i,n in enumerate(names):
        x=i%COLS*PITCH;y=i//COLS*ROW
        rooms.append(dict(number=i+1,name=n,family=manifest['variants'][n]['family'],sector=sec(n),sign_sector=sec('CEIL5_1',height=160,light=240),x=x+192,y=y+320,sign=f'RLG{i:05d}'))
    xs=sorted(set([-192,0,width,width+192]+[x for i in range(COLS) for x in (i*PITCH+16,i*PITCH+368,(i+1)*PITCH)]))
    ys=sorted(set([y for j in range(rows) for y in (j*ROW,j*ROW+192,j*ROW+480,j*ROW+496,(j+1)*ROW)]))
    for yi,(ya,yb) in enumerate(zip(ys,ys[1:])):
        row=int(ya//ROW);zone=int(ya%ROW)
        for xi,(xa,xb) in enumerate(zip(xs,xs[1:])):
            cx=(xa+xb)/2
            if cx<0 or cx>width or zone==0:cells[xi,yi]=corridor;continue
            col=int(cx//PITCH);local=cx-col*PITCH;i=row*COLS+col
            if 16<local<368 and i<total and zone in (192,480):cells[xi,yi]=rooms[i]['sector' if zone==192 else 'sign_sector']
    # Every sample floor is reachable on foot through a corridor. Sign shelves
    # deliberately sit above head height and are excluded from walkability.
    walk={p:s for p,s in cells.items() if sectors[s]['heightfloor']==0}
    todo=[next(p for p,s in walk.items() if s==corridor)];seen=set(todo)
    while todo:
        x,y=todo.pop()
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if p in walk and p not in seen:seen.add(p);todo.append(p)
    assert seen==set(walk),'Disconnected walkable gallery area'
    def vertex(p):
        if p not in vertex_ids:vertex_ids[p]=len(vertices);vertices.append(p)
        return vertex_ids[p]
    room_by_sector={r[k]:r for r in rooms for k in ('sector','sign_sector')}
    def side(s,solid):
        if s==corridor:tex='METAL2'
        else:
            r=room_by_sector[s];tex=r['sign'] if s==r['sign_sector'] else r['name']
        i=len(sides);sides.append(dict(sector=s,texturemiddle=tex if solid else '-',texturebottom=tex,texturetop=tex));return i
    edges={}
    for (xi,yi),s in cells.items():
        x0,x1=xs[xi],xs[xi+1];y0,y1=ys[yi],ys[yi+1]
        points=[(x0,y0),(x0,y1),(x1,y1),(x1,y0)]
        for a,b in zip(points,points[1:]+points[:1]):
            key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b,s))
    for records in edges.values():
        if len(records)==2 and records[0][2]==records[1][2]:continue
        a,b,s=records[0];line=dict(v1=vertex(a),v2=vertex(b),sidefront=side(s,len(records)==1))
        if len(records)==2:line.update(sideback=side(records[1][2],False),twosided=True)
        else:line['blocking']=True
        lines.append(line)
    def block(kind,fields):
        def value(v):return json.dumps(v) if not isinstance(v,bool) else str(v).lower()
        return kind+' { '+' '.join(k+'='+value(v)+';' for k,v in fields.items())+' }\n'
    text='namespace="ZDoom";\n'
    text+=''.join(block('vertex',dict(x=x,y=y)) for x,y in vertices)
    text+=''.join(block('sector',s) for s in sectors)
    text+=''.join(block('sidedef',s) for s in sides)
    text+=''.join(block('linedef',s) for s in lines)
    flags=dict(skill1=True,skill2=True,skill3=True,skill4=True,skill5=True,single=True,coop=True,dm=True)
    text+=block('thing',dict(x=192,y=96,angle=90,type=1,**flags))
    for r in rooms:text+=block('thing',dict(x=r['x'],y=r['y'],height=118,type=9800,arg0=180,arg1=172,arg2=160,arg3=128,**flags))
    mapdata=write_wad(b'PWAD',[(b'RELTEST',b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')])
    lumps={n.rstrip(b'\0').decode():b for n,b in read_wad(iwad)[1]}
    textures=[]
    for r in rooms:
        title=f"{r['number']:03d}  {r['name']}"
        widths=[4 if ch==' ' else struct.unpack_from('<H',lumps[f'STCFN{ord(ch):03d}'])[0]+1 for ch in title]
        px=(176-sum(widths))//2
        textures.append(f'Texture {r["sign"]}, 176, 16 {{ XScale 0.5 YScale 0.5')
        for x in (0,64,128):textures.append(f'Patch "WALL00_1", {x}, 0')
        for ch,w in zip(title,widths):
            if ch!=' ':textures.append(f'Patch "STCFN{ord(ch):03d}", {px}, 4')
            px+=w
        textures.append('}')
    # Values are read from map geometry at runtime, not user-maintained lists.
    helpers=[]
    for start in range(0,total,48):
        cases=' '.join(f'case {i}: return "{rooms[i]["name"]}";' for i in range(start,min(total,start+48)))
        helpers.append(f'clearscope static String Name{start}(int i) {{ switch(i) {{ {cases} }} return "?"; }}')
    dispatch=' '.join(f'if(i<{min(total,start+48)})return Name{start}(i);' for start in range(0,total,48))
    arrays='\n'.join(helpers)+f'\nclearscope static String NameAt(int i) {{ {dispatch} return "?"; }}'
    zscript='''version "4.14"
class ReliefGallery : EventHandler {
 int Current;
 ARRAYS
 int Near(Actor p) { return clamp(int(p.Pos.Y/512),0,ROWS-1)*15+clamp(int(p.Pos.X/384),0,14); }
 override void WorldTick() {
  if(!(level.MapName~=="RELTEST"))return;
  if(players[0].mo)Current=clamp(Near(players[0].mo),0,TOTAL-1);
  if(level.time==2) {
   int valid=0;
   for(int i=0;i<TOTAL;i++) {
    String actual=TexMan.GetName(level.Sectors[1+i*2].GetTexture(Sector.floor));
    if(actual~==NameAt(i))valid++;else Console.Printf("UTNT_ASSERT FAIL: relief floor %d %s",i,actual);
   }
   Console.Printf("RELIEF_GALLERY|%d|TOTAL",valid);
   Console.Printf("%s",StringTable.Localize("$RLG_HELP"));
  }
 }
 override void NetworkProcess(ConsoleEvent e) {
  if(!(level.MapName~=="RELTEST"))return;
  if(e.Name=="reliefprobe") {
   let p=players[0].mo;if(p)Console.Printf("RELIEF_POSITION|%.1f|%.1f|%s",p.Pos.X,p.Pos.Y,TexMan.GetName(p.CurSector.GetTexture(Sector.floor)));
   return;
  }
  int target=-1;
  if(e.Name=="reliefgoto")target=clamp(e.Args[0]-1,0,TOTAL-1);
  if(e.Name=="reliefnext")target=(Current+1)%TOTAL;
  if(e.Name=="reliefprev")target=(Current+TOTAL-1)%TOTAL;
  if(target<0)return;
  let p=players[0].mo;if(!p)return;
  p.Vel=(0,0,0);p.SetOrigin(((target%15)*384+192,(target/15)*512+260,0),false);
  p.Angle=90;p.Pitch=0;Current=target;
  Console.Printf("RELIEF_VISIT|%d|%s|%s",target+1,NameAt(target),TexMan.GetName(p.CurSector.GetTexture(Sector.floor)));
 }
 override void RenderOverlay(RenderEvent e) {
  if(!(level.MapName~=="RELTEST"))return;
  String label=String.Format("%03d / TOTAL   %s",Current+1,NameAt(Current));
  Screen.DrawText(Font.GetFont("SmallFont"),Font.CR_WHITE,12,8,label,DTA_VirtualWidth,640,DTA_VirtualHeight,360,DTA_KeepRatio,true);
 }
}
'''.replace('ARRAYS',arrays).replace('ROWS',str(rows)).replace('TOTAL',str(total))
    languages={'en':('Relief material gallery','Walk through the gallery. Console: netevent reliefnext / reliefprev / reliefgoto N.'),'de':('Relief-Materialgalerie','Galerie frei begehbar. Konsole: netevent reliefnext / reliefprev / reliefgoto N.'),'es':('Galeria de materiales con relieve','Recorre la galeria. Consola: netevent reliefnext / reliefprev / reliefgoto N.'),'fr':('Galerie des materiaux en relief','Parcourez la galerie. Console : netevent reliefnext / reliefprev / reliefgoto N.')}
    language='\n'.join(f'[{lang}]\nRLG_TITLE = "{title}";\nRLG_HELP = "{help}";\n' for lang,(title,help) in languages.items())
    payload={'maps/RELTEST.wad':mapdata,'MAPINFO':b'GameInfo { AddEventHandlers="ReliefGallery" }\nmap RELTEST "$RLG_TITLE" { levelnum=199 nointermission }\n','ZSCRIPT':zscript.encode(),'TEXTURES':'\n'.join(textures).encode(),'LANGUAGE':language.encode(),'relief-gallery.json':json.dumps(rooms,indent=2).encode()}
    addon=C/'builds/tutnt-relief-gallery.pk3'
    with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in payload.items():z.writestr(name,data)
    (work/'RELTEST.wad').write_bytes(mapdata)
    (work/'TEXTMAP.txt').write_text(text,encoding='utf-8')
    (work/'rooms.json').write_text(json.dumps(rooms,indent=2),encoding='utf-8')
    (work/'Texturenverzeichnis.txt').write_text('\n'.join(f"{r['number']:03d}  {r['name']:12}  {r['family']}" for r in rooms)+'\n',encoding='utf-8')
    launcher='@echo off\r\ncd /d "'+str(work)+'"\r\n"'+str(engine)+'" -iwad "'+str(iwad)+'" -file "'+str(ROOT/'tutnt.pk3')+'" "'+str(addon)+'" -config "'+str(work/'play.ini')+'" -savedir "'+str(work/'saves')+'" +map RELTEST\r\n'
    (work/'Relief-Test-starten.cmd').write_bytes(launcher.encode('utf-8'))
    report=dict(ok=True,materials=len(manifest['materials']),variants=total,rooms=len(rooms),sectors=len(sectors),linedefs=len(lines),connected_walkable_cells=len(seen),addon=str(addon),addon_sha256=hashlib.sha256(addon.read_bytes()).hexdigest())
    dest=C/'validation/relief-gallery';dest.mkdir(parents=True,exist_ok=True)
    (dest/'geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report));return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'));p.add_argument('--engine',type=Path,default=Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe'));a=p.parse_args();build(a.iwad,a.engine)
