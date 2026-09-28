"""Image-space sky-cube regression checks (Pillow and NumPy required)."""
from pathlib import Path
import unittest
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / 'zdcmp1/PATCHES/skybox/cube'

def pixels(name):
    return np.asarray(Image.open(ROOT / (name + '.png')).convert('RGB'), dtype=float)

class SkyCubeImages(unittest.TestCase):
    def test_wall_corners_and_halves(self):
        for name in ('outdoor', 'hell'):
            for a, b in zip('nwse', 'wsen'):
                face = pixels(f'{name}-{a}')
                self.assertTrue(np.array_equal(face[:, -1], pixels(f'{name}-{b}')[:, 0]))
                halves = np.concatenate([pixels(f'{name}-{a}{i}') for i in (0, 1)], axis=1)
                self.assertTrue(np.array_equal(face, halves))

    def test_cap_at_actual_wall_intersections(self):
        # Special 90 covers 320 units; walls are four units inside that border.
        coords = np.linspace(4/320*1023, 316/320*1023, 1024)
        def sample(im, x, y):
            x, y = np.broadcast_arrays(x, y)
            a, b = x.astype(int), y.astype(int)
            u, v = (x-a)[..., None], (y-b)[..., None]
            return ((im[b,a]*(1-u)+im[b,a+1]*u)*(1-v)
                    +(im[b+1,a]*(1-u)+im[b+1,a+1]*u)*v)
        for name in ('outdoor', 'hell'):
            cap = pixels(f'{name}-top')
            lo, hi = coords[0], coords[-1]
            edges = dict(n=sample(cap,coords[::-1],hi), w=sample(cap,lo,coords[::-1]),
                         s=sample(cap,coords,lo), e=sample(cap,hi,coords))
            for face, edge in edges.items():
                error = abs(edge-pixels(f'{name}-{face}')[0])
                self.assertLess(error.mean(), 0.6, (name, face, error.mean()))
                self.assertLess(error.max(), 5, (name, face, error.max()))

    def test_cloud_frames_keep_wall_intersections_static(self):
        for name in ('outdoor', 'hell'):
            base = pixels(f'{name}-top')
            for frame in range(8):
                image = pixels(f'{name}-top-{frame:02d}')
                for edge in (np.s_[:30,:], np.s_[-30:,:], np.s_[:,:30], np.s_[:,-30:]):
                    self.assertTrue(np.array_equal(base[edge], image[edge]))
            self.assertFalse(np.array_equal(pixels(f'{name}-top-00'), pixels(f'{name}-top-04')))

if __name__ == '__main__':
    unittest.main()
