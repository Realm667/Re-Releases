"""Reproduce the procedural UTNT weather sprites and two-second sound beds.
Requires Pillow and NumPy. Does not modify maps or gameplay sources.
"""
from pathlib import Path
import math, wave
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
ROOT=Path(__file__).resolve().parent.parent

def main():
    assets=ROOT/'tutnt/graphics/utnt-weather'; assets.mkdir(parents=True,exist_ok=True)
    for kind in range(3):
        im=Image.new('RGBA',(16,16)); p=im.load()
        for y in range(16):
            for x in range(16):
                dx=x-7.5; dy=y-7.5; angle=math.atan2(dy,dx)
                radius=5.3+.65*math.sin(angle*3+kind*2)+.3*math.cos(angle*5-kind)
                a=max(0,min(1,(radius-math.hypot(dx,dy))/1.2))
                p[x,y]=(224,232,238,int(a*235))
        im.save(assets/f'snow{kind}.png')
    im=Image.new('RGBA',(8,64)); p=im.load()
    for y in range(64):
        for x in range(8):
            a=math.exp(-((x-3.5)/1.15)**2)*math.sin(math.pi*(y+.5)/64)**.7
            p[x,y]=(194,207,218,int(255*a))
    im.save(assets/'rain.png')
    im=Image.new('RGBA',(48,24)); d=ImageDraw.Draw(im)
    d.ellipse((3,5,44,19),outline=(191,213,225,200),width=2)
    im=im.filter(ImageFilter.GaussianBlur(.6)); im.save(assets/'ripple.png')
    audio=ROOT/'tutnt/sounds/utnt-weather'; audio.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(667); sr=22050; n=sr*2; t=np.arange(n)/sr
    # Two-second overlapping sine envelopes: one voice launched each second.
    env=np.sin(np.pi*np.arange(n)/n)**2
    noise=rng.normal(0,1,n)
    low=np.convolve(noise,np.ones(96)/96,mode='same')
    mid=np.convolve(noise,np.ones(8)/8,mode='same')
    signals={'rain':mid*.7+noise*.12,'shelter':low*2.3,'wind':low*(1.8+.4*np.sin(t*4))}
    drip=np.sin(2*np.pi*(1800*t-650*t*t))*np.exp(-t*38); signals['drip']=drip*.22
    for name,signal in signals.items():
        signal=signal*(env if name!='drip' else 1)
        data=np.clip(signal*20000,-32767,32767).astype('<i2')
        with wave.open(str(audio/(name+'.wav')),'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr); f.writeframes(data.tobytes())
    (ROOT/'tutnt/sndinfo.weather').write_text('''// Locally mixed, overlapping weather beds; no per-marker sound loops.
UTNTWeather/Rain sounds/utnt-weather/rain.wav
UTNTWeather/Shelter sounds/utnt-weather/shelter.wav
UTNTWeather/Wind sounds/utnt-weather/wind.wav
UTNTWeather/Drip sounds/utnt-weather/drip.wav
$limit UTNTWeather/Rain 2
$limit UTNTWeather/Shelter 2
$limit UTNTWeather/Wind 2
$limit UTNTWeather/Drip 2
''')

if __name__=="__main__": main()
