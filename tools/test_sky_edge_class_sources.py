"""Keep generated model classes intact while bounding UDB source rescans."""
import re
import unittest
from build_sky_edges import actor_sources

class SkyEdgeClassSourcesTests(unittest.TestCase):
    def test_complete_ordered_roundtrip_through_includes(self):
        actors = [f'class Edge{i} : Actor {{\n Default {{ RenderRadius {i + 1}; }}\n}}' for i in range(385)]
        outputs = actor_sources(actors)
        entry = outputs['tutnt/zscript/sky-edges-generated.zc']
        includes = re.findall(r'#include "([^"]+)"', entry)
        self.assertEqual(len(includes), 4)
        bodies = [outputs['tutnt/' + name].split('\n', 1)[1] for name in includes]
        self.assertEqual(''.join(bodies), '\n'.join(actors) + '\n')
        self.assertTrue(all(len(re.findall(r'^class ', body, re.M)) <= 128 for body in bodies))
        self.assertEqual(set(outputs), {'tutnt/' + name for name in includes} | {'tutnt/zscript/sky-edges-generated.zc'})
        self.assertNotIn('$GZDB_SKIP', ''.join(outputs.values()))

    def test_empty_generation_has_no_dangling_include(self):
        outputs = actor_sources([])
        self.assertEqual(len(outputs), 1)
        self.assertNotIn('#include', next(iter(outputs.values())))

    def test_invalid_chunk_size_is_rejected(self):
        with self.assertRaises(ValueError):
            actor_sources(['class Edge : Actor {}'], 0)

if __name__ == '__main__':
    unittest.main()
