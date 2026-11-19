"""TikTok-style vertical videos: full-screen footage, inset clip, word captions, talking original mascot."""
import sys, json, subprocess, os, random, math, re
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content, render2
from PIL import Image, ImageDraw, ImageFont

C = "/home/claude/canal"; CL = "/home/claude/clips"; M = f"{C}/mascot"
W, H, FPS = 1080, 1920, 30
F = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 92)
FONTS = {}
pool = render2.pool; dur = render2.dur
MASC = {}
def masc(name, st, var=0):
    k = (name, st, var)
    if k not in MASC:
        im = Image.open(f"{M}/{name}_{st}_{var}.png").convert("RGBA")
        MASC[k] = im.resize((520, int(520 * im.size[1] / im.size[0])), Image.LANCZOS)
    return MASC[k]

def expr_for(v, i, sl):
    n = len(v["slides"])
    if i == 0: return "sorpresa"
    if i == n - 1: return "feliz"
    t = (sl["t"] + " " + sl["n"]).upper()
    if any(w in t for w in ("NO ", "ERROR", "OJO", "POLICÍA", "PIERDE", "CARO", "DAÑ")): return "serio"
    if any(w in t for w in ("?", "¿", "QUIZÁ", "CREE", "PODRÍA")): return "duda"
    return ["neutral", "risa", "neutral", "serio"][i % 4]

def run(a):
    r = subprocess.run(a, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode: raise SystemExit(r.stderr.decode()[-1500:])

def make(v):
    vid = v["id"]; tmp = f"/tmp/tt_{vid}"; os.makedirs(tmp, exist_ok=True)
    rng = random.Random(vid + "tt"); used = set()
    # timeline
    segs = []; t0 = 0.0
    for i, sl in enumerate(v["slides"]):
        D = round(dur[f"{vid}_{i:02d}"] + 0.75, 3); segs.append((t0, D, sl, i)); t0 += D
    total = t0
    # background (vertical, footage) and inset (horizontal) shot lists
    def build(kind, out, Wd, Hd):
        args = ["ffmpeg", "-y"]; fl = []; n = 0
        for (s0, D, sl, i) in segs:
            if kind == "bg":
                shots = render2.pick(v, i, D, True, rng, used)
            else:
                want = render2.MAP.get((vid, i), [])
                shots, tot = list(want), sum(pool[j]["dur"] for j in want)
                while tot < D + 0.1:
                    j = rng.choice(render2.H_IDX); shots.append(j); tot += pool[j]["dur"]
            for j in shots:
                x = pool[j]
                args += ["-ss", str(x["start"]), "-t", str(x["dur"]), "-i", f"{CL}/{x['src']}.mp4"]
                fl.append(f"[{n}:v]{render2.PRECROP.get(x['src'], '')}scale={Wd}:{Hd}:force_original_aspect_ratio=increase,crop={Wd}:{Hd},setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[s{n}]"); n += 1
            # per-slide trim to keep sync
            fl.append("".join(f"[s{k}]" for k in range(n - len(shots), n)) + f"concat=n={len(shots)}:v=1:a=0,trim=duration={D},setpts=PTS-STARTPTS[g{i}]")
        fl.append("".join(f"[g{i}]" for (_, _, _, i) in segs) + f"concat=n={len(segs)}:v=1:a=0[out]")
        run(args + ["-filter_complex", ";".join(fl), "-map", "[out]", "-an", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", out])
    build("bg", f"{tmp}/bg.mp4", W, H)
    build("in", f"{tmp}/in.mp4", 760, 428)
    # audio envelope for lip flap
    voice = f"/tmp/r2_{vid}/voice.wav"
    a, sr = sf.read(voice); a = a.mean(1) if a.ndim > 1 else a
    hop = sr // FPS; env = np.array([np.sqrt(np.mean(a[k * hop:(k + 1) * hop] ** 2) + 1e-12) for k in range(int(total * FPS) + 2)])
    thr = max(0.02, np.percentile(env, 60) * 0.5)
    # word timings
    words = []
    for (s0, D, sl, i) in segs:
        ws = sl["n"].split(); spoken = dur[f"{vid}_{i:02d}"]; st = s0 + 0.35
        tot = sum(len(w) + 2 for w in ws); acc = 0
        for w in ws:
            a0 = st + spoken * acc / tot; acc += len(w) + 2
            words.append((a0, st + spoken * acc / tot, w, i))
    # chunk into groups of up to 3 words, break at punctuation
    groups = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or re.search(r"[.,:;?!]$", w[2]):
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    # overlay frames
    mask = Image.new("L", (760, 428), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, 759, 427], 36, fill=255); mask.save(f"{tmp}/mask.png")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-i", f"{tmp}/bg.mp4", "-i", f"{tmp}/in.mp4", "-loop", "1", "-i", f"{tmp}/mask.png",
                          "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:",
                          "-filter_complex", "[2:v]format=gray,trim=duration=%f[m];[1:v]format=rgba[i];[i][m]alphamerge[ir];[0:v][ir]overlay=160:230:shortest=1[b];[b][3:v]overlay=0:0:format=auto,format=yuv420p[o]" % total,
                          "-map", "[o]", "-t", str(total), "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"{tmp}/vid.mp4"], stdin=subprocess.PIPE)
    av = Image.open(f"{C}/brand/avatar.png").convert("RGBA").resize((86, 86))
    am = Image.new("L", (86, 86), 0); ImageDraw.Draw(am).ellipse([0, 0, 85, 85], fill=255)
    nF = int(total * FPS); gi = 0
    for fno in range(nF):
        t = fno / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([154, 224, 160 + 766, 230 + 434], 40, outline=(255, 255, 255, 255), width=8)
        im.paste(av, (60, 80), am); d.text((160, 123), "@ZonaLeonida", font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 40), fill=(255, 255, 255, 235), anchor="lm", stroke_width=4, stroke_fill=(0, 0, 0, 200))
        # step label + big title of the current scene
        seg = [s for s in segs if s[0] <= t < s[0] + s[1]] or [segs[-1]]
        s0, D, sl, i = seg[0]
        kk, tt = sl.get("k", ""), sl.get("t", "")
        if kk:
            fk = FONTS.setdefault("k", ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 40))
            tw = d.textlength(kk, font=fk)
            d.rounded_rectangle([W / 2 - tw / 2 - 28, 690, W / 2 + tw / 2 + 28, 750], 30, fill=(25, 227, 208, 255))
            d.text((W / 2, 720), kk, font=fk, fill=(13, 11, 30, 255), anchor="mm")
        if tt:
            fs = 104
            while True:
                ft = FONTS.setdefault(("t", fs), ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", fs))
                words = tt.split(); lines = [""]
                for w_ in words:
                    cand = (lines[-1] + " " + w_).strip()
                    if d.textlength(cand, font=ft) <= 980: lines[-1] = cand
                    else: lines.append(w_)
                if len(lines) <= 2 or fs <= 60: break
                fs -= 8
            ty = 770
            for ln in lines:
                d.text((W / 2, ty), ln, font=ft, fill=(255, 210, 63, 255), anchor="ma", stroke_width=12, stroke_fill=(0, 0, 0, 255))
                ty += int(fs * 1.05)
        # caption
        while gi < len(groups) - 1 and t >= groups[gi + 1][0][0]: gi += 1
        g = groups[gi]
        if g[0][0] - 0.05 <= t <= g[-1][1] + 0.4:
            txt = [w[2].upper() for w in g]
            fs = 92; FF = F
            while True:
                widths = [d.textlength(x, font=FF) for x in txt]; sp = 26
                if sum(widths) + sp * (len(txt) - 1) <= 960 or fs <= 50: break
                fs -= 6; FF = FONTS.setdefault(fs, ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", fs))
            x = W / 2 - (sum(widths) + sp * (len(txt) - 1)) / 2; y = 1030
            for k, (w, wd) in enumerate(zip(txt, widths)):
                active = g[k][0] <= t < g[k][1]
                d.text((x, y + (92 - fs) // 2), w, font=FF, fill=(255, 210, 63, 255) if active else (255, 255, 255, 255), stroke_width=12, stroke_fill=(0, 0, 0, 255))
                x += wd + sp
        # mascot
        seg = [s for s in segs if s[0] <= t < s[0] + s[1]] or [segs[-1]]
        s0, D, sl, i = seg[0]
        name = expr_for(v, i, sl)
        talking = env[min(fno, len(env) - 1)] > thr and (fno // 3) % 2 == 0
        mi = masc(name, "o" if talking else "c", (fno // 4) % 3)
        bob = int(10 * math.sin(t * 6)) if talking else int(4 * math.sin(t * 2))
        pop = min(1.0, (t - s0) / 0.15)
        if pop < 1:
            mi = mi.resize((int(mi.size[0] * (0.85 + 0.15 * pop)), int(mi.size[1] * (0.85 + 0.15 * pop))))
        im.alpha_composite(mi, (W // 2 - mi.size[0] // 2, H - mi.size[1] + 40 + bob))
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    os.makedirs(f"{C}/video_tiktok", exist_ok=True); final = f"{C}/video_tiktok/{vid}.mp4"
    run(["ffmpeg", "-y", "-i", f"{tmp}/vid.mp4", "-i", voice, "-stream_loop", "-1", "-i", f"{C}/audio/music_loop.wav",
         "-filter_complex", "[2:a]volume=0.13[m];[1:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", final + ".part.mp4"])
    os.rename(final + ".part.mp4", final)

if __name__ == "__main__":
    for v in content.VIDEOS:
        if v["id"] in sys.argv[1:]:
            make(v); print(v["id"], "ok", flush=True)
