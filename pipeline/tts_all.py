import os, sys, re, soundfile as sf, numpy as np, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import content
from kokoro_onnx import Kokoro
k=Kokoro("/home/claude/tts/kokoro-v1.0.onnx","/home/claude/tts/voices-v1.0.bin")
def fix(t):
    for a,b in content.TTS_FIX: t=t.replace(a,b)
    return t
import os
dur=json.load(open('/home/claude/canal/audio/dur.json')) if os.path.exists('/home/claude/canal/audio/dur.json') else {}
import os
for v in content.VIDEOS:
    for i,s in enumerate(v["slides"]):
        out=f"/home/claude/canal/audio/{v['id']}_{i:02d}.wav"
        if os.path.exists(out) and f"{v['id']}_{i:02d}" in dur: continue
        a,sr=k.create(fix(s["n"]),voice="em_alex",speed=1.08,lang="es")
        sf.write(out,a,sr); dur[f"{v['id']}_{i:02d}"]=len(a)/sr
json.dump(dur,open("/home/claude/canal/audio/dur.json","w"),indent=0)
print(sum(dur.values()))
