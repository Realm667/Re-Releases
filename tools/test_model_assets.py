"""Check lossless numeric storage and shared geometry with independent actors."""
import struct
import unittest
from model_assets import compact_obj, ModelPool


class Models(unittest.TestCase):
    def test_precision_and_signed_zero(self):
        raw='# precision must not change\ns 1\nv -0.000000 0.000000 123.000000\nvt 0.00000001 0.12345678\nvn -1.000000 0.000001 -123.456780\nf 1/1/1 2/2/2 3/3/3\n'
        result=compact_obj(raw)
        self.assertLess(len(result),len(raw))
        for before,after in zip(raw.splitlines(),result.splitlines()):
            if before.startswith(('v ','vt ','vn ')):
                self.assertEqual([struct.pack('>d',float(v)) for v in before.split()[1:]],
                                 [struct.pack('>d',float(v)) for v in after.split()[1:]])
            else: self.assertEqual(before,after)
        self.assertEqual(compact_obj(result),result)

    def test_pool_shares_exact_meshes_only(self):
        outputs={}; pool=ModelPool(outputs,'tutnt/models/example')
        a=pool.add('a','v 1.000000 2.000000 -0.000000\n')
        b=pool.add('b','v 1.000000 2.000000 -0.000000\n')
        c=pool.add('c','v 1.000001 2.000000 -0.000000\n')
        d=pool.add('d','v 1.000000 2.000000 0.000000\n')
        self.assertEqual(a,b)
        self.assertEqual(len({a,c,d}),3)
        self.assertEqual(len(outputs),3)
        self.assertNotIn('tutnt/models/example/b.obj',outputs)


if __name__=='__main__': unittest.main()
