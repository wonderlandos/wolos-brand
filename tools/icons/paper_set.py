# SPDX-License-Identifier: GPL-2.0-or-later
"""The long tail in the D1 finish, "pressed paper, lit" (LANGUAGE-v2 section 8): places (folders and
the basket), devices and mimetypes. Each is a single OBJECT (a folder, a drive, a page), not a tile:
a +-3.5% lightness ramp with no hue shift, a 6-unit inner highlight at 18%, an ambient shadow (16%)
plus a contact line, and the emblem raised from the surface by one small emboss filter (one unit of
top light, one of bottom shade). One key light above, no gloss, no rim, matte. The finish has two
levels: the same object lit with fewer layers on the small variant."""
import colorsys

from palette import CAT, INK, PAPER
from svgk import mix, rrect, shadow, smooth

# Folder body per place, from the token categories (a calm teal for files; blue for the network)
FOLDER = CAT["files"]["body"]
NET = CAT["web"]["body"]
SYSTEM = CAT["system"]["body"]


def shade(hexc, dl):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(hh, min(1, max(0, ll + dl)), ss)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def emb(cv, sh="#000000"):
    """The emboss: a small drop, a unit of top light on the lower rim, a unit of shade on the upper."""
    def make(i):
        return (f'<filter id="{i}" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1224" height="1224" color-interpolation-filters="sRGB">'
                '<feGaussianBlur in="SourceAlpha" stdDeviation="3" result="sb"/><feOffset in="sb" dy="8" result="so"/>'
                f'<feFlood flood-color="{sh}" flood-opacity=".30"/><feComposite in2="so" operator="in" result="drop"/>'
                '<feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>'
                '<feGaussianBlur in="inv" stdDeviation="2" result="ib"/>'
                '<feOffset in="ib" dy="5" result="il"/><feFlood flood-color="#fff" flood-opacity=".55"/><feComposite in2="il" operator="in"/><feComposite in2="SourceAlpha" operator="in" result="light"/>'
                '<feOffset in="ib" dy="-6" result="id"/><feFlood flood-color="#000" flood-opacity=".28"/><feComposite in2="id" operator="in"/><feComposite in2="SourceAlpha" operator="in" result="dark"/>'
                '<feMerge><feMergeNode in="drop"/><feMergeNode in="SourceGraphic"/><feMergeNode in="light"/><feMergeNode in="dark"/></feMerge></filter>')
    return cv.raw(("emb", sh), make)


def raised(cv, markup, sh="#000000"):
    """The emblem lifted off its surface. The small variant drops the filter (a flat mark reads cleaner at 48)."""
    if cv.small:
        return markup
    return f'<g filter="{emb(cv, sh)}">{markup}</g>'


def pobj(cv, d, base, ramp=.035, hl=.18, ambient=True, contact=True):
    """One lit paper object: ambient shadow, contact line, ramp body, inner highlight. -> markup."""
    dark = shade(base, -.30)
    out = ""
    if ambient:
        out += shadow(cv, d, 20, 30, dark, .16 if not cv.small else .22)
    if contact:
        out += shadow(cv, d, 6, 4, dark, .55)
    out += f'<path d="{d}" fill="{cv.lin([(0, shade(base, ramp)), (1, shade(base, -ramp))])}"/>'
    if hl:
        g = cv.lin([(0, "#fff", hl), (.4, "#fff", .05), (1, "#fff", 0)])
        out += f'<g clip-path="{cv.clip(d)}"><path d="{d}" fill="none" stroke="{g}" stroke-width="6"/></g>'
    return out


# ---- places -------------------------------------------------------------------------------
FRONT = rrect(96, 330, 832, 506, 70)
BACK = ("M96 262Q96 196 162 196H364Q392 196 412 218L450 262H866Q928 262 928 324V700H96Z")


def folder(cv, base=FOLDER, sheet=True):
    back = shade(base, -.07)
    o = pobj(cv, BACK, back, ramp=.02, hl=.10)
    if sheet:
        sh = rrect(160, 268, 700, 300, 26)
        o += f'<path d="{sh}" fill="{cv.lin([(0, "#FFFFFF"), (1, "#E9DFCD")])}"/>'
        o += f'<rect x="160" y="268" width="700" height="4" fill="#fff"/>'
        o += f'<rect x="206" y="312" width="260" height="22" rx="11" fill="#D2A93C" opacity=".85"/>'
        o += f'<rect x="206" y="364" width="560" height="14" rx="7" fill="#B9A98A" opacity=".5"/>'
        o += f'<rect x="206" y="404" width="460" height="14" rx="7" fill="#B9A98A" opacity=".5"/>'
    front = pobj(cv, FRONT, base, ramp=.045, hl=.22, ambient=False)
    # the front plane's shadow falls on the sheet and the back
    o += shadow(cv, FRONT, -6, 10, shade(base, -.35), .45)
    o += front
    # a lip: the front's top edge, a hair lighter, and the hem a hair darker
    o += f'<path d="M166 332H858" stroke="#fff" stroke-opacity=".30" stroke-width="5" stroke-linecap="round"/>'
    cv.add(o)
    cv.begin_glyph()


def e_documents(cv):
    pg = rrect(396, 480, 232, 300, 28)
    return raised(cv, f'<path d="{pg}" fill="{PAPER}"/>' + "".join(
        f'<rect x="{428}" y="{y}" width="{w}" height="22" rx="11" fill="{shade(FOLDER, -.05)}"/>' for y, w in ((530, 168), (580, 168), (630, 168), (680, 110))), "#04302C")


def e_download(cv):
    return raised(cv, f'<path d="M512 468V684M424 606L512 694L600 606" fill="none" stroke="{PAPER}" stroke-width="64" stroke-linecap="round" stroke-linejoin="round"/>'
                      f'<path d="M388 772H636" stroke="{PAPER}" stroke-width="64" stroke-linecap="round"/>', "#04302C")


def e_music(cv):
    return raised(cv, f'<circle cx="512" cy="620" r="168" fill="{PAPER}"/>'
                      f'<circle cx="512" cy="620" r="118" fill="none" stroke="{shade(FOLDER, .08)}" stroke-width="16"/>'
                      f'<circle cx="512" cy="620" r="56" fill="#E9622A"/><circle cx="512" cy="620" r="14" fill="{PAPER}"/>', "#04302C")


def e_pictures(cv):
    fr = rrect(366, 478, 292, 252, 36)
    return raised(cv, f'<path d="{fr}" fill="{PAPER}"/>'
                      f'<path d="M390 706L470 590L528 654L572 600L636 706Z" fill="{shade(FOLDER, -.04)}"/>'
                      f'<circle cx="590" cy="548" r="30" fill="#F2B53A"/>', "#04302C")


def e_publicshare(cv):
    return raised(cv, f'<circle cx="512" cy="560" r="62" fill="{PAPER}"/>'
                      f'<path d="M388 758A124 118 0 0 1 636 758Z" fill="{PAPER}"/>'
                      f'<path d="M352 520A178 178 0 0 1 380 448M672 520A178 178 0 0 0 644 448" fill="none" stroke="{shade(FOLDER, .30)}" stroke-width="30" stroke-linecap="round"/>', "#04302C")


def e_templates(cv):
    return raised(cv, f'<rect x="478" y="470" width="196" height="196" rx="26" fill="{shade(FOLDER, .28)}"/>'
                      f'<rect x="372" y="540" width="196" height="196" rx="26" fill="{PAPER}"/>'
                      f'<rect x="408" y="590" width="124" height="20" rx="10" fill="{shade(FOLDER, -.05)}"/>'
                      f'<rect x="408" y="640" width="90" height="20" rx="10" fill="{shade(FOLDER, -.05)}"/>', "#04302C")


def e_videos(cv):
    return raised(cv, f'<rect x="358" y="486" width="308" height="236" rx="46" fill="{PAPER}"/>'
                      f'<path d="M470 548L572 604L470 660Z" fill="{shade(FOLDER, -.04)}" stroke="{shade(FOLDER, -.04)}" stroke-width="14" stroke-linejoin="round"/>', "#04302C")


def e_desktop(cv):
    return raised(cv, f'<rect x="352" y="478" width="320" height="214" rx="30" fill="{PAPER}"/>'
                      f'<rect x="388" y="512" width="248" height="146" rx="12" fill="{shade(FOLDER, .30)}"/>'
                      f'<path d="M512 692V752M436 756H588" stroke="{PAPER}" stroke-width="40" stroke-linecap="round"/>', "#04302C")


def e_home(cv):
    h = "M512 470L682 626V752H342V626Z"
    kh = "M512 590a26 26 0 0 1 14 48l16 52h-60l16 -52a26 26 0 0 1 14 -48z"
    return raised(cv, f'<path d="{h}" fill="{PAPER}" stroke="{PAPER}" stroke-width="36" stroke-linejoin="round"/>'
                      f'<path d="{kh}" fill="{shade(FOLDER, -.04)}"/>', "#04302C")


def e_globe(cv):
    return raised(cv, f'<circle cx="512" cy="620" r="168" fill="{PAPER}"/>'
                      f'<ellipse cx="512" cy="620" rx="68" ry="168" fill="none" stroke="{shade(NET, -.02)}" stroke-width="22"/>'
                      f'<path d="M344 620H680M366 540H658M366 700H658" stroke="{shade(NET, -.02)}" stroke-width="20" fill="none"/>', "#04223A")


PLACES = [("folder", FOLDER, None), ("folder-documents", FOLDER, e_documents), ("folder-download", FOLDER, e_download),
          ("folder-music", FOLDER, e_music), ("folder-pictures", FOLDER, e_pictures),
          ("folder-publicshare", FOLDER, e_publicshare), ("folder-templates", FOLDER, e_templates),
          ("folder-videos", FOLDER, e_videos), ("user-desktop", FOLDER, e_desktop), ("user-home", FOLDER, e_home),
          ("network-workgroup", NET, e_globe)]


def place(cv, base, emblem):
    folder(cv, base)
    if emblem:
        cv.add(emblem(cv))


def basket(cv, full):
    base = shade(SYSTEM, .16)
    d = "M196 300H828L770 820Q764 868 716 868H308Q260 868 254 820Z"
    o = ""
    if full:
        for pts, fill, dx in (([(250, 310), (264, 196), (352, 150), (440, 178), (452, 270), (430, 312)], PAPER, 0),
                              ([(420, 310), (440, 160), (544, 120), (634, 164), (644, 260), (620, 312)], "#F6D68A", 0),
                              ([(584, 312), (596, 220), (676, 184), (760, 220), (778, 312)], shade(SYSTEM, .32), 0)):
            pd = smooth(pts)
            o += shadow(cv, pd, 8, 5, shade(SYSTEM, -.3), .5) + f'<path d="{pd}" fill="{cv.lin([(0, fill), (1, mix(fill, "#000000", .16))])}"/>'
            o += f'<path d="{pd}" fill="none" stroke="{mix(fill, "#000000", .35)}" stroke-width="5" stroke-linejoin="round" stroke-opacity=".6"/>'
    o += pobj(cv, d, base, ramp=.05, hl=.2)
    clip = cv.clip(d)
    o += f'<g clip-path="{clip}" fill="none" stroke-linecap="round">'
    for i in range(-3, 12):
        x = 140 + i * 80
        o += f'<path d="M{x} 300L{x + 300} 880M{x + 300} 300L{x} 880" stroke="{shade(SYSTEM, .32)}" stroke-width="9" opacity=".75"/>'
    o += '</g>'
    rim = rrect(160, 276, 704, 80, 40)
    o += shadow(cv, rim, 8, 5, shade(SYSTEM, -.3), .5) + f'<path d="{rim}" fill="{PAPER}"/>'
    o += f'<path d="M190 296H834" stroke="#fff" stroke-opacity=".5" stroke-width="5" stroke-linecap="round"/>'
    o += f'<path d="M190 350H834" stroke="{shade(SYSTEM, -.3)}" stroke-opacity=".35" stroke-width="5"/>'
    cv.add(o)
    cv.begin_glyph()


# ---- devices ------------------------------------------------------------------------------
def drive_harddisk(cv):
    base = CAT["dev"]["body"]
    d = rrect(96, 300, 832, 424, 84)
    o = pobj(cv, d, shade(base, .20), ramp=.06, hl=.34)
    o += f'<path d="M156 440H868" stroke="{CAT["dev"]["tint"]}" stroke-width="30" stroke-linecap="round" opacity=".7"/>'
    cv.add(o)
    cv.begin_glyph()
    lab = rrect(168, 546, 420, 100, 42)
    cv.add(raised(cv, f'<path d="{lab}" fill="{PAPER}"/>', "#000000") +
           f'<circle cx="810" cy="596" r="38" fill="{CAT["dev"]["pop"]}" opacity=".5" filter="{cv.blur(14)}"/><circle cx="810" cy="596" r="26" fill="{CAT["dev"]["pop"]}"/>')


def drive_removable(cv):
    base = CAT["dev"]["body"]
    tint = CAT["dev"]["tint"]
    plug = rrect(368, 86, 288, 220, 36)
    o = pobj(cv, plug, shade(tint, .02), ramp=.06, hl=.30, ambient=False)
    o += f'<rect x="424" y="140" width="56" height="56" rx="12" fill="{shade(base, -.1)}"/><rect x="544" y="140" width="56" height="56" rx="12" fill="{shade(base, -.1)}"/>'
    d = rrect(250, 270, 524, 668, 120)
    o += pobj(cv, d, shade(base, .20), ramp=.06, hl=.34)
    cv.add(o)
    cv.begin_glyph()
    lab = rrect(342, 450, 340, 214, 40)
    cv.add(raised(cv, f'<path d="{lab}" fill="{PAPER}"/>'
                      f'<rect x="384" y="500" width="256" height="20" rx="10" fill="{shade(base, .05)}"/>'
                      f'<rect x="384" y="548" width="190" height="20" rx="10" fill="{shade(base, .05)}"/>'
                      f'<rect x="384" y="596" width="224" height="20" rx="10" fill="{shade(base, .05)}"/>') +
           f'<circle cx="512" cy="810" r="30" fill="{CAT["dev"]["pop"]}" opacity=".5" filter="{cv.blur(12)}"/><circle cx="512" cy="810" r="22" fill="{CAT["dev"]["pop"]}"/>')


# ---- mimetypes: the page, a type band in the category hue ---------------------------------
PX0, PY0, PX1, PY1, EAR = 212, 96, 812, 930, 200
PAGE = (f"M{PX0 + EAR} {PY0}H{PX1 - 46}Q{PX1} {PY0} {PX1} {PY0 + 46}V{PY1 - 90}Q{PX1} {PY1} {PX1 - 90} {PY1}"
        f"H{PX0 + 46}Q{PX0} {PY1} {PX0} {PY1 - 46}V{PY0 + EAR}Z")
EAR_D = f"M{PX0 + EAR} {PY0}V{PY0 + EAR - 36}Q{PX0 + EAR} {PY0 + EAR} {PX0 + EAR - 36} {PY0 + EAR}H{PX0}Z"


def page(cv, cat):
    base = CAT[cat]["body"]
    o = pobj(cv, PAGE, PAPER, ramp=.02, hl=.5)
    o += f'<path d="{PAGE}" fill="none" stroke="{shade(PAPER, -.34)}" stroke-opacity=".6" stroke-width="7"/>'
    clip = cv.clip(PAGE)
    o += f'<g clip-path="{clip}"><rect x="{PX0}" y="{PY1 - 170}" width="{PX1 - PX0}" height="190" fill="{cv.lin([(0, shade(base, .03)), (1, shade(base, -.05))])}"/>'
    o += f'<rect x="{PX0}" y="{PY1 - 172}" width="{PX1 - PX0}" height="4" fill="#fff" opacity=".28"/></g>'
    ear = mix(PAPER, INK, .14)
    o += shadow(cv, EAR_D, 6, 6, "#241A3A", .35) + f'<path d="{EAR_D}" fill="{cv.lin([(0, mix(ear, "#FFFFFF", .5)), (1, ear)], 0, 0, 1, 1)}"/>'
    cv.add(o)
    cv.begin_glyph()


def tone(cat):
    from palette import contrast
    b = CAT[cat]["body"]
    return b if contrast(b, PAPER) >= 3.0 else INK


def m_pdf(cv, c):
    t = tone("talk")
    return raised(cv, "".join(f'<path d="{p}" fill="none" stroke="{t}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>'
                              for p in ("M338 366V318H386", "M638 318H686V366", "M686 560V608H638", "M386 608H338V560")) +
                  f'<path d="M388 400H636M388 462H636M388 524H540" stroke="{t}" stroke-width="30" stroke-linecap="round"/>')


def m_exec(cv, c):
    t = tone("dev")
    return raised(cv, f'<path d="M356 372L460 476L356 580" fill="none" stroke="{t}" stroke-width="58" stroke-linecap="round" stroke-linejoin="round"/>'
                      f'<rect x="506" y="528" width="164" height="58" rx="18" fill="{CAT["dev"]["pop"]}"/>')


def m_generic(cv, c):
    t = tone("system")
    return raised(cv, "".join(f'<circle cx="{x}" cy="{y}" r="36" fill="{t}"/>' for x in (368, 512, 656) for y in (352, 484, 616)))


def m_audio(cv, c):
    t = tone("wolos")
    return raised(cv, "".join(f'<path d="M{x} {484 - h / 2}V{484 + h / 2}" stroke="{t}" stroke-width="50" stroke-linecap="round"/>'
                              for x, h in ((344, 100), (428, 230), (512, 330), (596, 200), (680, 90))))


def m_image(cv, c):
    t = tone("media")
    return raised(cv, f'<rect x="326" y="310" width="372" height="326" rx="38" fill="{CAT["media"]["tint"]}"/>'
                      f'<path d="M326 636L440 478L526 568L578 506L698 636Z" fill="{t}"/>'
                      f'<circle cx="610" cy="394" r="42" fill="{CAT["media"]["pop"]}"/>')


def m_package(cv, c):
    t = tone("store")
    return raised(cv, f'<rect x="318" y="372" width="388" height="290" rx="36" fill="{CAT["store"]["tint"]}" stroke="{t}" stroke-width="40"/>'
                      f'<path d="M318 470H706" stroke="{t}" stroke-width="40"/>'
                      f'<rect x="476" y="344" width="72" height="170" rx="14" fill="{CAT["store"]["pop"]}"/>')


def m_text(cv, c):
    t = tone("files")
    return raised(cv, f'<path d="M326 330H698M326 420H698M326 510H640M326 600H698M326 690H530" stroke="{t}" stroke-width="44" stroke-linecap="round"/>')


def m_video(cv, c):
    t = tone("web")
    return raised(cv, f'<rect x="322" y="318" width="380" height="316" rx="54" fill="{t}"/>'
                      f'<path d="M458 400L588 476L458 552Z" fill="{PAPER}" stroke="{PAPER}" stroke-width="18" stroke-linejoin="round"/>')


def m_document(cv, c):
    t = tone("web")
    return raised(cv, f'<path d="M326 340H500" stroke="{t}" stroke-width="58" stroke-linecap="round"/>'
                      f'<path d="M326 450H698M326 540H698M326 630H600" stroke="{t}" stroke-width="40" stroke-linecap="round"/>')


def m_spreadsheet(cv, c):
    t = tone("files")
    return raised(cv, f'<rect x="318" y="316" width="388" height="340" rx="34" fill="{CAT["files"]["tint"]}"/>'
                      f'<rect x="318" y="316" width="388" height="86" rx="34" fill="{t}"/>'
                      f'<path d="M447 402V656M577 402V656M318 486H706M318 570H706" stroke="{t}" stroke-width="26"/>'
                      f'<rect x="318" y="316" width="388" height="340" rx="34" fill="none" stroke="{t}" stroke-width="40"/>')


def m_presentation(cv, c):
    t = tone("media")
    return raised(cv, f'<rect x="304" y="304" width="416" height="268" rx="40" fill="{t}"/>'
                      f'<path d="M388 508V440M472 508V380M556 508V420M640 508V350" stroke="{PAPER}" stroke-width="40" stroke-linecap="round"/>'
                      f'<path d="M512 572V650M420 700L512 622L604 700" fill="none" stroke="{t}" stroke-width="40" stroke-linecap="round" stroke-linejoin="round"/>')


MIMES = [("application-pdf", "talk", m_pdf), ("application-x-executable", "dev", m_exec),
         ("application-x-generic", "system", m_generic), ("audio-x-generic", "wolos", m_audio),
         ("image-x-generic", "media", m_image), ("package-x-generic", "store", m_package),
         ("text-x-generic", "files", m_text), ("video-x-generic", "web", m_video),
         ("x-office-document", "web", m_document), ("x-office-presentation", "media", m_presentation),
         ("x-office-spreadsheet", "files", m_spreadsheet)]


def mime(cv, cat, glyph):
    page(cv, cat)
    cv.add(glyph(cv, CAT[cat]))
