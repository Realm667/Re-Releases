"""Workspace and tool defaults for ZDCMP1, independent of other mod workspaces."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
LOCAL_REPOSITORY = Path('F:/DoomDev/Projects/realm667.git')
LOCAL_WORKSPACE = Path('D:/Codex/ReReleases/ZDCMP1')


def workspace():
    configured = os.environ.get('ZDCMP1_WORKSPACE')
    if configured:
        return Path(configured).expanduser().resolve()
    if os.name == 'nt' and ROOT.resolve() == LOCAL_REPOSITORY.resolve():
        return LOCAL_WORKSPACE
    raise ValueError('Set ZDCMP1_WORKSPACE to the local ZDCMP1 working directory')


def data_root():
    return workspace() / '.codex'


def temporary_root():
    path = data_root() / 'cache/temp'
    path.mkdir(parents=True, exist_ok=True)
    return path


def tool_default(name):
    configured = os.environ.get('ZDCMP1_' + name.upper())
    if configured:
        return str(Path(configured).expanduser().resolve())
    relative = {'engine': 'uzdoom/uzdoom.exe' if os.name == 'nt' else 'uzdoom/uzdoom',
                'iwad': 'iwads/DOOM2.WAD', 'acc': 'acc/acc.exe' if os.name == 'nt' else 'acc/acc'}
    candidate = workspace() / 'dependencies' / relative[name]
    if candidate.is_file():
        return str(candidate)
    # CI may retain the existing shared variable names, but inputs must belong
    # to this workspace or checkout. An unrelated mod's environment is ignored.
    inherited = os.environ.get('UTNT_' + name.upper())
    if inherited:
        path = Path(inherited).expanduser().resolve()
        if path.is_relative_to(workspace()) or path.is_relative_to(ROOT):
            return str(path)
    return None


def configure_environment():
    """Configure only the current ZDCMP1 command and its children."""
    os.environ['ZDCMP1_WORKSPACE'] = str(workspace())
    temporary = temporary_root()
    for name in ('TEMP', 'TMP', 'TMPDIR'):
        os.environ[name] = str(temporary)
    tempfile.tempdir = str(temporary)
    for name in ('logs', 'builds', 'validation'):
        (data_root() / name).mkdir(parents=True, exist_ok=True)
    for name in ('engine', 'iwad'):
        value = tool_default(name)
        if value:
            os.environ['UTNT_' + name.upper()] = value
        else:
            os.environ.pop('UTNT_' + name.upper(), None)
    return data_root()


def is_zdcmp1_mod(mod):
    if mod is None:
        return False
    path = Path(mod)
    return path.name.lower() == 'zdcmp1' or (path.suffix.lower() == '.pk3' and path.stem.lower().startswith('zdcmp1'))


def run_case(*args, **kwargs):
    from check_engine import run_case as shared_run_case
    kwargs.setdefault('root', data_root())
    return shared_run_case(*args, **kwargs)


def native_options():
    if os.name != 'nt':
        return {}
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    return {'startupinfo': startup, 'creationflags': subprocess.CREATE_NO_WINDOW}
