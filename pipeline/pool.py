import os
import re, json, subprocess, glob
pool=[]
for f in sorted(glob.glob("/home/claude/clips/*.scenes.txt")):
    k=f.split("/")[-1].split(".")[0]
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"/home/claude/clips/{k}.mp4"]))
    cuts=[float(x) for x in re.findall(r"pts_time:([0-9.]+)",open(f).read())]
    luma=[]; t=None
    for line in open(f"/home/claude/clips/{k}.luma.txt"):
        m=re.search(r"pts_time:([0-9.]+)",line)
        if m: t=float(m.group(1))
        m=re.search(r"YAVG=([0-9.]+)",line)
        if m: luma.append((t,float(m.group(1))))
    b=[0]+cuts+[dur]
    for a,e in zip(b,b[1:]):
        a2,e2=a+0.2,e-0.2
        if k in("t1","t2","lt","pl","cv"): # skip opening/end cards
            if a2<1.5 or e2>dur-7: continue
        if e2-a2<1.0: continue
        ls=[y for (t,y) in luma if a2<=t<=e2]
        if not ls or min(ls)<28: continue
        # split long shots into <=3.2s pieces
        s=a2
        while e2-s>=1.0:
            d=min(3.2,e2-s); pool.append(dict(src=k,start=round(s,2),dur=round(d,2),luma=round(sum(ls)/len(ls),1))); s+=d
json.dump(pool,open("/home/claude/clips/pool.json","w"))
from collections import Counter
print(len(pool), round(sum(p['dur'] for p in pool)), Counter(p['src'] for p in pool))
