"""Lossless storage for generated OBJ meshes; actor identities stay independent."""
import hashlib
import re

_DECIMAL = re.compile(r"(?<![\w.])-?\d+\.\d+(?![\w.])")


def compact_obj(text):
    """Strip decimal padding only; preserve precision, signed zero and all indices."""
    return ''.join(
        _DECIMAL.sub(lambda m: m[0].rstrip('0').rstrip('.'), line)
        if line.startswith(('v ', 'vt ', 'vn ')) else line
        for line in text.splitlines(keepends=True)
    )


class ModelPool:
    """Choose the first deterministic generated name for each identical mesh."""
    def __init__(self, outputs, directory):
        self.outputs = outputs
        self.directory = directory.rstrip('/')
        self.meshes = {}

    def add(self, stem, text):
        text = compact_obj(text)
        digest = hashlib.sha256(text.encode()).digest()
        if digest in self.meshes:
            name = self.meshes[digest]
            if self.outputs[self.directory + '/' + name] != text:
                raise ValueError('Model digest collision')
            return name
        name = stem + '.obj'
        self.meshes[digest] = name
        self.outputs[self.directory + '/' + name] = text
        return name
