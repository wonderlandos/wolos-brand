# SPDX-License-Identifier: GPL-2.0-or-later
import math, os, json
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for s in ["brand","tokens","icons/apps","icons/symbolic","wallpapers","cursors"]:
    os.makedirs(f"{D}/{s}", exist_ok=True)

def w(p, s):
    with open(f"{D}/{p}", "w") as f: f.write(s.strip()+"\n")

ACCENT = "#7C5CFF"   # looking-glass violet
ACCENT_D = "#9B85FF"

# ---------- squircle (superellipse n=5), body 824 at 100 ----------
def squircle(cx=512, cy=512, r=412, n=5, steps=96):
    pts = []
    for i in range(steps):
        t = 2*math.pi*i/steps
        c, s = math.cos(t), math.sin(t)
        x = cx + r*math.copysign(abs(c)**(2/n), c)
        y = cy + r*math.copysign(abs(s)**(2/n), s)
        pts.append(f"{x:.1f},{y:.1f}")
    return "M" + " L".join(pts) + " Z"
SQ = squircle()

# No SVG filters (GTK, Qt, Firefox clip the filter region into a grey box). Depth is baked:
# black copies of the shape, offset down, translucent.
import re
def shadow(shape, layers):
    black = re.sub(r'(fill|stroke)="(?!none)[^"]*"', r'\1="#000"', shape)
    black = re.sub(r'\s(fill|stroke)-opacity="[^"]*"', '', black)
    return "".join(f'<g transform="translate(0 {dy})" fill="#000" opacity="{o}">{black}</g>' for dy, o in layers)

def app(name, g1, g2, body, extra_defs=""):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>
<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="sq"><path d="{SQ}"/></clipPath>
{extra_defs}
</defs>
{shadow(f'<path d="{SQ}"/>', ((16, .06), (10, .08), (5, .10)))}<path d="{SQ}" fill="url(#bg)"/>
<g clip-path="url(#sq)">{shadow(body, ((10, .07), (5, .10)))}{body}</g>
<path d="{SQ}" fill="url(#gloss)"/>
<path d="{SQ}" fill="none" stroke="#000" stroke-opacity=".08" stroke-width="2"/>
</svg>'''
    w(f"icons/apps/wolos-{name}.svg", svg)

W = "#ffffff"
apps = {
"files": ("#5AC8FA","#1E7BE6", f'''<path d="M232 330 q0-30 30-30 h170 l50 50 h280 q30 0 30 30 v330 q0 30-30 30 H262 q-30 0-30-30Z" fill="#cfe9ff"/>
<path d="M232 400 q0-30 30-30 h500 q30 0 30 30 v290 q0 30-30 30 H262 q-30 0-30-30Z" fill="{W}"/>
<rect x="432" y="430" width="160" height="26" rx="13" fill="#1E7BE6" fill-opacity=".35"/>'''),
"terminal": ("#3A3A42","#121216", f'''<rect x="212" y="262" width="600" height="500" rx="44" fill="#000" fill-opacity=".55" stroke="#fff" stroke-opacity=".15" stroke-width="4"/>
<path d="M300 400 l90 80 -90 80" fill="none" stroke="#3CE37A" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="430" y="540" width="180" height="34" rx="17" fill="{W}" fill-opacity=".9"/>'''),
"browser": ("#62D0FF","#2463EB", f'''<circle cx="512" cy="512" r="290" fill="{W}"/>
<circle cx="512" cy="512" r="250" fill="none" stroke="#2463EB" stroke-opacity=".18" stroke-width="6"/>
<path d="M512 262 v28 M512 734 v28 M262 512 h28 M734 512 h28" stroke="#2463EB" stroke-opacity=".4" stroke-width="10" stroke-linecap="round"/>
<path d="M512 512 L652 372 L560 560 Z" fill="#FF3B30"/><path d="M512 512 L372 652 L464 464 Z" fill="#9aa4b8"/><circle cx="512" cy="512" r="18" fill="{W}"/>'''),
"settings": ("#B9BEC7","#6E7480", f'''<g transform="translate(512 512)"><g fill="#3E434C">{''.join(f'<rect x="-34" y="-300" width="68" height="110" rx="18" transform="rotate({a})"/>' for a in range(0,360,30))}</g>
<circle r="230" fill="#3E434C"/><circle r="170" fill="#D7DAE0"/><circle r="90" fill="#3E434C"/><circle r="50" fill="#9aa0aa"/></g>'''),
"software": ("#5AB8FF","#1658E8", f'''<g fill="none" stroke="{W}" stroke-width="56" stroke-linecap="round"><path d="M420 300 L300 720"/><path d="M604 300 L724 720"/><path d="M290 610 H560"/><path d="M640 610 H740"/></g>'''),
"music": ("#FF6A88","#E8204E", f'''<path d="M440 330 L690 280 V640" fill="none" stroke="{W}" stroke-width="44" stroke-linejoin="round"/><path d="M440 330 V700" stroke="{W}" stroke-width="44"/>
<ellipse cx="380" cy="705" rx="80" ry="62" fill="{W}"/><ellipse cx="630" cy="645" rx="80" ry="62" fill="{W}"/>'''),
"photos": ("#FFFFFF","#EEF0F4", '<g transform="translate(512 512)">'+''.join(f'<ellipse rx="92" ry="190" cy="-150" fill="{c}" fill-opacity=".82" transform="rotate({i*45})"/>' for i,c in enumerate(["#FF9500","#FFCC00","#9BE15D","#34C759","#32ADE6","#5856D6","#AF52DE","#FF3B30"]))+'</g>'),
"notes": ("#FFE38A","#FFC93C", f'''<rect x="100" y="100" width="824" height="170" fill="#F7B500"/><rect x="100" y="250" width="824" height="700" fill="#FFFBEA"/>
<g stroke="#D9D2B8" stroke-width="8">{''.join(f'<path d="M230 {y} H794"/>' for y in range(380,800,90))}</g>
<path d="M230 380 H620 M230 470 H700 M230 560 H560" stroke="#6b5f3a" stroke-width="14" stroke-linecap="round" stroke-opacity=".55"/>'''),
"calendar": ("#FFFFFF","#F2F2F5", f'''<rect x="100" y="100" width="824" height="230" fill="#FF3B30"/>
<text x="512" y="270" font-family="Inter, sans-serif" font-weight="700" font-size="120" text-anchor="middle" fill="{W}">OCT</text>
<text x="512" y="760" font-family="Inter, sans-serif" font-weight="300" font-size="400" text-anchor="middle" fill="#1c1c1e">26</text>'''),
"mail": ("#6AC8FF","#1A73F0", f'''<rect x="232" y="322" width="560" height="380" rx="40" fill="{W}"/><path d="M252 352 L512 552 L772 352" fill="none" stroke="#1A73F0" stroke-opacity=".55" stroke-width="26" stroke-linejoin="round"/>'''),
"calculator": ("#4A4A50","#1E1E22", ''.join(f'<circle cx="{332+x*180}" cy="{332+y*180}" r="72" fill="{"#FF9F0A" if x==2 else ("#A5A5AA" if y==0 else "#5A5A60")}"/>' for x in range(3) for y in range(3))+f'<path d="M692 312 v40 M672 332 h40 M672 512 h40 M672 692 h40 M672 676 h40" stroke="{W}" stroke-width="12" stroke-linecap="round"/>'),
"games": ("#2B3B5C","#0E1628", f'''<path d="M300 420 q-100 0-120 140 l-20 140 q-6 70 60 70 q40 0 80-60 l40-60 h344 l40 60 q40 60 80 60 q66 0 60-70 l-20-140 q-20-140-120-140Z" fill="#E9EEF7"/>
<path d="M330 500 v120 M270 560 h120" stroke="#2B3B5C" stroke-width="34" stroke-linecap="round"/><circle cx="680" cy="520" r="28" fill="#FF375F"/><circle cx="740" cy="590" r="28" fill="#30D158"/><circle cx="620" cy="590" r="28" fill="#0A84FF"/>'''),
"text-editor": ("#FFFFFF","#E9EBF0", f'''<rect x="262" y="212" width="500" height="600" rx="36" fill="{W}" stroke="#d5d8e0" stroke-width="6"/>
<path d="M332 330 H690 M332 410 H650 M332 490 H690 M332 570 H560" stroke="#8a90a0" stroke-width="22" stroke-linecap="round"/>
<path d="M600 760 L800 560 l60 60 -200 200 -80 20Z" fill="{ACCENT}"/>'''),
"system-monitor": ("#2E2E36","#101014", f'''<rect x="212" y="262" width="600" height="500" rx="40" fill="#000" fill-opacity=".5"/>
<g stroke="#fff" stroke-opacity=".1" stroke-width="4">{''.join(f'<path d="M212 {y} H812"/>' for y in range(362,762,100))}</g>
<path d="M232 620 L340 560 L420 600 L500 420 L580 520 L660 360 L792 460" fill="none" stroke="#30D158" stroke-width="22" stroke-linejoin="round" stroke-linecap="round"/>'''),
"trash": ("#E7E9EE","#BFC3CC", f'''<path d="M322 352 h380 l-30 410 q-4 40-44 40 H396 q-40 0-44-40Z" fill="#F8F9FB" stroke="#9aa0ab" stroke-width="10"/>
<rect x="292" y="300" width="440" height="60" rx="20" fill="#9aa0ab"/>
<path d="M432 430 V720 M512 430 V720 M592 430 V720" stroke="#9aa0ab" stroke-width="16" stroke-linecap="round"/>'''),
"launcher": ("#9B85FF","#5B3BE8", f'''<circle cx="470" cy="470" r="150" fill="none" stroke="{W}" stroke-width="54"/><path d="M582 582 L730 730" stroke="{W}" stroke-width="64" stroke-linecap="round"/>'''),
}
for n,(a,b,body) in apps.items(): app(n,a,b,body)

# ---------- brand ----------
# mark: keyhole whose top is a looking-glass oval with two rabbit ears
MARK_PATH = "M44 8 C44 2 52 2 52 10 L50 22 M20 8 C20 2 12 2 12 10 L14 22"
def mark(size_box=64):
    return '''<g>
<path d="M22 22 C17 14 16 4 21 3 C26 2 28 12 28 21Z M42 22 C47 14 48 4 43 3 C38 2 36 12 36 21Z" fill="url(#mg)"/>
<circle cx="32" cy="33" r="15" fill="url(#mg)"/>
<path d="M27 40 L24 60 H40 L37 40Z" fill="url(#mg)"/>
<circle cx="32" cy="32" r="6" fill="#fff"/><path d="M29.5 35 L28 46 H36 L34.5 35Z" fill="#fff"/>
</g>'''
MG = f'<linearGradient id="mg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B49CFF"/><stop offset="1" stop-color="#5B3BE8"/></linearGradient>'
w("brand/wolos-mark.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64"><defs>{MG}</defs>{mark()}</svg>')
# symbolic menubar glyph (monochrome, 16px)
GLYPH = '<path fill="currentColor" fill-rule="evenodd" d="M5.4 5.6C4.2 3.8 4 1 5.3.7 6.6.4 7.1 3 7.1 5.2ZM10.6 5.6c1.2-1.8 1.4-4.6.1-4.9C9.4.4 8.9 3 8.9 5.2ZM8 4.4a4 4 0 0 1 1.6 7.7L10.3 15.5H5.7L6.4 12.1A4 4 0 0 1 8 4.4ZM8 6.9a1.4 1.4 0 0 0-.7 2.6L6.9 12.6H9.1L8.7 9.5A1.4 1.4 0 0 0 8 6.9Z"/>'
w("brand/wolos-glyph-symbolic.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" style="color:#2e3436">{GLYPH}</svg>')
def wordmark(fill, fname):
    w(fname, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 96" width="360" height="96"><defs>{MG}</defs>
<g transform="translate(8 16)">{mark()}</g>
<text x="92" y="66" font-family="Inter, 'SF Pro Display', 'Helvetica Neue', sans-serif" font-size="56" font-weight="600" letter-spacing="-1.5" fill="{fill}">Wol<tspan fill="url(#mg)" font-weight="700">OS</tspan></text></svg>''')
wordmark("#1C1C1E", "brand/wolos-wordmark.svg")
wordmark("#F5F5F7", "brand/wolos-wordmark-dark.svg")
w("brand/wolos-boot.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080"><defs>
<linearGradient id="mg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#D9D0FF"/></linearGradient></defs>
<rect width="1920" height="1080" fill="#000"/>
<g transform="translate(864 360) scale(3)">{mark().replace('fill="#fff"','fill="#000"')}</g>
<rect x="810" y="720" width="300" height="6" rx="3" fill="#fff" fill-opacity=".22"/><rect x="810" y="720" width="110" height="6" rx="3" fill="#fff"/>
</svg>''')

# ---------- symbolic icons (16px, Adwaita-style currentColor) ----------
def sym(name, body):
    w(f"icons/symbolic/{name}.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><g fill="#2e3436">{body}</g></svg>')
ARC = lambda r: f'M{8-r*0.866:.2f} {12-r*0.5:.2f}A{r} {r} 0 0 1 {8+r*0.866:.2f} {12-r*0.5:.2f}'
def wifi(level):
    parts = ['<circle cx="8" cy="12.5" r="1.5"/>']
    for i,r in enumerate([4.5,7.5,10.5]):
        op = 1 if i < level else .3
        parts.append(f'<path d="{ARC(r)}" fill="none" stroke="#2e3436" stroke-width="2" stroke-linecap="round" opacity="{op}"/>')
    return ''.join(parts)
sym("network-wireless-signal-weak-symbolic", wifi(1))
sym("network-wireless-signal-good-symbolic", wifi(2))
sym("network-wireless-signal-excellent-symbolic", wifi(3))
sym("network-wireless-offline-symbolic", wifi(0)+'<path d="M2 2 L14 14" stroke="#2e3436" stroke-width="2" stroke-linecap="round"/>')
def batt(frac, charging=False):
    s = '<path fill-rule="evenodd" d="M2.5 4h9A1.5 1.5 0 0 1 13 5.5v5A1.5 1.5 0 0 1 11.5 12h-9A1.5 1.5 0 0 1 1 10.5v-5A1.5 1.5 0 0 1 2.5 4Zm0 1a.5.5 0 0 0-.5.5v5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-5a.5.5 0 0 0-.5-.5Z"/><rect x="14" y="6.5" width="1.2" height="3" rx=".5"/>'
    if frac: s += f'<rect x="3" y="6" width="{8*frac:.2f}" height="4" rx=".5" fill="{"#e01b24" if frac<=.15 else "#2e3436"}"/>'
    if charging: s += '<path d="M7.8 3.2 4.8 8.4h2.3L6.4 12.8 9.6 7.4H7.3Z" fill="#2e3436" stroke="#fff" stroke-width=".8"/>'
    return s
for n,f in [("empty",0),("caution",.12),("low",.3),("good",.65),("full",1)]:
    sym(f"battery-{n}-symbolic", batt(f))
    sym(f"battery-{n}-charging-symbolic", batt(f, True))
SPK = '<path d="M1.5 5.5h2.5L7.5 2.5v11L4 10.5H1.5Z"/>'
def vol(level):
    s = SPK
    for i,r in enumerate([2.5,4.5,6.5]):
        op = 1 if i < level else .3
        s += f'<path d="M{8.5+r*0.0:.1f} {8-r:.1f}A{r} {r} 0 0 1 {8.5:.1f} {8+r:.1f}" transform="translate(1 0)" fill="none" stroke="#2e3436" stroke-width="1.5" stroke-linecap="round" opacity="{op}"/>'
    return s
sym("audio-volume-low-symbolic", vol(1)); sym("audio-volume-medium-symbolic", vol(2)); sym("audio-volume-high-symbolic", vol(3))
sym("audio-volume-muted-symbolic", SPK+'<path d="M10 5.5l4 5m0-5-4 5" stroke="#2e3436" stroke-width="1.5" stroke-linecap="round"/>')
sym("bluetooth-active-symbolic", '<path d="M4 4.5 11 11 7.5 14V2L11 5 4 11.5" fill="none" stroke="#2e3436" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>')
sym("bluetooth-disabled-symbolic", '<path d="M4 4.5 11 11 7.5 14V2L11 5 4 11.5" fill="none" stroke="#2e3436" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" opacity=".35"/><path d="M2 2 14 14" stroke="#2e3436" stroke-width="1.5" stroke-linecap="round"/>')
sym("wolos-control-center-symbolic", '<rect x="1" y="2.5" width="14" height="4.5" rx="2.25" fill="none" stroke="#2e3436" stroke-width="1.2"/><circle cx="12.75" cy="4.75" r="1.6"/><rect x="1" y="9" width="14" height="4.5" rx="2.25" fill="none" stroke="#2e3436" stroke-width="1.2"/><circle cx="3.25" cy="11.25" r="1.6"/>')
sym("preferences-system-notifications-symbolic", '<path d="M8 1.5a4 4 0 0 0-4 4V9L2.5 11.5h11L12 9V5.5a4 4 0 0 0-4-4Z"/><path d="M6.3 13a1.8 1.8 0 0 0 3.4 0Z"/>')
sym("system-search-symbolic", '<circle cx="6.5" cy="6.5" r="4.5" fill="none" stroke="#2e3436" stroke-width="2"/><path d="M10 10 14.5 14.5" stroke="#2e3436" stroke-width="2.2" stroke-linecap="round"/>')
sym("system-shutdown-symbolic", '<path d="M4.5 4A6 6 0 1 0 11.5 4" fill="none" stroke="#2e3436" stroke-width="1.8" stroke-linecap="round"/><path d="M8 1.5V8" stroke="#2e3436" stroke-width="1.8" stroke-linecap="round"/>')
sym("preferences-system-time-symbolic", '<circle cx="8" cy="8" r="6.3" fill="none" stroke="#2e3436" stroke-width="1.5"/><path d="M8 4.2V8l2.6 1.8" fill="none" stroke="#2e3436" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
sym("wolos-logo-symbolic", GLYPH.replace('fill="currentColor" ',''))

# ---------- wallpapers ----------
def wall(name, bg, blobs, extra=""):
    defs = ''.join(f'<radialGradient id="b{i}"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>' for i,(c,o,*_) in enumerate(blobs))
    shapes = ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#b{i})" transform="rotate({rot} {x} {y})"/>' for i,(c,o,x,y,rx,ry,rot) in enumerate(blobs))
    w(f"wallpapers/{name}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3840 2160" width="3840" height="2160" preserveAspectRatio="xMidYMid slice"><defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o,c in bg)}</linearGradient>{defs}
<filter id="soft"><feGaussianBlur stdDeviation="40"/></filter></defs>
<rect width="3840" height="2160" fill="url(#bg)"/>{shapes}{extra}</svg>''')
wave = lambda c,o,y: f'<path d="M-300 {y} C900 {y-380} 1700 {y+260} 2500 {y-120} S3500 {y-420} 3840 {y-200} L4140 {y-200} V2400 H-300Z" fill="{c}" fill-opacity="{o}" filter="url(#soft)"/>'
wall("wonderland-day", [(0,"#F6F1FF"),(.55,"#E3ECFF"),(1,"#FFE9F1")],
     [("#B49CFF",.75,900,700,1300,900,-20),("#7FD4FF",.6,2900,600,1200,800,15),("#FFB3C8",.65,2400,1700,1400,800,-10),("#FFE08A",.5,700,1800,900,600,0)],
     wave("#ffffff",.45,1500)+wave("#C9B8FF",.25,1850))
wall("wonderland-night", [(0,"#0B0A1A"),(.6,"#17123A"),(1,"#2A0F3A")],
     [("#5B3BE8",.8,1000,800,1400,900,-20),("#1E7BE6",.5,3000,500,1100,700,15),("#C2307A",.55,2500,1700,1400,800,-10),("#7C5CFF",.4,500,1900,900,600,0)],
     wave("#9B85FF",.18,1550)+wave("#000000",.35,1900)+''.join(f'<circle cx="{(i*977)%3840}" cy="{(i*613)%1300}" r="{3+i%4}" fill="#fff" fill-opacity="{.25+(i%5)*.12:.2f}"/>' for i in range(1,70)))
wall("wonderland-dusk", [(0,"#FFD6C2"),(.5,"#C7A6F0"),(1,"#3B2A78")],
     [("#FF8FA3",.6,1100,600,1300,800,-15),("#FFC96B",.55,2900,500,1100,700,10),("#5B3BE8",.6,2200,1800,1600,800,0)],
     wave("#ffffff",.2,1450)+wave("#2A1F5E",.4,1850))

# ---------- tokens ----------
tok = {
 "accent": {"light": ACCENT, "dark": ACCENT_D},
 "light": {"bg":"#F5F5F7","surface":"#FFFFFF","surface-2":"#ECECEF","menubar":"rgba(246,246,248,0.72)","dock":"rgba(255,255,255,0.55)","border":"rgba(0,0,0,0.10)","text":"#1C1C1E","text-2":"#6E6E73","shadow":"rgba(0,0,0,0.18)","red":"#FF3B30","orange":"#FF9500","yellow":"#FFCC00","green":"#34C759","blue":"#007AFF","accent":ACCENT,"accent-fg":"#FFFFFF","selection":"rgba(124,92,255,0.22)"},
 "dark": {"bg":"#1C1C1E","surface":"#2C2C2E","surface-2":"#3A3A3C","menubar":"rgba(28,28,30,0.62)","dock":"rgba(40,40,44,0.50)","border":"rgba(255,255,255,0.10)","text":"#F5F5F7","text-2":"#A1A1A6","shadow":"rgba(0,0,0,0.45)","red":"#FF453A","orange":"#FF9F0A","yellow":"#FFD60A","green":"#30D158","blue":"#0A84FF","accent":ACCENT_D,"accent-fg":"#FFFFFF","selection":"rgba(155,133,255,0.30)"},
 "radius": {"sm":"6px","md":"10px","lg":"14px","window":"12px","dock":"18px","icon":"22.5%"},
 "blur": {"menubar":"20px","dock":"24px","popover":"30px","hyprland_size":8,"hyprland_passes":3},
 "font": {"ui":"Inter","ui-fallback":["Inter","Cantarell","Noto Sans","DejaVu Sans","sans-serif"],"mono":"JetBrains Mono","mono-fallback":["JetBrains Mono","Fira Code","DejaVu Sans Mono","monospace"],"size":"13px","size-menubar":"13px","ports":["x11-fonts/inter","x11-fonts/jetbrains-mono","x11-fonts/noto-basic"]},
 "wallpaper": {"light":"wonderland-day.svg","dark":"wonderland-night.svg"},
}
w("tokens/colors.json", json.dumps(tok, indent=2))
css = ["/* WolOS design tokens. Generated alongside colors.json/colors.sh; keep in sync. */", ":root {"]
def cssblock(p):
    return [f"  --wol-{k}: {v};" for k,v in tok[p].items()]
css += cssblock("light")
css += [f"  --wol-radius-{k}: {v};" for k,v in tok["radius"].items()]
css += [f"  --wol-blur-{k}: {v};" for k,v in tok["blur"].items() if str(v).endswith("px")]
css += [f'  --wol-font-ui: {", ".join(repr(f).replace(chr(39),chr(34)) if " " in f else f for f in tok["font"]["ui-fallback"])};',
        f'  --wol-font-mono: {", ".join(repr(f).replace(chr(39),chr(34)) if " " in f else f for f in tok["font"]["mono-fallback"])};',
        f'  --wol-font-size: {tok["font"]["size"]};', "}",
        "@media (prefers-color-scheme: dark) {", "  :root {"] + ["  "+l for l in cssblock("dark")] + ["  }", "}",
        '[data-theme="dark"] {'] + cssblock("dark") + ["}"]
w("tokens/colors.css", "\n".join(css))
sh = ["# WolOS design tokens (POSIX sh). Usage: . /usr/local/share/wolos/tokens/colors.sh", ": \"${WOL_THEME:=light}\""]
for p in ("light","dark"):
    for k,v in tok[p].items(): sh.append(f'WOL_{p.upper()}_{k.upper().replace("-","_")}=\'{v}\'')
sh += ['if [ "$WOL_THEME" = dark ]; then _p=DARK; else _p=LIGHT; fi']
for k in tok["light"]:
    K=k.upper().replace("-","_"); sh.append(f'eval "WOL_{K}=\\${{WOL_${{_p}}_{K}}}"')
sh += [f"WOL_RADIUS_{k.upper()}='{v}'" for k,v in tok["radius"].items()]
sh += [f"WOL_BLUR_{k.upper()}='{v}'" for k,v in tok["blur"].items()]
sh += [f"WOL_FONT_UI='{tok['font']['ui']}'", f"WOL_FONT_MONO='{tok['font']['mono']}'", "unset _p"]
w("tokens/colors.sh", "\n".join(sh))

# ---------- icon theme ----------
w("icons/index.theme", """[Icon Theme]
Name=WolOS
Comment=WolOS (Wonderland OS) icon theme
Inherits=Adwaita,hicolor
Directories=scalable/apps,scalable/places,symbolic/status,symbolic/actions

[scalable/apps]
Size=128
MinSize=16
MaxSize=1024
Context=Applications
Type=Scalable

[scalable/places]
Size=128
MinSize=16
MaxSize=1024
Context=Places
Type=Scalable

[symbolic/status]
Size=16
MinSize=16
MaxSize=512
Context=Status
Type=Scalable

[symbolic/actions]
Size=16
MinSize=16
MaxSize=512
Context=Actions
Type=Scalable
""")
aliases = {
 "files": ["org.gnome.Nautilus","system-file-manager","thunar","org.xfce.thunar","pcmanfm","nemo"],
 "terminal": ["utilities-terminal","org.gnome.Terminal","foot","kitty","Alacritty","org.wezfurlong.wezterm","xfce4-terminal"],
 "browser": ["firefox","web-browser","org.mozilla.firefox","chromium","librewolf","epiphany"],
 "settings": ["preferences-system","org.gnome.Settings","gnome-control-center","nwg-look"],
 "software": ["system-software-install","org.gnome.Software","octopkg"],
 "music": ["multimedia-audio-player","org.gnome.Music","audacious","rhythmbox","elisa"],
 "photos": ["multimedia-photo-viewer","org.gnome.eog","org.gnome.Loupe","org.gnome.Shotwell","ristretto"],
 "notes": ["accessories-notes","org.gnome.gitlab.cheywood.Iotas","xpad"],
 "calendar": ["office-calendar","org.gnome.Calendar"],
 "mail": ["internet-mail","mail-client","thunderbird","org.mozilla.Thunderbird","evolution"],
 "calculator": ["accessories-calculator","org.gnome.Calculator","galculator","qalculate-gtk"],
 "games": ["steam","applications-games","lutris"],
 "text-editor": ["accessories-text-editor","org.gnome.TextEditor","org.gnome.gedit","mousepad","code","codium"],
 "system-monitor": ["utilities-system-monitor","org.gnome.SystemMonitor","htop","btop"],
 "trash": ["user-trash","user-trash-full"],
 "launcher": ["system-search","fuzzel","org.gnome.Settings-search-symbolic-x"][:2],
}
w("icons/aliases.tsv", "# wolos-<icon>\\tfreedesktop/app icon names (tab-separated). install.sh symlinks these.\n" +
  "\n".join(f"{k}\t{' '.join(v)}" for k,v in aliases.items()))
w("icons/install.sh", r'''#!/bin/sh
# Install WolOS icon theme. Usage: install.sh [DESTDIR] (default /usr/local/share/icons/WolOS)
set -eu
src=$(cd "$(dirname "$0")" && pwd)
dst=${1:-/usr/local/share/icons/WolOS}
mkdir -p "$dst/scalable/apps" "$dst/scalable/places" "$dst/symbolic/status" "$dst/symbolic/actions"
cp "$src/index.theme" "$dst/"
cp "$src"/apps/*.svg "$dst/scalable/apps/"
cp "$src"/symbolic/*.svg "$dst/symbolic/status/"
grep -v '^#' "$src/aliases.tsv" | while IFS="$(printf '\t')" read -r base names; do
  for n in $names; do
    case $n in user-trash*) d=places ;; *) d=apps ;; esac
    ln -sf "../apps/wolos-$base.svg" "$dst/scalable/$d/$n.svg"
  done
done
for n in system-search-symbolic system-shutdown-symbolic; do
  ln -sf "../status/$n.svg" "$dst/symbolic/actions/$n.svg"
done
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$dst" || true
''')
os.chmod(f"{D}/icons/install.sh", 0o755)
