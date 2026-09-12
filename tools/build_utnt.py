"""Compile all embedded ACS and create a fresh, deterministic UTNT PK3.

Python 3.11+; ACC 1.60 or compatible is required. Map SCRIPTS remain authoritative.
Usage: python tools/build_utnt.py --acc /path/to/acc.exe [--check-only]
"""
import contextlib, shutil
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

def input_files(root):
    """Runtime assets plus ACS sources; editor/backup/reference data never ships."""
    source = root/'tutnt'
    files = []
    for folder, dirs, names in os.walk(source):
        # Prune before traversal: local references may contain entire repositories.
        dirs[:] = [name for name in dirs if not name.startswith('.')
                   and name not in ('tools', '#PSD')]
        for name in names:
            p = pathlib.Path(folder)/name
            if (p.is_file() and not name.startswith('.')
                and p.suffix.lower() not in ('.dbs','.psd','.bat','.otf','.ttf','.rar','.zip')
                and '.backup' not in name and '.autosave' not in name):
                files.append(p)
    return sorted(files, key=lambda p:p.relative_to(source).as_posix())


class BuildLock:
    """OS-held lock: a crashed process releases it, so no stale-lock deletion race."""
    def __init__(self, output):
        self.path = pathlib.Path(str(pathlib.Path(output).resolve())+'.build.lock')
        self.file = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open('a+b')
        self.file.seek(0, 2)
        if self.file.tell() == 0:
            self.file.write(b'\0'); self.file.flush()
        self.file.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.file.close(); self.file = None
            raise RuntimeError(f'Another build owns {self.path.name}; existing package preserved.') from exc
        return self

    def __exit__(self, *args):
        if self.file:
            self.file.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file, fcntl.LOCK_UN)
            self.file.close()


def source_hashes(root):
    return {p.relative_to(root/'tutnt').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in input_files(root)}


def revision(root):
    git = shutil.which('git')
    if not git and os.name == 'nt':
        candidate = pathlib.Path(os.environ.get('ProgramFiles', r'C:\Program Files'))/'Git/cmd/git.exe'
        if candidate.is_file(): git = str(candidate)
    if not git: return {'commit': 'unavailable', 'local_changes': True}
    base = [git, '-c', 'safe.directory='+root.as_posix(), '-C', str(root)]
    p = subprocess.run(base+['rev-parse','HEAD'],capture_output=True)
    if p.returncode: return {'commit':'unavailable','local_changes':True}
    changes = subprocess.run(base+['status','--porcelain','--','tutnt'],capture_output=True,check=True)
    return {'commit':p.stdout.decode().strip(), 'local_changes':bool(changes.stdout.strip())}


@contextlib.contextmanager
def snapshot(root):
    root = pathlib.Path(root).resolve()
    provenance = revision(root)
    before = source_hashes(root)
    with tempfile.TemporaryDirectory(prefix='utnt-snapshot-') as directory:
        target = pathlib.Path(directory)
        for name, digest in before.items():
            data = (root/'tutnt'/name).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise RuntimeError('Sources changed while taking snapshot; build again.')
            dest = target/'tutnt'/name
            dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        if source_hashes(root) != before or revision(root) != provenance:
            raise RuntimeError('Sources or Git revision changed while taking snapshot; build again.')
        fingerprint = hashlib.sha256(json.dumps(before,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        yield target, before, dict(provenance, source_sha256=fingerprint, build_id=fingerprint[:12])


def publish_snapshot(source, original, output, hashes, metadata, engine=None, iwad=None):
    files = [p for p in input_files(source) if 'source' not in p.relative_to(source/'tutnt').parts]
    payload = {p.relative_to(source/'tutnt').as_posix():p.read_bytes() for p in files}
    from build_definition_tables import package_textures
    payload = package_textures(payload)
    if any(name in payload for name in ('UTNTBLD','LANGUAGE.zzbuild')):
        raise RuntimeError('UTNTBLD and LANGUAGE.zzbuild are reserved build outputs.')
    metadata = dict(metadata, files={name:hashlib.sha256(data).hexdigest() for name,data in payload.items()})
    metadata['build_id'] = hashlib.sha256(json.dumps(metadata,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:12]
    payload['UTNTBLD'] = (json.dumps(metadata,sort_keys=True,indent=2)+'\n').encode()
    label = f"Build {metadata['build_id']} / {metadata['commit'][:12]}" + (' +local' if metadata['local_changes'] else '')
    payload['LANGUAGE.zzbuild'] = ''.join(
        '['+lang+']\nUTNT_BUILD_INFO = \"'+label+'\";\n'
        for lang in ('enu default','deu de','esp es','fra fr')).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=output.name+'.',suffix='.tmp.pk3',dir=output.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temp,'w') as archive:
            for name, data in sorted(payload.items()):
                info = zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info,data,compresslevel=6)
        with zipfile.ZipFile(temp) as archive:
            if archive.testzip(): raise RuntimeError('PK3 integrity check failed')
            if not all(x in archive.namelist() for x in ('zscript.zc','MAPINFO.txt','acs/tutnt.o')):
                raise RuntimeError('Required runtime resources missing from PK3')
        validation = None
        if engine:
            from check_engine import run_case
            validation_root = original/'tutnt/.codex/validation/build-engine'
            validation_root.mkdir(parents=True,exist_ok=True)
            validation = run_case(engine,iwad,root=validation_root,mod=pathlib.Path(temp),
                                  label='build-'+metadata['build_id']+'-engine',quiet=True)
            if not validation['ok']:
                raise RuntimeError('Engine rejected snapshot; previous PK3 preserved. See '+validation['log'])
        # Compilation occurs only in the snapshot. Refuse publication if live
        # sources changed while ACC, compression or the engine check was running.
        if source_hashes(original) != hashes or revision(original) != {
                key:metadata[key] for key in ('commit','local_changes')}:
            raise RuntimeError('Project changed during build; previous PK3 preserved. Build the new snapshot again.')
        try: os.replace(temp,output)
        except PermissionError as exc:
            raise RuntimeError(f'{output.name} is in use; close the game/editor and build again. Previous package preserved.') from exc
    finally:
        if os.path.exists(temp): os.unlink(temp)
    with output.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    result = {'path':str(output),'files':len(payload),'bytes':output.stat().st_size,
              'sha256':digest,'engine_checked':bool(engine),'build_id':metadata['build_id'],
              'commit':metadata['commit'],'local_changes':metadata['local_changes']}
    (original/'logs').mkdir(exist_ok=True)
    atomic_write(original/'logs'/('build-'+metadata['build_id']+'.json'),
                 (json.dumps(result,indent=2)+'\n').encode())
    return result


def package(root, output, engine=None, iwad=None):
    """Compatibility API: packages a verified immutable snapshot of supplied bytecode."""
    root, output = pathlib.Path(root).resolve(), pathlib.Path(output).resolve()
    with BuildLock(output), snapshot(root) as (source, hashes, metadata):
        return publish_snapshot(source,root,output,hashes,metadata,engine,iwad)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=pathlib.Path,default=ROOT)
    p.add_argument('--acc',type=pathlib.Path,default=os.environ.get('UTNT_ACC',r'F:\DoomDev\Tools\UltimateDoombuilder\Compilers\ZDoom\acc.exe'))
    p.add_argument('--check-only',action='store_true')
    p.add_argument('--output',type=pathlib.Path)
    p.add_argument('--engine',type=pathlib.Path,default=os.environ.get('UTNT_ENGINE',ROOT/'engine/uzdoom.exe'))
    p.add_argument('--iwad',type=pathlib.Path,default=os.environ.get('UTNT_IWAD',r'F:\DoomDev\DOOM2.WAD'))
    p.add_argument('--skip-engine-check',action='store_true')
    a=p.parse_args(); root=a.root.resolve(); compiler=a.acc.resolve()
    if not compiler.is_file(): p.error('ACC not found; set --acc or UTNT_ACC')
    from build_definition_tables import generate as generate_definition_tables
    generate_definition_tables(root, check=a.check_only)
    from build_lava_lips import generate as generate_lava_lips
    generate_lava_lips(root,check=a.check_only)
    from build_environment_fx import check as check_environment_fx
    check_environment_fx(root)
    from build_local_heat import generate as generate_local_heat
    generate_local_heat(root, check=a.check_only)
    from build_organic_materials import generate as generate_organic_materials
    generate_organic_materials(root, check=a.check_only, iwad=a.iwad)
    from build_crt_materials import generate as generate_crt_materials
    generate_crt_materials(root, check=a.check_only)
    output=(a.output or root/'tutnt.pk3').resolve()
    with BuildLock(output), snapshot(root) as (source, hashes, metadata):
        from check_localization import validate as validate_localization
        # Validate the immutable source snapshot, using the reviewed source manifest.
        (source/'tools').mkdir(exist_ok=True)
        shutil.copyfile(root/'tools/localization-review.json', source/'tools/localization-review.json')
        localization = validate_localization(source)
        from check_font_coverage import validate as validate_fonts
        shutil.copyfile(root/'tools/font-glyphs.json', source/'tools/font-glyphs.json')
        localization['fonts'] = validate_fonts(source)
        result={'localization':localization, 'acs':compile_sources(source,compiler,a.check_only)}
        if not a.check_only:
            if not a.skip_engine_check and (not a.engine.is_file() or not a.iwad.is_file()):
                p.error('Set UTNT_ENGINE / UTNT_IWAD or explicitly use --skip-engine-check')
            result['pk3']=publish_snapshot(source,root,output,hashes,metadata,
                None if a.skip_engine_check else a.engine.resolve(),a.iwad.resolve())
    print(json.dumps(result,indent=2))


if __name__ == '__main__': main()
