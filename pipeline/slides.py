import sys, math, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
NAVY = (13, 11, 30); PINK = (255, 46, 136); ORANGE = (255, 138, 61); TEAL = (25, 227, 208); YEL = (255, 210, 63); WHITE = (255, 255, 255)
OUT = "/home/claude/canal/slides"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import sun, palm  # noqa  (re-run of brand.py is harmless)

def bg_svg(W, H, hue_shift=0):
    hz = int(H * 0.70)
    cx = W // 2
    r = int(min(W, H) * 0.33)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f0826"/><stop offset=".5" stop-color="#2c0f52"/><stop offset=".68" stop-color="#7d1d62"/><stop offset=".70" stop-color="#0d0b1e"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g opacity=".55">{sun(cx, hz - r * 0.35, r, "sb")}</g>
<rect x="0" y="{hz}" width="{W}" height="{H - hz}" fill="#0d0b1e"/>
{"".join(f'<line x1="{cx + (i - 14) * W / 40}" y1="{hz}" x2="{cx + (i - 14) * W / 8}" y2="{H}" stroke="#19e3d0" stroke-opacity=".28" stroke-width="2.5"/>' for i in range(29))}
{"".join(f'<line x1="0" y1="{hz + d * (H - hz)}" x2="{W}" y2="{hz + d * (H - hz)}" stroke="#19e3d0" stroke-opacity=".28" stroke-width="2.5"/>' for d in [.05, .13, .25, .42, .66, .98])}
{palm(W * 0.08, hz + 10, H * 0.42, W / 1500, 1, "#07051a")}{palm(W * 0.93, hz + 10, H * 0.36, W / 1700, -1, "#07051a")}
</svg>'''

_bgcache = {}
def background(W, H):
    if (W, H) not in _bgcache:
        p = f"/tmp/bg_{W}x{H}.svg"
        open(p, "w").write(bg_svg(W, H))
        subprocess.run(["rsvg-convert", p, "-o", p + ".png"], check=True)
        im = Image.open(p + ".png").convert("RGB")
        # darken for legibility
        dark = Image.new("RGB", im.size, NAVY)
        _bgcache[(W, H)] = Image.blend(im, dark, 0.35)
    return _bgcache[(W, H)].copy()

def font(path, size): return ImageFont.truetype(path, size)

def wrap(draw, text, fpath, size, maxw, maxlines):
    while size > 20:
        f = font(fpath, size)
        words = text.split(); lines = []; cur = ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= maxw: cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        if len(lines) <= maxlines and all(draw.textlength(l, font=f) <= maxw for l in lines):
            return f, lines
        size = int(size * 0.92)
    return font(fpath, size), [text]

def grad_text(img, xy, text, f, anchor="la", colors=(YEL, ORANGE, PINK), shadow=True):
    d = ImageDraw.Draw(img)
    bbox = d.textbbox(xy, text, font=f, anchor=anchor)
    if shadow:
        sh = Image.new("L", img.size, 0)
        ImageDraw.Draw(sh).text((xy[0] + 6, xy[1] + 8), text, font=f, anchor=anchor, fill=200)
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        img.paste((0, 0, 0), (0, 0), sh)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=f, anchor=anchor, fill=255)
    x0, y0, x1, y1 = [int(round(c)) for c in bbox]
    h = max(1, y1 - y0)
    grad = Image.new("RGB", img.size)
    gd = ImageDraw.Draw(grad)
    for y in range(max(0, y0), min(img.size[1], y1 + 1)):
        t = (y - y0) / h
        if t < .5: a, b, u = colors[0], colors[1], t / .5
        else: a, b, u = colors[1], colors[2], (t - .5) / .5
        gd.line([(x0, y), (x1, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3)))
    img.paste(grad, (0, 0), mask)
    return bbox

def pill(d, x, y, text, f, fill=TEAL, color=NAVY, anchor="l"):
    tw = d.textlength(text, font=f); ph = f.size * 1.6; pw = tw + f.size * 1.4
    if anchor == "c": x = x - pw / 2
    d.rounded_rectangle([x, y, x + pw, y + ph], radius=ph / 2, fill=fill)
    d.text((x + pw / 2, y + ph / 2), text, font=f, fill=color, anchor="mm")
    return y + ph

def car_svg(w):
    # original generic retro coupe silhouette
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{int(w*0.38)}" viewBox="0 0 1000 380">
<defs><linearGradient id="cg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff2e88"/><stop offset="1" stop-color="#ff8a3d"/></linearGradient></defs>
<path d="M40,250 L60,195 Q80,175 150,170 L300,160 Q360,95 470,85 L640,88 Q720,95 790,160 L900,175 Q960,185 965,230 L960,262 Q955,280 930,280 L860,280 A75,75 0 0 0 712,280 L310,280 A75,75 0 0 0 162,280 L70,280 Q42,278 40,250 Z" fill="url(#cg)"/>
<path d="M330,165 Q380,110 470,104 L555,104 L555,165 Z M580,104 L640,106 Q700,112 755,165 L580,165 Z" fill="#0d0b1e" opacity=".85"/>
<rect x="60" y="215" width="900" height="8" fill="#ffd23f" opacity=".9"/>
<circle cx="236" cy="282" r="62" fill="#0d0b1e"/><circle cx="236" cy="282" r="30" fill="#19e3d0"/>
<circle cx="786" cy="282" r="62" fill="#0d0b1e"/><circle cx="786" cy="282" r="30" fill="#19e3d0"/>
<path d="M905,200 L955,205 L955,222 L905,220 Z" fill="#fff" opacity=".9"/>
</svg>'''

_car = {}
def car_img(w):
    if w not in _car:
        open("/tmp/car.svg", "w").write(car_svg(w))
        subprocess.run(["rsvg-convert", "/tmp/car.svg", "-o", "/tmp/car.png"], check=True)
        _car[w] = Image.open("/tmp/car.png").convert("RGBA")
    return _car[w]

_av = Image.open("/home/claude/canal/brand/avatar.png").convert("RGBA")
def brand_tag(img, s):
    d = ImageDraw.Draw(img)
    a = _av.resize((int(64 * s), int(64 * s)))
    m = Image.new("L", a.size, 0); ImageDraw.Draw(m).ellipse([0, 0, a.size[0], a.size[1]], fill=255)
    x, y = int(140 * s), int(100 * s)
    img.paste(a, (x, y), m)
    d.text((x + a.size[0] + 16 * s, y + a.size[1] / 2), "ZONA LEONIDA", font=font(XB, int(26 * s)), fill=WHITE, anchor="lm")

def render(slide, W, H, path, vertical=False, overlay=False):
    if overlay:
        img = Image.new('RGBA', (W, H), (13, 11, 30, 80))
        g = Image.new('L', (1, 256)); [g.putpixel((0, y), int(170 * abs(y - 128) / 128)) for y in range(256)]
        sc = Image.new('RGBA', (W, H), (13, 11, 30, 255)); sc.putalpha(g.resize((W, H)))
        img = Image.alpha_composite(img, sc)
    else:
        img = background(W, H)
    d = ImageDraw.Draw(img)
    s = W / 1920 if not vertical else W / 1080
    brand_tag(img, s * (1.25 if vertical else 1))
    lay = slide["lay"]
    M = int(W * 0.08)
    if vertical:
        cx = W // 2; y = int(H * 0.26)
        y = pill(d, cx, y, slide["k"], font(XB, int(44 * s)), anchor="c") + 50 * s
        f, lines = wrap(d, slide["t"], BLACK, int(150 * s), W - 2 * M, 4)
        for l in lines:
            bb = grad_text(img, (cx, y), l, f, anchor="ma"); y = bb[3] + 22 * s
        if slide["b"]:
            f2, l2 = wrap(d, slide["b"], SB, int(56 * s), W - 2 * M, 3); y += 30 * s
            for l in l2:
                d.text((cx, y), l, font=f2, fill=WHITE, anchor="ma"); y += f2.size * 1.25
    elif lay in ("hero", "list"):
        cx = W // 2; y = int(H * 0.22)
        y = pill(d, cx, y, slide["k"], font(XB, int(34 * s)), anchor="c") + 40 * s
        f, lines = wrap(d, slide["t"], BLACK, int(150 * s), W - 2 * M, 2)
        for l in lines:
            bb = grad_text(img, (cx, y), l, f, anchor="ma"); y = bb[3] + 20 * s
        if slide["b"]:
            f2, l2 = wrap(d, slide["b"], SB, int(48 * s), W - 2 * M, 2); y += 30 * s
            for l in l2:
                d.text((cx, y), l, font=f2, fill=WHITE, anchor="ma"); y += f2.size * 1.3
    elif lay == "num":
        R = int(170 * s); cx0 = M + R; cy0 = int(H * 0.42)
        d.ellipse([cx0 - R, cy0 - R, cx0 + R, cy0 + R], fill=PINK)
        d.ellipse([cx0 - R + 10 * s, cy0 - R + 10 * s, cx0 + R - 10 * s, cy0 + R - 10 * s], outline=YEL, width=int(6 * s))
        d.text((cx0, cy0), slide["k"], font=font(BLACK, int(200 * s if len(slide["k"]) < 2 else 160 * s)), fill=WHITE, anchor="mm")
        x = cx0 + R + int(80 * s); maxw = W - x - M
        f, lines = wrap(d, slide["t"], BLACK, int(120 * s), maxw, 3)
        tot = len(lines) * f.size * 1.08
        y = cy0 - tot / 2 - 40 * s
        for l in lines:
            bb = grad_text(img, (x, y), l, f); y += f.size * 1.08
        f2, l2 = wrap(d, slide["b"], SB, int(44 * s), maxw, 2); y += 30 * s
        for l in l2:
            d.text((x, y), l, font=f2, fill=WHITE); y += f2.size * 1.3
    elif lay == "stat":
        cx = W // 2; y = int(H * 0.14)
        y = pill(d, cx, y, slide["k"], font(XB, int(34 * s)), anchor="c") + 20 * s
        f, lines = wrap(d, slide["t"], BLACK, int(330 * s), W - 2 * M, 1)
        bb = grad_text(img, (cx, y), lines[0], f, anchor="ma"); y = bb[3] + 40 * s
        f2, l2 = wrap(d, slide["b"], XB, int(56 * s), W - 2 * M, 2)
        for l in l2:
            d.text((cx, y), l, font=f2, fill=WHITE, anchor="ma"); y += f2.size * 1.3
    elif lay == "car":
        x = M; y = int(H * 0.17)
        y = pill(d, x, y, slide["k"], font(XB, int(34 * s))) + 30 * s
        f, lines = wrap(d, slide["t"], BLACK, int(140 * s), W - 2 * M, 1)
        bb = grad_text(img, (x, y), lines[0], f); y = bb[3] + 30 * s
        f2, l2 = wrap(d, slide["b"], SB, int(46 * s), W * 0.6, 2)
        for l in l2:
            d.text((x, y), l, font=f2, fill=WHITE); y += f2.size * 1.3
        c = car_img(int(W * 0.5))
        if not overlay: img.paste(c, (W - M - c.size[0], int(H * 0.88) - c.size[1]), c)
    img.save(path) if overlay else img.save(path, quality=95)

def thumb(v, path):
    W, H = 1280, 720
    img = background(W, H); d = ImageDraw.Draw(img)
    l1, l2, tag = v["thumb"]
    f1, _ = wrap(d, l1, BLACK, 170, W - 120, 1)
    f2, _ = wrap(d, l2, BLACK, 110, W - 120, 1)
    # stroke + fill
    for txt, f, y, fill in [(l1, f1, 130, None), (l2, f2, 330, WHITE)]:
        d.text((W // 2, y), txt, font=f, anchor="ma", fill=NAVY, stroke_width=14, stroke_fill=NAVY)
        if fill: d.text((W // 2, y), txt, font=f, anchor="ma", fill=fill)
        else: grad_text(img, (W // 2, y), txt, f, anchor="ma", shadow=False)
        d = ImageDraw.Draw(img)
    pill(d, W // 2, 500, tag, font(XB, 44), fill=PINK, color=WHITE, anchor="c")
    a = _av.resize((150, 150)); img.paste(a, (W - 180, H - 180), a)
    d.rectangle([0, H - 18, W, H], fill=TEAL)
    img.save(path, quality=95)

if __name__ == "__main__":
    only = sys.argv[1:]
    for v in content.VIDEOS:
        if only and v["id"] not in only: continue
        vert = v["fmt"] == "v"
        W, H = (1134, 2016) if vert else (2016, 1134)
        for i, sl in enumerate(v["slides"]):
            render(sl, W, H, f"{OUT}/{v['id']}_{i:02d}.png", vert)
        thumb(v, f"/home/claude/canal/thumbs/{v['id']}.jpg")
    print("done")
