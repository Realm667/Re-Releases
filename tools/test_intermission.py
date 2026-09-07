"""Real TNT01 exit, inherited counters and continuation, plus layout screenshots.
Set UTNT_ENGINE and UTNT_IWAD. The addon provides empty/stress statistics only.
"""
import json, os, pathlib, struct
from check_engine import ROOT, run_case

def main():
    results=[]
    for stress, renderer in [(False, '1'), (True, '0')]:
        label='intermission-stress' if stress else 'intermission-empty'
        c=['wait 100','netevent interexit','wait 60']
        def snap(name): c.extend(['wait 15',f'screenshot logs/{label}-{name}.png'])
        snap('percent')
        c.extend(['wi_percents false']);snap('counts')
        c.extend(['wi_showtotaltime false']);snap('no-total')
        c.extend(['wi_showtotaltime true','language deu','vid_setsize 1024 768']);snap('de-4by3')
        c.extend(['language enu','vid_setsize 1920 1080']);snap('1080p')
        c.extend(['vid_setsize 2560 1080']);snap('ultrawide')
        c.extend(['wait 220','echo UTNT_TEST_END','wait 5','quit'])
        result=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],
            addon=ROOT/'tools/intermission-tests', mapname='TNT01',renderer=renderer,
            label=label,timeout=45,commands='; '.join(c)+'\n',settings=[
                ('wi_percents','true'),('wi_showtotaltime','true'),('utnt_imstress',str(stress).lower()),
                ('language','enu'),('con_notifytime',0),('i_pauseinbackground','false'),('vid_activeinbackground','true')])
        log=pathlib.Path(result['log']).read_text(encoding='utf-8')
        if result['assertions']!=8: result['errors'].append('expected eight counter/continuation assertions')
        for error in ['Unknown command','reverting to default','Unknown font']:
            if error in log: result['errors'].append(error)
        for name,size in [('de-4by3',(1024,768)),('1080p',(1920,1080)),('ultrawide',(2560,1080))]:
            shot=ROOT/'logs'/f'{label}-{name}.png'
            actual=struct.unpack('>II',shot.read_bytes()[16:24]) if shot.exists() else None
            if actual!=size:result['errors'].append(f'{name}: {actual} instead of {size}')
        result['ok']=result['ok'] and not result['errors'];results.append(result)
    (ROOT/'logs/intermission-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))
    raise SystemExit(0 if all(r['ok'] for r in results) else 1)
if __name__=='__main__':main()
