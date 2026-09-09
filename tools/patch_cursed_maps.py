"""Install the shared Cursed Peak clock without changing gameplay geometry.

The original anonymous sky camera becomes an inert MapSpot. Only TEXTMAP's
single thing type, SCRIPTS' daylight block, and recompiled BEHAVIOR may change.
"""
import argparse,re
from pathlib import Path
from build_utnt import read_wad,write_wad
ROOT=Path(__file__).resolve().parent.parent
BLOCK='''//Global Variables
global int 1 : g_lightval;
// Cursed Peak owns previously unused global slot 12; shared across this hub.
global int 12 : g_cursedskytime;
int time = 18000,tag1 = 2,tag2 = 3,tag3 = 1,tag4 = 19,tag5 = 14,daylight;

Script 23 OPEN
{
    ACS_Execute(21,0);
}

// RETURN runs once per player. Ordinary Execute is idempotent here;
// ExecuteAlways would create multiple clock updaters in cooperative play.
script "UTNT_CursedSkyResume" RETURN
{
    ACS_Execute(21,0);
}

Script 21 (VOID)
{
    while(TRUE)
    {
        daylight=g_lightval;
        // This exact neutral fade drives both tagged sectors and sky haze.
        ScriptCall("UTNTCursedSkyHandler","SetClock",g_lightval,g_cursedskytime,255-165*g_lightval/time);
        delay(1);
        if(ScriptCall("UTNTCursedSkyHandler","ClockRunning"))
        {
            if(g_lightval<time) g_lightval++;
            // Common multiple of both cloud layers and the snowfall cycle.
            g_cursedskytime=(g_cursedskytime+1)%1050000;
        }
    }
}

Script 22 UNLOADING
{
    // The engine suspends this map's updater with the hub snapshot. Do not
    // terminate it or overwrite globals from a stale map-local daylight value.
}

script "UTNT_CursedSkySetTime" (int value)
{
    if(value<0) value=0;
    if(value>18000) value=18000;
    g_lightval=value;
    daylight=value;
    ScriptCall("UTNTCursedSkyHandler","SetClock",g_lightval,g_cursedskytime,255-165*g_lightval/time);
    SetResultValue(g_lightval);
}

'''

def patch(path):
 magic,entries=read_wad(path);out=[]
 for name,raw in entries:
  key=name.rstrip(b'\0')
  if key==b'TEXTMAP':
   text=raw.decode('utf-8')
   def camera(m):
    block=m[0]
    return re.sub(r'(type\s*=\s*)9080(?=\s*;)',r'\g<1>9001',block) if re.search(r'type\s*=\s*9080\s*;',block) else block
   text,n=re.subn(r'thing\s*(?://[^\n]*)?\s*\{[^}]*\}',camera,text)
   raw=text.encode('utf-8')
  if key==b'SCRIPTS':
   text=raw.decode('cp1252');start=text.index('//Global Variables',text.index('//DAY TO NIGHT TRANSITION//'))
   end=text.index('//Objective 1',start)
   newline='\r\n' if '\r\n' in text else '\n'
   text=text[:start]+BLOCK.replace('\n',newline)+text[end:];raw=text.encode('cp1252')
  out.append((name,raw))
 path.write_bytes(write_wad(magic,out))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args()
 for name in ['tnt03a1','tnt03a2']:patch(a.root/f'tutnt/maps/{name}.wad')
