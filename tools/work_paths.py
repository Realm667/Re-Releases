"""Resolve agent outputs without depending on the retired local junctions."""
import os
from pathlib import Path

LOCAL_REPOSITORY = Path("F:/DoomDev/Projects/realm667.git")
LOCAL_CODEX_ROOT = Path("D:/Codex/ReReleases/UTNT Reforged/.codex")

def codex_root(repository=None):
    """Use D: for this local checkout; keep isolated/portable fixtures local."""
    repository = Path(repository) if repository is not None else Path(__file__).resolve().parent.parent
    configured = os.environ.get("UTNT_CODEX_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    if os.name == "nt" and repository.resolve() == LOCAL_REPOSITORY.resolve():
        return LOCAL_CODEX_ROOT
    return repository / "tutnt" / ".codex"


def runtime_root(root):
    """Redirect the source checkout; preserve an explicit isolated output root."""
    root = Path(root).resolve()
    repository = Path(__file__).resolve().parent.parent
    return codex_root(root) if root == repository else root
