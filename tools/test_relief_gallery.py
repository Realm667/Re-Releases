"""Native all-material coverage, walkability, navigation and save/load probes.
Build the gallery addon with build_relief_gallery.py first.
"""
from pathlib import Path
import sys,json,re
from build_relief_gallery import ROOT as R,C
from check_engine import run_case
rooms=json.loads((C/'work/relief-gallery/rooms.json').read_text());results=[];total=len(rooms)
for renderer in ('1','0'):
 cmd='wait 100;screenblocks 12;screenshot "logs/relief-gallery-start-r'+renderer+'.png";+forward;wait 45;-forward;wait 6;netevent reliefprobe;wait 12;'
 for n in [1,15,16,total//2,total]:
  cmd+=f'netevent reliefgoto {n};wait 8;netevent reliefgoto {n};wait 24;screenshot "logs/relief-gallery-room{n}-r{renderer}.png";wait 3;'
 cmd+='netevent reliefprev;wait 16;netevent reliefnext;wait 16;save relief-gallery;wait 6;load relief-gallery;wait 20;netevent reliefprobe;wait 16;echo UTNT_TEST_END;wait 5;quit\n'
 r=run_case(Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe'),Path('F:/DoomDev/DOOM2.WAD'),root=C,mod=R/'tutnt.pk3',addon=C/'builds/tutnt-relief-gallery.pk3',mapname='RELTEST',renderer=renderer,label='relief-gallery-r'+renderer,timeout=55,commands=cmd,settings=[('cl_capfps',True),('vid_scalemode',5),('vid_scale_customwidth',960),('vid_scale_customheight',540),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('use_joystick',False),('con_notifytime',0)],quiet=True)
 out=Path(r['log']).read_text(encoding='utf-8')
 assert r['ok'],out[-5000:]
 assert f'RELIEF_GALLERY|{total}|{total}' in out,out[-5000:]
 visits=re.findall(r'RELIEF_VISIT\|(\d+)\|(\S+)\|(\S+)',out)
 assert all(name==actual==rooms[int(n)-1]['name'] for n,name,actual in visits),visits
 assert {1,15,16,total//2,total-1,total}<={int(v[0]) for v in visits},visits
 positions=re.findall(r'RELIEF_POSITION\|([\d.-]+)\|([\d.-]+)\|(\S+)',out)
 assert positions and positions[0][2]==rooms[0]['name'],positions
 assert positions[-1][2]==rooms[-1]['name'],positions
 assert not any(x in out for x in ['Failed to compile','Unknown texture','Missing texture','UTNT_ASSERT FAIL']),out[-5000:]
 r.update(verified_floor_bindings=total,visited_rooms=sorted({int(v[0]) for v in visits}),walk_into_first_room=True,save_load_last_room=True)
 results.append(r);print(json.dumps(r),flush=True)
(C/'validation/relief-gallery/native.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
