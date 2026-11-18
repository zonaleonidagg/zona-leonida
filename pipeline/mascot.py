"""Original mascot for Zona Leonida: 'Lío', a cartoon alligator in a Vice City shirt."""
import subprocess, os
OUT = "/home/claude/canal/mascot"; os.makedirs(OUT, exist_ok=True)
K = "#141018"; G = "#57c26c"; G2 = "#9be08f"; GD = "#2f8f4a"; PINK = "#ff2e88"; YEL = "#ffd23f"; TEAL = "#19e3d0"
SW = 9

def eyes(kind):
    s = ""
    for cx in (215, 385):
        s += f'<circle cx="{cx}" cy="128" r="72" fill="{G}" stroke="{K}" stroke-width="{SW}"/>'
        if kind == "closed":
            s += f'<path d="M{cx-38},140 Q{cx},100 {cx+38},140" fill="none" stroke="{K}" stroke-width="11" stroke-linecap="round"/>'
        elif kind == "squeeze":
            d = 1 if cx < 300 else -1
            s += f'<path d="M{cx-34},112 L{cx+6*d},132 L{cx-34},152" fill="none" stroke="{K}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" transform="scale({1 if d>0 else -1},1) translate({0 if d>0 else -2*cx},0)"/>'
        else:
            r = 50 if kind != "wide" else 56
            s += f'<circle cx="{cx}" cy="132" r="{r}" fill="#fff" stroke="{K}" stroke-width="7"/>'
            pr = 15 if kind != "wide" else 11
            s += f'<circle cx="{cx + (8 if cx < 300 else -8)}" cy="138" r="{pr}" fill="{K}"/><circle cx="{cx + (12 if cx < 300 else -4)}" cy="132" r="5" fill="#fff"/>'
    return s

def brows(kind):
    if kind == "none": return ""
    s = ""
    for cx in (215, 385):
        d = -1 if cx < 300 else 1
        if kind == "up": y1, y2 = 52, 46
        elif kind == "angry": y1, y2 = 58, 78   # inner end lower
        elif kind == "worried": y1, y2 = 70, 52
        else: y1, y2 = 60, 60
        x_out, x_in = cx + d * 45, cx - d * 40
        s += f'<path d="M{x_out},{y1} L{x_in},{y2}" stroke="{K}" stroke-width="14" stroke-linecap="round"/>'
    return s

def mouth(kind):
    y = 318
    if kind == "smile":
        return f'<path d="M190,{y-6} Q300,{y+44} 410,{y-6}" fill="none" stroke="{K}" stroke-width="10" stroke-linecap="round"/>'
    if kind == "flat":
        return f'<path d="M205,{y+6} Q300,{y+16} 395,{y+6}" fill="none" stroke="{K}" stroke-width="10" stroke-linecap="round"/>'
    if kind == "frown":
        return f'<path d="M215,{y+22} Q300,{y-12} 385,{y+22}" fill="none" stroke="{K}" stroke-width="10" stroke-linecap="round"/>'
    if kind in ("open", "big", "o"):
        if kind == "o":
            return f'<ellipse cx="300" cy="{y+12}" rx="34" ry="40" fill="#5a1530" stroke="{K}" stroke-width="{SW}"/><ellipse cx="300" cy="{y+30}" rx="18" ry="12" fill="{PINK}"/>'
        h = 46 if kind == "open" else 74
        teeth = "".join(f'<path d="M{x},{y-2} l12,18 l12,-18 Z" fill="#fff" stroke="{K}" stroke-width="3"/>' for x in range(204, 386, 26))
        return (f'<path d="M190,{y-4} Q300,{y+h*1.5} 410,{y-4} Z" fill="#5a1530" stroke="{K}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<ellipse cx="300" cy="{y+h*0.62}" rx="{50 if kind=="open" else 66}" ry="{h*0.28}" fill="{PINK}"/>{teeth}')
    return ""

def body(pose):
    arms = {
        "neutral": (f'<path d="M150,470 Q90,520 100,590" fill="none" stroke="{K}" stroke-width="44" stroke-linecap="round"/><path d="M150,470 Q90,520 100,590" fill="none" stroke="{G}" stroke-width="28" stroke-linecap="round"/>'
                    f'<path d="M450,470 Q510,520 500,590" fill="none" stroke="{K}" stroke-width="44" stroke-linecap="round"/><path d="M450,470 Q510,520 500,590" fill="none" stroke="{G}" stroke-width="28" stroke-linecap="round"/>'),
        "up": (f'<path d="M150,470 Q70,420 80,330" fill="none" stroke="{K}" stroke-width="44" stroke-linecap="round"/><path d="M150,470 Q70,420 80,330" fill="none" stroke="{G}" stroke-width="28" stroke-linecap="round"/>'
               f'<path d="M450,470 Q530,420 520,330" fill="none" stroke="{K}" stroke-width="44" stroke-linecap="round"/><path d="M450,470 Q530,420 520,330" fill="none" stroke="{G}" stroke-width="28" stroke-linecap="round"/>'),
        "point": (f'<path d="M150,470 Q90,520 100,590" fill="none" stroke="{K}" stroke-width="44" stroke-linecap="round"/><path d="M150,470 Q90,520 100,590" fill="none" stroke="{G}" stroke-width="28" stroke-linecap="round"/>'
                  f'<path d="M450,470 Q540,440 560,380" fill="none" stroke="{K}" stroke-width="44" stroke-linecap="round"/><path d="M450,470 Q540,440 560,380" fill="none" stroke="{G}" stroke-width="28" stroke-linecap="round"/>'
                  f'<path d="M560,380 L568,340" stroke="{K}" stroke-width="30" stroke-linecap="round"/><path d="M560,380 L568,340" stroke="{G}" stroke-width="14" stroke-linecap="round"/>'),
    }[pose]
    flowers = "".join(f'<circle cx="{x}" cy="{y}" r="13" fill="{YEL}"/><circle cx="{x}" cy="{y}" r="5" fill="{PINK}"/>' for x, y in [(215, 470), (330, 520), (250, 580), (380, 460), (395, 590), (290, 450)])
    leaves = "".join(f'<path d="M{x},{y} q18,-22 36,0 q-18,10 -36,0 Z" fill="{TEAL}"/>' for x, y in [(180, 520), (345, 560), (300, 490), (410, 520)])
    return (arms +
            f'<path d="M170,620 L190,690 L280,690 L300,640 L320,690 L410,690 L430,620 Z" fill="{TEAL}" stroke="{K}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M150,440 Q300,400 450,440 L440,630 Q300,650 160,630 Z" fill="{PINK}" stroke="{K}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'{flowers}{leaves}'
            f'<path d="M270,420 L300,470 L330,420" fill="{G}" stroke="{K}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M300,470 L300,640" stroke="{K}" stroke-width="5"/>'
            f'<ellipse cx="230" cy="700" rx="58" ry="22" fill="{GD}" stroke="{K}" stroke-width="{SW}"/><ellipse cx="370" cy="700" rx="58" ry="22" fill="{GD}" stroke="{K}" stroke-width="{SW}"/>')

def head(e, b, m):
    return (f'<path d="M95,250 Q90,110 300,105 Q510,110 505,250 Q520,420 300,420 Q80,420 95,250 Z" fill="{G}" stroke="{K}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<rect x="150" y="225" width="300" height="170" rx="85" fill="{G2}" stroke="{K}" stroke-width="7"/>'
            f'<ellipse cx="262" cy="258" rx="11" ry="8" fill="{K}"/><ellipse cx="338" cy="258" rx="11" ry="8" fill="{K}"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{GD}"/>' for x, y in [(130, 330), (470, 330), (300, 170)])
            + mouth(m) + (f'<path d="M178,300 l12,24 l12,-22 Z" fill="#fff" stroke="{K}" stroke-width="4"/><path d="M398,300 l12,24 l12,-22 Z" fill="#fff" stroke="{K}" stroke-width="4"/>' if m in ('smile','flat','frown') else '') + eyes(e) + brows(b))

EXPR = {  # name: (eyes, brows, mouth_closed, mouth_open, pose)
    "neutral":  ("normal", "flat",    "smile", "open", "neutral"),
    "feliz":    ("closed", "up",      "smile", "big",  "up"),
    "sorpresa": ("wide",   "up",      "o",     "o",    "up"),
    "duda":     ("normal", "worried", "flat",  "open", "neutral"),
    "serio":    ("normal", "angry",   "frown", "open", "point"),
    "risa":     ("squeeze","up",      "big",   "big",  "up"),
}

def svg(e, b, m, pose, seed=1):
    flt = (f'<defs><filter id="hd" x="-5%" y="-5%" width="110%" height="110%">'
           f'<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{seed}" result="n"/>'
           f'<feDisplacementMap in="SourceGraphic" in2="n" scale="9" xChannelSelector="R" yChannelSelector="G"/></filter></defs>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="760" viewBox="0 -20 600 760">{flt}<g filter="url(#hd)">{body(pose)}{head(e, b, m)}</g></svg>'

if __name__ == "__main__":
    for name, (e, b, mc, mo, pose) in EXPR.items():
        for st, m in (("c", mc), ("o", mo)):
            for v in range(3):
                p = f"{OUT}/{name}_{st}_{v}.svg"; open(p, "w").write(svg(e, b, m, pose, seed=v * 7 + 3))
                subprocess.run(["rsvg-convert", "-w", "600", p, "-o", p[:-4] + ".png"], check=True)
    print("ok")
