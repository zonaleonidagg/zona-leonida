import numpy as np, soundfile as sf, sys, random
sr=44100
def m(n): return 440*2**((n-69)/12)
def osc(f,t,kind):
    if kind=="saw": return 2*(t*f-np.floor(0.5+t*f))
    if kind=="sq": return np.sign(np.sin(2*np.pi*f*t))
    if kind=="tri": return 2*np.abs(2*(t*f-np.floor(t*f+0.5)))-1
    return np.sin(2*np.pi*f*t)
def note(f,d,kind,a,r):
    t=np.arange(int(sr*d))/sr
    env=np.minimum(1,t/a)*np.clip((d-t)/r,0,1)
    return osc(f,t,kind)*env
PROGS=[[0,-4,3,-2],[0,5,-3,-5],[0,-2,-4,-5],[0,3,5,-2],[0,-5,-3,-4],[0,7,5,3]]
def track(seed,out,secs=200):
    R=random.Random(seed); np.random.seed(seed)
    bpm=R.choice([84,92,98,104,110,118,124]); beat=60/bpm; bar=4*beat
    root=R.randint(45,55); minor=R.random()<0.7
    prog=R.choice(PROGS); padk=R.choice(["saw","tri","sq"]); leadk=R.choice(["sin","tri","sq"])
    arp_pat=R.choice([[0,1,2,3],[0,2,1,3],[0,1,2,1],[2,1,0,1],[0,2,3,2]])
    kick_pat=R.choice([[0,2],[0,1.5,2],[0,2.5],[0,0.75,2,2.5]]); hat_div=R.choice([2,4]); swing=R.choice([0,0.04])
    L=int(sr*bar*len(prog)*2); outb=np.zeros(L+sr*2)
    third=3 if minor else 4
    for rep in range(2):
      for ci,deg in enumerate(prog):
        s0=int((rep*len(prog)+ci)*bar*sr); r=root+deg
        ch=[r,r+third,r+7]
        pad=sum(note(m(n+12),bar,padk,0.3,0.6)+note(m(n+12)*1.006,bar,padk,0.3,0.6) for n in ch)*0.028
        outb[s0:s0+len(pad)]+=pad
        for e in range(8):
            step=beat/2; b=note(m(r-12),step*0.85,"sq" if padk!="sq" else "saw",0.005,0.05)*0.09
            p=s0+int(e*step*sr); outb[p:p+len(b)]+=b
        arp=ch+[ch[1]+12]
        for e in range(16):
            n=arp[arp_pat[e%4]]+24; b=note(m(n),beat/4*0.8,leadk,0.002,0.06)*0.045
            p=s0+int((e*beat/4+(swing if e%2 else 0))*sr); outb[p:p+len(b)]+=b
        for k in kick_pat:
            t=np.arange(int(sr*0.25))/sr; kick=np.sin(2*np.pi*(48+90*np.exp(-t*30))*t)*np.exp(-t*12)*0.33
            p=s0+int(k*beat*sr); outb[p:p+len(kick)]+=kick
            p=s0+int((k+2)*beat*sr) if k<2 else None
        for k in range(4*hat_div):
            hat=np.random.randn(int(sr*0.03))*np.exp(-np.arange(int(sr*0.03))/250)*0.03
            p=s0+int((k*beat/hat_div+(swing if k%2 else 0))*sr); outb[p:p+len(hat)]+=hat
        for k in (1,3):
            sn=np.random.randn(int(sr*0.15))*np.exp(-np.arange(int(sr*0.15))/1400)*0.11
            p=s0+int(k*beat*sr); outb[p:p+len(sn)]+=sn
    outb=outb[:L]; reps=int(np.ceil(secs*sr/L)); full=np.tile(outb,reps)[:int(secs*sr)]
    full/=np.abs(full).max()*1.1
    sf.write(out,np.stack([full,full],1),sr); return bpm
import os, zlib
os.makedirs("/home/claude/canal/music",exist_ok=True)
for vid in sys.argv[1:]:
    print(vid, track(zlib.crc32(vid.encode()) % 100000, f"/home/claude/canal/music/{vid}.wav"))
