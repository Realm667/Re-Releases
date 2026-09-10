"""Build a saved-clock seven-second implosion from Klerrp's CC0 Near/Far sounds.

Source provenance and public HQ preview conversion: tools/audio/utnt-source/.
The build itself needs only Python and NumPy; no network or audio codecs.
"""
from pathlib import Path
import wave
import numpy as np

RATE=44100
COLLAPSE=158/35

def read_source(path):
 with wave.open(str(path),'rb') as f:
  assert f.getsampwidth()==2
  rate=f.getframerate();channels=f.getnchannels()
  samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,channels).astype(float)/32768
 return samples.mean(axis=1),rate

def build(root=None):
 root=Path(root) if root else Path(__file__).resolve().parent.parent
 out=root/'tutnt/sounds/utnt-source/finale.wav';out.parent.mkdir(parents=True,exist_ok=True)
 t=np.arange(RATE*7)/RATE
 signals=[]
 for label in ('near','far'):
  x,sr=read_source(root/f'tools/audio/utnt-source/klerrp-implosion-{label}.wav')
  def at(seconds):return np.interp(seconds*sr,np.arange(len(x)),x,left=0,right=0)
  # Reverse the actual chosen material: the rising suction belongs to the
  # same sound as the impact, with a 100 ms quiet pocket at the point of collapse.
  pre=COLLAPSE-.100
  buildup=at(pre-t)*np.clip(t/1.4,0,1)**1.7*np.clip((pre-t)/.025,0,1)
  buildup*=0.21 if label=='near' else .29
  age=np.maximum(0,t-COLLAPSE)
  body=at(age)*(t>=COLLAPSE)*np.clip(age/.004,0,1)
  body*=np.exp(-age*(1.1 if label=='near' else .42))*(.85 if label=='near' else 1.0)
  signals.append(buildup+body)
 signal=signals[0]+signals[1]
 # Small delayed reflections retain a chamber-sized tail without a repeated bang.
 for delay,gain in ((.11,.14),(.29,.09),(.51,.05)):
  shift=int(delay*RATE);echo=np.zeros_like(t)
  dry=(signals[0]+signals[1])*(t>=COLLAPSE)
  echo[shift:]=dry[:-shift]*gain;signal+=echo
 signal*=np.clip((7-t)/.7,0,1)
 signal=np.tanh(signal*1.4)
 signal*=.94/max(1e-9,np.max(np.abs(signal)))
 with wave.open(str(out),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(np.int16(signal*32767).tobytes())
 quiet=signal[(t>COLLAPSE-.09)&(t<COLLAPSE)]
 assert np.max(np.abs(quiet))==0 and len(signal)==RATE*7
 print(f'{out}: 7 seconds; collapse {COLLAPSE:.6f}s; peak {np.max(np.abs(signal)):.3f}; quiet pocket verified')
if __name__=='__main__':build()
