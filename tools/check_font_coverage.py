"""Require real, intact mod glyphs for every localized character; no font fallback."""
from pathlib import Path
import argparse,hashlib,json,re,struct,zipfile,zlib
from check_localization import ROOT,COLOR,catalogs
FONTS=('smallfont','bigfont','bigupper','ucrbig')
def required_characters(data):
    chars=set()
    for lang,entries in data.items():
        for value in entries.values():
            value=COLOR.sub('',value)
            value=re.sub(r'\\[nrt]',' ',value).replace(r'\"','"').replace('\\\\','\\')
            chars.update(value);chars.update(value.upper())
    return {c for c in chars if not c.isspace()}
def validate(root=ROOT,pk3=None):
    root=Path(root);manifest=json.loads((root/'tools/font-glyphs.json').read_text())
    data=catalogs(root,pk3);required=required_characters(data);errors=[]
    archive=zipfile.ZipFile(pk3) if pk3 else None
    def read(rel):
        try:return archive.read(rel) if archive else (root/'tutnt'/rel).read_bytes()
        except (KeyError,FileNotFoundError):return None
    try:
        for legacy in ('DBIGFONT.fon2','UCRBIG.fon2','BIGFONT.fon2','SMALLFNT.fon2'):
            if read(legacy) is not None:errors.append(legacy+': obsolete font would override native glyphs')
        for font in FONTS:
            records=manifest['fonts'][font]['glyphs']
            for char in sorted(required):
                if f'{ord(char):04X}' not in records:errors.append(f'{font}: missing U+{ord(char):04X} ({char})')
            info=read(f'fonts/{font}/font.inf')
            if not info or re.search(rb'\baltfont\b',info,re.I):errors.append(font+': missing definition or forbidden fallback')
            if info and hashlib.sha256(info).hexdigest()!=manifest['fonts'][font]['definition_sha256']:
                errors.append(font+': font metrics changed; rebuild/review assets')
            for code,entry in records.items():
                content=read(f'fonts/{font}/{code}.png')
                if content is None or hashlib.sha256(content).hexdigest()!=entry['sha256']:
                    errors.append(font+'/'+code+': glyph missing or changed; rebuild/review assets');continue
                if chr(int(code,16)).isspace():continue
                pos=8;compressed=b''
                while pos<len(content):
                    length=struct.unpack_from('>I',content,pos)[0];kind=content[pos+4:pos+8]
                    if kind==b'IDAT':compressed+=content[pos+8:pos+8+length]
                    pos+=length+12
                raw=zlib.decompress(compressed);stride=entry['width']*4+1
                if not any(raw[y*stride+x*4+4] for y in range(entry['height']) for x in range(entry['width'])):
                    errors.append(font+'/'+code+': blank glyph')
    finally:
        if archive:archive.close()
    if errors:raise ValueError('\n'.join(errors))
    return {'fonts':{f:len(manifest['fonts'][f]['glyphs']) for f in FONTS},'required_characters':len(required),'fallbacks':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--pk3',type=Path);a=p.parse_args()
    try:print(json.dumps(validate(a.root,a.pk3),indent=2))
    except (ValueError,FileNotFoundError) as e:p.exit(1,str(e)+'\n')
