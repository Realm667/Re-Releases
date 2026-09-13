"""Native map metadata preservation and lossless model packaging regressions."""
import unittest
from package_runtime_assets import prepare_precache

class PrecacheTests(unittest.TestCase):
    def test_map_lists_preserve_native_fields_and_do_not_leak(self):
        original=b'map TNT01 "First" { next="TNT02"\nPrecacheClasses="Existing"\n}\nmap TNT02 "Second" { gravity=0.5 }\nmap TNT03 "Third" { }'
        payload={"MAPINFO.txt":original,"skyedges/tnt01.txt":b"UTNTEdgeOne|x|y\nUTNTEdgeOne|z\n", "lavalips/tnt02.txt":b"UTNTLipTwo|0\n", "models/a.obj":b"v 0 1 2\n"}
        result=prepare_precache(payload)
        self.assertEqual(payload["MAPINFO.txt"],original)
        first,second,third=result["MAPINFO.txt"].decode().split("map ")[1:]
        self.assertIn('next="TNT02"',first)
        self.assertIn('PrecacheClasses="Existing"',first)
        self.assertEqual(first.count('"UTNTEdgeOne"'),1)
        self.assertNotIn('UTNTLipTwo',first)
        self.assertIn('gravity=0.5',second)
        self.assertIn('UTNTLipTwo',second)
        self.assertNotIn('UTNTEdgeOne',second)
        self.assertNotIn('PrecacheClasses',third)
        self.assertEqual(result['models/a.obj'],payload['models/a.obj'])

if __name__=='__main__': unittest.main()
