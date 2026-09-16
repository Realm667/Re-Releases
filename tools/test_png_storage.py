"""Regression tests for exact PNG semantics and generator preservation."""
import io
from pathlib import Path
import tempfile
import unittest
from PIL import Image, PngImagePlugin
from png_storage import chunks, encode, equivalent, normalized, preserve_png, restore_chunks


def png(mode='RGBA', color=(10,20,30,255), level=0, meta=True):
    im=Image.new(mode,(12,10),color);out=io.BytesIO();info=PngImagePlugin.PngInfo()
    if meta:info.add(b'grAb',b'\0\0\0\x06\0\0\0\x09')
    im.save(out,format='PNG',pnginfo=info,compress_level=level)
    return out.getvalue()

class StorageTests(unittest.TestCase):
    def test_recompression(self):
        self.assertTrue(equivalent(png(),png(level=9)))
    def test_opaque_alpha(self):
        a=png();b=restore_chunks(a,png('RGB',(10,20,30),9))
        self.assertTrue(equivalent(a,b));self.assertLess(len(b),len(a))
    def test_partial_alpha_cannot_be_removed(self):
        self.assertFalse(equivalent(png(color=(10,20,30,127)),png('RGB',(10,20,30))))
    def test_hidden_rgb_must_match(self):
        self.assertFalse(equivalent(png(color=(10,20,30,0)),png(color=(0,0,0,0))))
    def test_offset_required(self):
        self.assertFalse(equivalent(png(),png(meta=False)))
    def test_crc_repair_keeps_payload(self):
        a=bytearray(png());pos=a.index(b'grAb')+12;a[pos]^=1
        self.assertTrue(any(not valid for k,v,valid in chunks(a)))
        self.assertTrue(equivalent(bytes(a),normalized(bytes(a))))
    def test_palette_changes_rejected(self):
        a=Image.new('P',(2,1));a.putpalette([0,0,0,255,0,0]+[0]*762)
        stream=io.BytesIO();a.save(stream,format='PNG');before=stream.getvalue()
        parts=[(k,(b'\x01'+v[1:]) if k==b'PLTE' else v) for k,v,_ in chunks(before)]
        self.assertFalse(equivalent(before,encode(parts)))
    def test_generator_retains_only_equivalent_smaller_file(self):
        # The system temp directory is cleaned by TemporaryDirectory.
        with tempfile.TemporaryDirectory(prefix='utnt-png-unit-') as d:
            path=Path(d)/'a.png';small=png(level=9);path.write_bytes(small)
            self.assertEqual(preserve_png(path,png()),small)
            changed=png(color=(20,20,30,255))
            self.assertEqual(preserve_png(path,changed),changed)
    def test_restore_private_chunks(self):
        a=png();b=restore_chunks(a,png(level=9,meta=False))
        self.assertTrue(equivalent(a,b))
    def test_animation_not_silently_flattened(self):
        a=encode([(k,v) for k,v,_ in chunks(png())][:-1]+[(b'acTL',b'\0'*8),(b'IEND',b'')])
        with self.assertRaises(ValueError):equivalent(a,a)

if __name__=='__main__':unittest.main()
