import os
import math, subprocess
NAVY="#0d0b1e"; PINK="#ff2e88"; ORANGE="#ff8a3d"; TEAL="#19e3d0"; YEL="#ffd23f"
def palm(x,y,h,s=1.0,flip=1,color="#0d0b1e"):
    # trunk: curved tapered
    tx = x + flip*h*0.18
    trunk=f'<path d="M{x-8*s},{y} Q{x+flip*h*0.05},{y-h*0.5} {tx-3*s},{y-h} L{tx+3*s},{y-h} Q{x+flip*h*0.05+10*s},{y-h*0.5} {x+8*s},{y} Z" fill="{color}"/>'
    fr=""
    cx,cy=tx,y-h
    for ang,L in [(-170,1.0),(-140,0.9),(-110,0.7),(-70,0.7),(-40,0.9),(-10,1.0),(160,0.6),(20,0.6)]:
        a=math.radians(ang); L*=h*0.45
        ex,ey=cx+math.cos(a)*L, cy+math.sin(a)*L*0.6+L*0.35
        mx,my=cx+math.cos(a)*L*0.5, cy+math.sin(a)*L*0.6-L*0.15
        nx,ny=-(ey-cy),(ex-cx); n=math.hypot(nx,ny) or 1; w=L*0.12
        fr+=f'<path d="M{cx},{cy} Q{mx+nx/n*w},{my+ny/n*w} {ex},{ey} Q{mx-nx/n*w*0.3},{my-ny/n*w*0.3} {cx},{cy} Z" fill="{color}"/>'
    return trunk+fr
def sun(cx,cy,r,idp):
    stripes="".join(f'<rect x="{cx-r}" y="{cy+r*(0.15+i*0.17)}" width="{2*r}" height="{r*(0.03+i*0.025)}" fill="{NAVY}"/>' for i in range(5))
    return f'''<defs><linearGradient id="{idp}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{YEL}"/><stop offset=".55" stop-color="{ORANGE}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<clipPath id="{idp}c"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>
<g clip-path="url(#{idp}c)"><circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{idp})"/>{stripes}</g>'''
FONT="Inter Display"
# Avatar 800
av=f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
<defs><radialGradient id="bg" cx=".5" cy=".35" r=".8"><stop offset="0" stop-color="#2a1550"/><stop offset="1" stop-color="{NAVY}"/></radialGradient></defs>
<rect width="800" height="800" fill="url(#bg)"/>
{sun(400,330,215,"s1")}
<rect x="0" y="470" width="800" height="330" fill="{NAVY}"/>
{"".join(f'<line x1="{400+(i-6)*30}" y1="470" x2="{400+(i-6)*170}" y2="800" stroke="{TEAL}" stroke-opacity=".35" stroke-width="3"/>' for i in range(13))}
{"".join(f'<line x1="0" y1="{470+d}" x2="800" y2="{470+d}" stroke="{TEAL}" stroke-opacity=".35" stroke-width="3"/>' for d in [18,45,85,140,215,310])}
{palm(150,520,330,1.3,1)}{palm(660,520,280,1.1,-1)}
<text x="400" y="640" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="300" fill="none" stroke="{PINK}" stroke-width="22" letter-spacing="-10">ZL</text>
<text x="400" y="640" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="300" fill="#ffffff" letter-spacing="-10">ZL</text>
</svg>'''
open("brand/avatar.svg","w").write(av)
# Wordmark logo (transparent) 1600x600
wm=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="560" viewBox="0 0 1600 560">
<defs><linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{YEL}"/><stop offset=".5" stop-color="{ORANGE}"/><stop offset="1" stop-color="{PINK}"/></linearGradient></defs>
{sun(250,260,200,"s2")}{palm(170,470,330,1.3,1)}
<text x="500" y="270" font-family="{FONT}" font-weight="900" font-size="230" fill="url(#tg)" letter-spacing="-6">ZONA</text>
<text x="505" y="470" font-family="{FONT}" font-weight="900" font-size="200" fill="#fff" letter-spacing="2">LEONIDA</text>
<rect x="508" y="500" width="1040" height="12" fill="{TEAL}"/>
</svg>'''
open("brand/logo_wordmark.svg","w").write(wm)
# Banner 2560x1440, safe area 1546x423 centered
W,H=2560,1440
bn=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140a2e"/><stop offset=".45" stop-color="#3b1360"/><stop offset=".62" stop-color="#a0246d"/><stop offset=".72" stop-color="{NAVY}"/></linearGradient>
<linearGradient id="tg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{YEL}"/><stop offset=".5" stop-color="{ORANGE}"/><stop offset="1" stop-color="{PINK}"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{sun(1280,960,380,"s3")}
<rect x="0" y="1010" width="{W}" height="430" fill="{NAVY}"/>
{"".join(f'<line x1="{1280+(i-12)*60}" y1="1010" x2="{1280+(i-12)*300}" y2="1440" stroke="{TEAL}" stroke-opacity=".4" stroke-width="3"/>' for i in range(25))}
{"".join(f'<line x1="0" y1="{1010+d}" x2="{W}" y2="{1010+d}" stroke="{TEAL}" stroke-opacity=".4" stroke-width="3"/>' for d in [20,50,95,160,250,370])}
<path d="M0,1010 L120,960 L180,980 L240,880 L300,890 L330,800 L380,810 L400,720 L450,730 L470,840 L540,850 L560,930 L640,940 L700,1010 Z" fill="#090616"/>
<path d="M{W},1010 L{W-110},950 L{W-170},970 L{W-230},860 L{W-300},870 L{W-320},760 L{W-370},770 L{W-400},900 L{W-470},910 L{W-520},970 L{W-600},1010 Z" fill="#090616"/>
{palm(830,1030,380,1.4,1,"#090616")}{palm(1750,1030,330,1.2,-1,"#090616")}{palm(920,1030,260,1.0,-1,"#090616")}
<text x="1280" y="752" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="210" fill="#000" fill-opacity=".45" letter-spacing="-4">ZONA LEONIDA</text>
<text x="1280" y="742" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="210" fill="url(#tg2)" letter-spacing="-4">ZONA LEONIDA</text>
<rect x="760" y="782" width="1040" height="64" rx="32" fill="{TEAL}"/>
<text x="1280" y="827" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="{NAVY}" letter-spacing="3">GUÍAS · COCHES · SECRETOS · CURIOSIDADES</text>
<text x="1280" y="548" text-anchor="middle" font-family="Inter" font-weight="700" font-size="40" fill="#fff" fill-opacity=".85" letter-spacing="8">TODO SOBRE GTA 6 EN ESPAÑOL</text>
</svg>'''
open("brand/banner.svg","w").write(bn)
for n,w in [("avatar",800),("logo_wordmark",1600),("banner",2560)]:
    subprocess.run(["rsvg-convert","-w",str(w),f"brand/{n}.svg","-o",f"brand/{n}.png"],check=True)
print("ok")
