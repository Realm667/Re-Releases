"""Deterministic seven-second electrical score. No borrowed audio or gameplay RNG."""
from pathlib import Path
import wave
import numpy as np

def build(root=None):
 root=Path(root) if root else Path(__file__).resolve().parent.parent
 out=root/'tutnt/sounds/utnt-source/finale.wav';out.parent.mkdir(parents=True,exist_ok=True)
 rate=44100;t=np.arange(rate*7)/rate;rng=np.random.default_rng(66704)
 noise=rng.standard_normal(len(t))
 # Filter the noise into air, electric grain and a low cavern tail.
 freq=np.fft.rfftfreq(len(t),1/rate);spectrum=np.fft.rfft(noise)
 def band(lo,hi):
  f=np.fft.irfft(spectrum*(1-np.exp(-(freq/lo)**2))*np.exp(-(freq/hi)**2),n=len(t))
  return f/(np.std(f)+1e-9)
 grain=band(500,6000);air=band(1800,9000);low=band(24,140)
 strain=np.clip((t-.7)/3.8,0,1)*(t<4.5)
 phase=2*np.pi*(82*t+12*t*t)
 signal=(np.sin(phase)*.065+np.sin(phase*2.01)*.018)*strain
 signal+=grain*.022*strain*(.7+.3*np.sin(t*31)**2)
 # Two separated arcs illuminate the architecture; small cracks sever bonds.
 events=[(111/35,.23),(140/35,.28),(158/35,.39)]+[(x/35,.12) for x in (163,168,173,178,183)]
 dry=np.zeros_like(t)
 for at,amp in events:
  age=np.maximum(0,t-at);gate=t>=at
  dry+=amp*gate*(grain*np.exp(-age*26)+air*.28*np.exp(-age*65))
  signal+=amp*.14*low*gate*np.exp(-age*2.3)
 signal+=dry
 for delay,gain in [(0.085,.24),(.173,.18),(.31,.12),(.57,.08),(.93,.055)]:
  shift=int(delay*rate);signal[shift:]+=dry[:-shift]*gain
 # The break leaves a falling electrical pitch and a long, restrained tail.
 age=np.maximum(0,t-158/35)
 signal+=(t>=158/35)*np.exp(-age*2.4)*np.sin(2*np.pi*(65*age+90*(1-np.exp(-age*2))))*.09
 signal*=np.minimum(1,t/.025)*np.clip((7-t)/.45,0,1)
 signal=np.tanh(signal*1.15)*.82
 with wave.open(str(out),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(np.int16(signal*32767).tobytes())
 print(f'{out}: 7 seconds, peak {np.max(np.abs(signal)):.3f}')
if __name__=='__main__':build()
