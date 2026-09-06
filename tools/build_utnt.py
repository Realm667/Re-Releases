"""Compile all embedded ACS and create a fresh, deterministic UTNT PK3.

Python 3.11+; ACC 1.60 or compatible is required. Map SCRIPTS remain authoritative.
Usage: python tools/build_utnt.py --acc /path/to/acc.exe [--check-only]
"""
import argparse, hashlib, json, os, pathlib, struct, subprocess, tempfile, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

def read_wad(path):
    data = path.read_bytes()
    magic, count, directory = struct.unpack_from('<4sII', data)
    if magic not in (b'PWAD', b'IWAD') or directory+count*16 > len(data):
        raise ValueError(f'Invalid WAD: {path}')
    entries = []
    for i in range(count):
        offset, size, name = struct.unpack_from('<II8s', data, directory+i*16)
        if offset+size > len(data): raise ValueError(f'Invalid lump in {path}')
        entries.append((name, data[offset:offset+size]))
    return magic, entries

def write_wad(magic, entries):
    body, directory = bytearray(), bytearray()
    for name, data in entries:
        directory += struct.pack('<II8s', 12+len(body), len(data), name)
        body += data
    return struct.pack('<4sII', magic, len(entries), 12+len(body))+body+directory

def atomic_write(path, data):
    path = pathlib.Path(path)
    fd, tmp = tempfile.mkstemp(prefix=path.name+'.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f: f.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def compile_sources(root, compiler, check_only=False):
    pending, results = [], []
    with tempfile.TemporaryDirectory(prefix='utnt-acs-') as tmp:
        tmp = pathlib.Path(tmp)
        sources = [(root/'tutnt/source/tutnt.acs', None)]
        sources += [(p, read_wad(p)) for p in sorted((root/'tutnt/maps').glob('*.wad'))]
        for path, wad in sources:
            raw = path.read_bytes() if wad is None else next(data for name,data in wad[1] if name.rstrip(b'\0') == b'SCRIPTS')
            source = tmp/(path.stem+'.acs')
            target = tmp/(path.stem+'.o')
            source.write_bytes(raw)
            p = subprocess.run([str(compiler), '-i', str(compiler.parent), str(source), str(target)], capture_output=True, timeout=60)
            log = (p.stdout+p.stderr).decode(errors='replace')
            if p.returncode or not target.exists(): raise RuntimeError(f'{path}:\n{log}')
            compiled = target.read_bytes()
            if wad is None:
                dest = root/'tutnt/acs/tutnt.o'
                previous, replacement = dest.read_bytes(), compiled
            else:
                dest = path
                previous = next(data for name,data in wad[1] if name.rstrip(b'\0') == b'BEHAVIOR')
                replacement = write_wad(wad[0], [(name,compiled if name.rstrip(b'\0') == b'BEHAVIOR' else data) for name,data in wad[1]])
            changed = previous != compiled
            results.append({'source':str(path.relative_to(root)), 'compiled_bytes':len(compiled), 'bytecode_changed':changed, 'sha256':hashlib.sha256(compiled).hexdigest()})
            if changed: pending.append((dest,replacement))
        # Never write any module if a later compile fails.
        if check_only and pending: raise RuntimeError('Stale ACS bytecode: '+', '.join(str(p) for p,_ in pending))
        if not check_only:
            for path,data in pending: atomic_write(path,data)
    return results

def package(root, output, engine=None, iwad=None):
    files = sorted((p for p in (root/'tutnt').rglob('*') if p.is_file()
                   and not any(x.startswith('.') or x in ('tools','#PSD','source') for x in p.relative_to(root/'tutnt').parts)
                   and p.suffix.lower() not in ('.dbs','.psd','.bat','.otf','.ttf','.rar','.zip')
                   and '.backup' not in p.name and '.autosave' not in p.name), key=lambda p:p.relative_to(root/'tutnt').as_posix())
    output.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp = tempfile.mkstemp(prefix=output.name+'.',suffix='.tmp.pk3',dir=output.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for path in files:
                info=zipfile.ZipInfo(path.relative_to(root/'tutnt').as_posix(),date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())
        with zipfile.ZipFile(tmp) as archive:
            if archive.testzip(): raise RuntimeError('PK3 integrity check failed')
            assert len(archive.namelist()) == len(set(archive.namelist())) == len(files)
            assert all(x in archive.namelist() for x in ('zscript.zc','MAPINFO.txt','acs/tutnt.o'))
        if engine:
            from check_engine import run_case
            validation=run_case(engine,iwad,root=root,mod=pathlib.Path(tmp),label='build-engine-check',quiet=True)
            if not validation['ok']: raise RuntimeError('Engine rejected package; previous PK3 preserved. See '+validation['log'])
        os.replace(tmp,output)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    with output.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    return {'path':str(output),'files':len(files),'bytes':output.stat().st_size,'sha256':digest,'engine_checked':bool(engine)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=pathlib.Path,default=ROOT)
    p.add_argument('--acc',type=pathlib.Path,default=os.environ.get('UTNT_ACC',r'F:\DoomDev\Tools\UltimateDoombuilder\Compilers\ZDoom\acc.exe'))
    p.add_argument('--check-only',action='store_true')
    p.add_argument('--output',type=pathlib.Path)
    p.add_argument('--engine',type=pathlib.Path,default=os.environ.get('UTNT_ENGINE',ROOT/'engine/uzdoom.exe'))
    p.add_argument('--iwad',type=pathlib.Path,default=os.environ.get('UTNT_IWAD',r'F:\DoomDev\DOOM2.WAD'))
    p.add_argument('--skip-engine-check',action='store_true',help='Only for environments without a runnable UZDoom; does not certify engine compatibility.')
    a=p.parse_args(); root=a.root.resolve(); compiler=a.acc.resolve()
    if not compiler.is_file(): p.error('ACC not found; set --acc or UTNT_ACC')
    result={'acs':compile_sources(root,compiler,a.check_only)}
    if not a.check_only:
        if not a.skip_engine_check and (not a.engine.is_file() or not a.iwad.is_file()): p.error('Set UTNT_ENGINE / UTNT_IWAD or explicitly use --skip-engine-check')
        result['pk3']=package(root,(a.output or root/'tutnt.pk3').resolve(),None if a.skip_engine_check else a.engine.resolve(),a.iwad.resolve())
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()
