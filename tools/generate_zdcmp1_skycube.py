"""Project the editable MAP01 panoramas into matching cube faces.

The same spherical sample function is evaluated on every face.  Shared cube
edges therefore receive identical source rays; the tiny source wrap is
feathered before projection and both poles converge to a single colour.
"""
from pathlib import Path
import argparse
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "zdcmp1/source/art/skybox"
DEST = ROOT / "zdcmp1/PATCHES/skybox/cube"
SIZE = 1024


def smoothstep(a, b, x):
    t = np.clip((x-a)/(b-a), 0.0, 1.0)
    return t*t*(3.0-2.0*t)


def periodic_source(path):
    image = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    h, w, _ = image.shape
    band = max(24, w//72)
    edge = (image[:, 0, :] + image[:, -1, :]) * 0.5
    for k in range(band):
        t = smoothstep(0.0, float(band-1), float(k))
        image[:, k, :] = edge*(1-t) + image[:, k, :]*t
        image[:, w-1-k, :] = edge*(1-t) + image[:, w-1-k, :]*t
    # Set both boundary columns exactly equal after the symmetric feather.
    image[:, 0, :] = edge
    image[:, -1, :] = edge
    return image


def sample(image, x, y, z):
    h, w, _ = image.shape
    lon = np.arctan2(y, x)
    lat = np.degrees(np.arctan2(z, np.hypot(x, y)))
    px = ((lon / (2*np.pi) + 0.5) * (w-1)) % (w-1)
    # The generated landscape's horizon is at 75% of the source height.
    py = np.where(lat >= 0, .75*(1-lat/90), .75 + .25*(-lat/90)) * (h-1)
    py = np.clip(py, 0, h-1)
    x0 = np.floor(px).astype(np.int32); y0 = np.floor(py).astype(np.int32)
    x1 = (x0+1) % (w-1); y1 = np.minimum(y0+1, h-1)
    tx = (px-x0)[..., None]; ty = (py-y0)[..., None]
    out = ((image[y0,x0]*(1-tx)+image[y0,x1]*tx)*(1-ty)
          +(image[y1,x0]*(1-tx)+image[y1,x1]*tx)*ty)
    # No longitude may survive at the zenith or nadir.
    pole = np.mean(image, axis=1)
    avg = pole[y0]*(1-ty)+pole[y1]*ty
    fade = smoothstep(68, 90, np.abs(lat))[..., None]
    return out*(1-fade)+avg*fade


def cube_vectors(face):
    u = np.linspace(-1, 1, SIZE, dtype=np.float32)
    v = np.linspace(-1, 1, SIZE, dtype=np.float32)
    U, V = np.meshgrid(u, v)
    if face == 'n': return -U, -np.ones_like(U), -V
    if face == 'w': return -np.ones_like(U), U, -V
    if face == 's': return U, np.ones_like(U), -V
    if face == 'e': return np.ones_like(U), -U, -V
    if face == 'top': return U, V, np.ones_like(U)
    if face == 'bottom': return U, V, -np.ones_like(U)
    raise ValueError(face)


def cloud_layer(source, name):
    h,w,_ = source.shape
    crop = source[int(h*.14):int(h*.65)]
    layer = Image.fromarray(np.uint8(np.clip(crop,0,255))).resize((512,512),Image.Resampling.LANCZOS)
    a = np.asarray(layer, dtype=np.float32)
    # Feather both axes to a tileable auxiliary cloud sample.
    for axis in (0,1):
        b = np.swapaxes(a,0,axis)
        edge = (b[0]+b[-1])*.5
        for k in range(64):
            t=smoothstep(0,63,k)
            b[k] = b[k]*t+edge*(1-t)
            b[-1-k] = b[-1-k]*t+edge*(1-t)
        a=np.swapaxes(b,0,axis)
    luminance = a.mean(axis=2)
    low, high = np.percentile(luminance, (5, 95))
    mask = np.clip((luminance-low)/max(high-low, 1.0), 0.0, 1.0)
    Image.fromarray(np.uint8(np.rint(mask*255))).save(DEST / f'{name}-cloud-layer.png')
    return mask


def render(name):
    source = periodic_source(SOURCE / f'{name}-source.png')
    faces = {face: sample(source, *cube_vectors(face))
             for face in ('n','w','s','e','top','bottom')}
    # A shared calm high-altitude colour closes the cap even when the engine's
    # wall/flat UV precision differs by a texel. The landscape below is intact.
    cap = np.mean(np.concatenate([faces[f][0] for f in 'nwse']), axis=0)
    position = np.linspace(0.0, 1.0, SIZE, dtype=np.float32)
    U, V = np.meshgrid(position, position)
    distance = np.minimum(np.minimum(U, 1.0-U), np.minimum(V, 1.0-V))
    top_weight = smoothstep(0.0, 0.30, distance)[..., None]
    # The red source has much stronger high-cloud contrast. Keep its zenith
    # restrained so the flat/wall transition stays invisible in live views.
    strength = 0.10 if name == 'hell' else 1.0
    faces['top'] = cap * (1.0-top_weight*strength) + faces['top'] * (top_weight*strength)
    wall_weight = smoothstep(0.0, 0.32, V)[..., None]
    for face in 'nwse':
        faces[face] = cap * (1.0-wall_weight) + faces[face] * wall_weight
    for face, rgb in faces.items():
        face_image = Image.fromarray(np.uint8(np.clip(np.rint(rgb),0,255)))
        face_image.save(DEST / f'{name}-{face}.png', optimize=True)
        if face in ('n', 'w', 's', 'e'):
            for half in (0, 1):
                face_image.crop((half*512, 0, (half+1)*512, SIZE)).save(DEST / f'{name}-{face}{half}.png', optimize=True)
    clouds = cloud_layer(source, name)
    for index, shift in enumerate((0, 4, 8, 12, 16, 12, 8, 4)):
        moved = np.roll(clouds, shift, axis=1)
        moved = np.asarray(Image.fromarray(np.uint8(np.rint(moved*255)))
                           .resize((SIZE, SIZE), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0
        motion = 1.0 + (moved[..., None]-0.5) * (0.05 if name == 'hell' else 0.12) * top_weight
        frame = np.uint8(np.clip(np.rint(faces['top'] * motion), 0, 255))
        Image.fromarray(frame).save(DEST / f'{name}-top-{index:02d}.png', optimize=True)


def main():
    global DEST
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=DEST)
    args=ap.parse_args()
    DEST=args.output; DEST.mkdir(parents=True,exist_ok=True)
    for name in ('outdoor','hell'): render(name)

if __name__ == '__main__': main()
