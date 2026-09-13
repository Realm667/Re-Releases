"""Build the restrained, deterministic TITLEMAP reveal accent (no external samples)."""
from pathlib import Path
import argparse,io,wave,math,struct
ROOT=Path(__file__).resolve().parents[1]

def render():
    rate=44100;duration=1.8;data=bytearray();phase=0.0
    for i in range(int(rate*duration)):
        t=i/rate
        frequency=48+36*math.exp(-t*5)
        phase+=2*math.pi*frequency/rate
        envelope=(1-math.exp(-t*95))*math.exp(-t*3.4)*min(1,(duration-t)/0.16)
        value=envelope*(0.25*math.sin(phase)+0.045*math.sin(phase*2.003)+0.02*math.sin(phase*3.01))
        data.extend(struct.pack('<h',round(value*32767)))
    out=io.BytesIO()
    with wave.open(out,'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(data)
    return out.getvalue()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');a=parser.parse_args()
    p=ROOT/'tutnt/sounds/title/reveal.wav';data=render()
    if a.check:assert p.read_bytes()==data,'Stale TITLEMAP reveal accent'
    else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    print('TITLEMAP accent: 1.8 seconds, mono 44100 Hz, deterministic PCM verified')
