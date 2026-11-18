import sys, json, subprocess, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content, slides
from PIL import Image, ImageEnhance, ImageDraw

C = "/home/claude/canal"; CL = "/home/claude/clips"
dur = json.load(open(f"{C}/audio/dur.json"))
pool = json.load(open(f"{CL}/pool.json"))
EXCL = {13, 19, 29, 35, 41, 45, 50, 52, 53, 70, 73}
H_IDX = [i for i, x in enumerate(pool) if not x["src"].startswith("el") and i not in EXCL]
V_IDX = [i for i, x in enumerate(pool) if x["src"].startswith("el") and i not in EXCL]
PRECROP = {"t2": "crop=1920:864:0:108,", "pl": "crop=1920:960:0:60,"}

MAP = {
 ("00_trailer_canal", 0): [79, 86, 84], ("00_trailer_canal", 1): [80, 98, 55], ("00_trailer_canal", 2): [54, 66],
 ("01_primeros_pasos", 0): [79, 86, 84], ("01_primeros_pasos", 2): [97], ("01_primeros_pasos", 3): [62, 96],
 ("01_primeros_pasos", 4): [97, 64], ("01_primeros_pasos", 6): [112, 110], ("01_primeros_pasos", 7): [98, 82],
 ("01_primeros_pasos", 8): [82, 84], ("01_primeros_pasos", 10): [97, 109], ("01_primeros_pasos", 11): [54, 66, 120],
 ("01_primeros_pasos", 12): [111, 106],
 ("02_coches", 0): [84, 82, 98], ("02_coches", 2): [95, 113], ("02_coches", 3): [54], ("02_coches", 4): [84],
 ("02_coches", 5): [55, 78], ("02_coches", 6): [71, 80, 139, 140],
 ("03_secretos", 1): [136, 137], ("03_secretos", 2): [47, 48, 49], ("03_secretos", 3): [47, 48],
 ("03_secretos", 4): [75, 76, 77, 114], ("03_secretos", 5): [46], ("03_secretos", 7): [115, 116, 117],
 ("05_personajes", 1): [76, 77, 87], ("05_personajes", 2): [49, 47, 48], ("05_personajes", 4): [101, 103, 104],
 ("05_personajes", 5): [85], ("05_personajes", 6): [127, 131], ("05_personajes", 7): [61, 125],
 ("05_personajes", 8): [130, 133],
 ("07_dinero", 1): [98, 82], ("07_dinero", 2): [97, 109], ("07_dinero", 3): [130, 133],
 ("08_historia_retrasos", 1): [79, 86], ("08_historia_retrasos", 7): [54, 66],
 ("09_gta6_vs_gta5", 1): [83, 86], ("09_gta6_vs_gta5", 2): [54, 66], ("09_gta6_vs_gta5", 3): [62, 96],
 ("09_gta6_vs_gta5", 4): [111, 106],
 ("10_actividades", 1): [111], ("10_actividades", 2): [80, 139, 71], ("10_actividades", 3): [140, 93],
 ("10_actividades", 4): [55, 78], ("10_actividades", 5): [85, 127, 124],
}
VMAP = {("S6_waink", 1): [24, 25, 26], ("S2_seis_estrellas", 1): [16, 17], ("S2_seis_estrellas", 3): [14, 15],
        ("S7_vice_city", 1): [42, 43, 44], ("S4_no_hagas", 2): [16, 17, 18]}

def run(a):
    r = subprocess.run(a, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode: raise SystemExit(r.stderr.decode()[-1500:])

def pick(v, i, D, vert, rng, used):
    want = list((VMAP if vert else MAP).get((v["id"], i), []))
    base = (V_IDX + H_IDX) if vert else H_IDX
    shots, tot = [], 0.0
    for j in want:
        shots.append(j); tot += pool[j]["dur"]; used.add(j)
    n = 0
    while want and tot < D + 0.1:
        j = want[n % len(want)]; shots.append(j); tot += pool[j]["dur"]; n += 1
    while tot < D + 0.1:
        free = [j for j in base if j not in used] or base
        if vert:
            vf = [j for j in free if j in V_IDX]
            if vf and rng.random() < 0.6: free = vf
        j = rng.choice(free); used.add(j); shots.append(j); tot += pool[j]["dur"]
    return shots

def render_video(v):
    vert = v["fmt"] == "v"; W, H = (1080, 1920) if vert else (1920, 1080)
    rng = random.Random(v["id"]); used = set()
    tmp = f"/tmp/r2_{v['id']}"; os.makedirs(tmp, exist_ok=True)
    vl = open(f"{tmp}/v.txt", "w"); al = open(f"{tmp}/a.txt", "w")
    first_shot = None
    for i, sl in enumerate(v["slides"]):
        key = f"{v['id']}_{i:02d}"; D = round(dur[key] + 0.75, 3)
        ov = f"{tmp}/ov{i:02d}.png"; slides.render(sl, W, H, ov, vert, overlay=True)
        shots = pick(v, i, D, vert, rng, used)
        if first_shot is None: first_shot = shots[0]
        args = ["ffmpeg", "-y"]; fl = []
        for n, j in enumerate(shots):
            x = pool[j]
            args += ["-ss", str(x["start"]), "-t", str(x["dur"]), "-i", f"{CL}/{x['src']}.mp4"]
            fl.append(f"[{n}:v]{PRECROP.get(x['src'], '')}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[s{n}]")
        k = len(shots)
        args += ["-framerate", "30", "-i", ov]
        fl.append("".join(f"[s{n}]" for n in range(k)) + f"concat=n={k}:v=1:a=0,trim=duration={D},setpts=PTS-STARTPTS,eq=saturation=1.08[bg]")
        fl.append(f"[{k}:v]format=rgba,loop=-1:1,trim=duration={D},setpts=PTS-STARTPTS[o]")
        fl.append(f"[bg][o]overlay=0:0:format=auto,format=yuv420p,fade=in:st=0:d=0.2,fade=out:st={D - 0.2}:d=0.2[out]")
        out = f"{tmp}/{i:02d}.mp4"
        run(args + ["-filter_complex", ";".join(fl), "-map", "[out]", "-an", "-r", "30", "-c:v", "libx264", "-crf", "20",
                    "-preset", "veryfast", "-pix_fmt", "yuv420p", out + ".part.mp4"])
        os.rename(out + ".part.mp4", out); vl.write(f"file '{out}'\n")
        run(["ffmpeg", "-y", "-i", f"{C}/audio/{key}.wav", "-af", f"adelay=350|350,apad,atrim=0:{D},aresample=44100", "-ac", "2", f"{tmp}/{i:02d}.wav"])
        al.write(f"file '{tmp}/{i:02d}.wav'\n")
    vl.close(); al.close()
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/v.txt", "-c", "copy", f"{tmp}/video.mp4"])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/a.txt", "-c", "copy", f"{tmp}/voice.wav"])
    os.makedirs(f"{C}/video2", exist_ok=True)
    final = f"{C}/video2/{v['id']}.mp4"
    run(["ffmpeg", "-y", "-i", f"{tmp}/video.mp4", "-i", f"{tmp}/voice.wav", "-stream_loop", "-1", "-i", f"{C}/audio/music_loop.wav",
         "-filter_complex", "[2:a]volume=0.13[m];[1:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", final + ".part.mp4"])
    os.rename(final + ".part.mp4", final)
    return first_shot

def thumb_with_footage(v, j):
    x = pool[j]; f = f"/tmp/th_{v['id']}.jpg"
    run(["ffmpeg", "-y", "-ss", str(x["start"] + x["dur"] / 2), "-i", f"{CL}/{x['src']}.mp4", "-frames:v", "1",
         "-vf", f"{PRECROP.get(x['src'], '')}scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720", f])
    bg = ImageEnhance.Brightness(Image.open(f).convert("RGB")).enhance(0.7)
    slides._bgcache[(1280, 720)] = bg
    slides.thumb(v, f"{C}/thumbs/{v['id']}.jpg")
    slides._bgcache.pop((1280, 720), None)

if __name__ == "__main__":
    only = sys.argv[1:]
    for v in content.VIDEOS:
        if only and v["id"] not in only: continue
        j = render_video(v)
        if v["fmt"] == "h":
            thumb_with_footage(v, (MAP.get((v["id"], 0)) or [j])[0])
        print(v["id"], "ok", flush=True)
