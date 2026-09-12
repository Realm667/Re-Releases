"""Verify the exact second-pass map edits, localization, and voice timing against committed sources."""
import hashlib,io,json,math,pathlib,re,struct,subprocess,tempfile
from build_utnt import ROOT,read_wad
from audit_campaign import udmf

BASE='179735e36'
def original(path):
    return subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'-C',str(ROOT),'show',BASE+':'+path])
def wad_bytes(data):
    _,count,directory=struct.unpack_from('<4sII',data)
    return {name.rstrip(b'\0').decode():data[start:start+size] for start,size,name in (struct.unpack_from('<II8s',data,directory+i*16) for i in range(count))}
def main():
    checks=[]
    def check(ok,message):
        checks.append(dict(ok=bool(ok),check=message))
        if not ok:raise AssertionError(message)
    for p in sorted((ROOT/'tutnt/maps').glob('*.wad')):
        rel=p.relative_to(ROOT).as_posix();old=wad_bytes(original(rel));new=wad_bytes(p.read_bytes())
        if p.stem=='tnt02':
            a,b=udmf(old['TEXTMAP'].decode()),udmf(new['TEXTMAP'].decode())
            for kind in ('vertex','sector','thing'):check(a[kind]==b[kind],f'TNT02 {kind} definitions unchanged')
            for kind in ('linedef','sidedef'):check(b[kind][:-1]==a[kind],f'TNT02 all existing {kind} indices and properties preserved')
            check(b['linedef'][-1]==dict(v1=7783,v2=7779,sidefront=len(a['sidedef']),blocking=True,blocksound=True),'TNT02 only missing light-niche edge appended')
            check(b['sidedef'][-1]==dict(sector=1720,texturemiddle='QTECH25'),'TNT02 new edge uses adjacent niche material')
            allowed={'TEXTMAP','ZNODES','GL_NODES','GL_VERT','GL_SEGS','GL_SSECT','BLOCKMAP','REJECT'}
        else:allowed={'SCRIPTS','BEHAVIOR'}
        check(all(old.get(n)==new.get(n) for n in old.keys()|new.keys() if n not in allowed),p.stem+' unrelated map lumps unchanged')
        if p.stem not in ('tnt03a1','tnt04cn'):check(old['SCRIPTS']==new['SCRIPTS'],p.stem+' embedded ACS source preserved')
        else:
            expected=old['SCRIPTS'].decode()
            if p.stem=='tnt03a1':expected=expected.replace('acs_terminate (14, 1);',"acs_terminate (14, 0); // Stop this map's rocket hazard.")
            else:expected=expected.replace('ACS_Execute(669,0,0,0,0);','// IntroText is started by the common library OPEN script; legacy 669 no longer exists.')
            check(new['SCRIPTS'].decode()==expected,p.stem+' only reviewed ACS correction applied')
    current=(ROOT/'tutnt/source/tutnt.acs').read_text()
    before=original('tutnt/source/tutnt.acs').decode().replace('\r\n','\n')
    def boss_end(s):return s[s.index('\tif(boss==1)'):s.index('script "UTNTCheckpoint"')].strip()
    check(boss_end(before)==boss_end(current),'All five original boss completion blocks unchanged')
    keys=set(re.findall(r'(?m)^\s*(\w+)\s*=',(ROOT/'tutnt/language/LANGUAGE.enu').read_text()))
    de=set(re.findall(r'(?m)^\s*(\w+)\s*=',(ROOT/'tutnt/language/LANGUAGE.deu').read_text()))
    check(de<=keys,'German entries have English fallback keys')
    check(all(f'UTNT_VOICE_{i:03}' in de for i in range(19,54)),'All 35 player voice subtitles translated')
    durations=[]
    for i in range(1,36):
        d=next((ROOT/'tutnt/sounds').rglob(f'VOC{i:03}.ogg')).read_bytes();header=d.index(b'\x01vorbis');rate=struct.unpack_from('<I',d,header+12)[0]
        off=0;last=0
        while off<len(d):
            check(d[off:off+4]==b'OggS',f'VOC{i:03} Ogg page integrity')
            last=max(last,struct.unpack_from('<q',d,off+6)[0]);segments=d[off+26];off+=27+segments+sum(d[off+27:off+27+segments])
        durations.append(math.ceil(last*35/rate))
    stored=list(map(int,re.search(r'int voiceDuration\[35\]=\{([^}]+)',current)[1].split(',')))
    check(stored==durations,'Shared voice timings match original Ogg durations without runtime audio-device queries')
    check('S_GetLength' not in (ROOT/'tutnt/zscript/UTNT_Presentation.zc').read_text(),'Sound-device-dependent length never changes shared voice timing')
    report=dict(baseline=BASE,checks=checks,source_hashes={p.relative_to(ROOT/'tutnt').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'tutnt').rglob('*')) if p.is_file()})
    (ROOT/'logs/second-pass-structure.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(passed=len(checks),files=len(report['source_hashes']))))
if __name__=='__main__':main()
