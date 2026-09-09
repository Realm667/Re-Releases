"""Compare identical frozen shader times in lit and dark lava test fixtures.

Capture with test_lava.py --label lit --time 3.75 and then --label dark
--time 3.75 --dark. Use the same renderer and --out for both runs.
"""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image

def compare(logs,renderer,previous=None):
    def frame(label,kind):
        return np.asarray(Image.open(logs/f'lava-{label}-{renderer}-{kind}-0.png').convert('RGB'),dtype=float)
    result={}
    for kind,region in [('surface',(slice(470,760),slice(250,1350))),('fall',(slice(80,430),slice(200,1400)))]:
        lit=frame('lit',kind)[region];dark=frame('dark',kind)[region]
        hot=lit[:,:,0]>150
        assert hot.sum()>1000,(kind,'too few luminous pixels',hot.sum())
        ratio=dark[:,:,0][hot]/np.maximum(1,lit[:,:,0][hot])
        result[kind]={'hot_pixels':int(hot.sum()),'dark_hot_retention_median':float(np.median(ratio)),
                      'dark_hot_retention_p10':float(np.percentile(ratio,10)),
                      'mean_red':float(lit[:,:,0].mean()),'red_p95':float(np.percentile(lit[:,:,0],95))}
        if previous:
            old=frame(previous,kind)[region]
            result[kind].update(previous_mean_red=float(old[:,:,0].mean()),previous_red_p95=float(np.percentile(old[:,:,0],95)))
        assert np.median(ratio)>0.85,(kind,'lost emission',result[kind])
    control=frame('dark','surface')[60:220,20:180].mean()/frame('lit','surface')[60:220,20:180].mean()
    result['non_lava_wall_dark_ratio']=float(control)
    assert control<0.65,'Dark fixture did not reduce ordinary lighting'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--logs',type=Path,default=Path(__file__).resolve().parent.parent/'logs/lava-test/logs')
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--previous',help='Optional label for an earlier-version frozen capture.')
    a=p.parse_args()
    result={r:compare(a.logs,r,a.previous) for r in (['0','1'] if a.renderer=='both' else [a.renderer])}
    (a.logs.parent/'light-metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
