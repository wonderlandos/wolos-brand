# SPDX-License-Identifier: GPL-2.0-or-later
"""More of the long tail in the D1 finish, "pressed paper, lit" (design/icons/LANGUAGE.md): the
devices GIO names for what people plug in (computer, disc, memory card, phone, camera, printer) and
the mimetype generics shared-mime-info falls back to that the first set lacked. Same objects and
helpers as paper_set.py: one lit object, a +-3.5% ramp, a 6-unit inner highlight, an ambient shadow
plus a contact line, the emblem raised by one emboss filter on the full variant only."""
from palette import CAT, PAPER
from paper_set import pobj, raised, shade, page, tone
from svgk import circ, rrect

DEV = CAT["dev"]["body"]
TINT = CAT["dev"]["tint"]
POP = CAT["dev"]["pop"]
SLAB = shade(DEV, .20)          # the device body tone of drive-harddisk / drive-removable-media


def led(cv, x, y, r=22, c=POP):
    """A lit indicator: a soft bloom (filtered) over a sharp dot (the dot alone reads the same)."""
    return (f'<circle cx="{x}" cy="{y}" r="{r * 1.6:.0f}" fill="{c}" opacity=".5" filter="{cv.blur(r * .5)}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')


# ---- devices ------------------------------------------------------------------------------
def computer(cv):
    """A display on a foot: the slab is the bezel, the emblem the lit screen."""
    stand = "M440 744H584L612 860H412Z"
    foot = rrect(330, 846, 364, 54, 26)
    o = pobj(cv, foot, shade(TINT, -.10), ramp=.05, hl=.30)
    o += pobj(cv, stand, shade(TINT, -.18), ramp=.05, hl=.0, ambient=False)
    body = rrect(110, 170, 804, 590, 70)
    o += pobj(cv, body, SLAB, ramp=.06, hl=.34)
    cv.add(o)
    cv.begin_glyph()
    scr = rrect(168, 226, 688, 476, 34)
    cv.add(raised(cv, f'<path d="{scr}" fill="{cv.lin([(0, shade(TINT, .12)), (1, shade(TINT, -.08))])}"/>'
                      f'<rect x="168" y="226" width="688" height="70" rx="34" fill="{PAPER}" opacity=".9"/>'
                      f'<rect x="216" y="352" width="300" height="300" rx="28" fill="{PAPER}"/>'
                      f'<rect x="556" y="352" width="252" height="132" rx="24" fill="{PAPER}" opacity=".75"/>'
                      f'<rect x="556" y="520" width="252" height="132" rx="24" fill="{CAT["wolos"]["body"]}"/>', "#000000"))


def drive_optical(cv):
    """A disc: pressed paper with a mirror band, the hub the emblem."""
    d = circ(512, 512, 400)
    o = pobj(cv, d, shade(TINT, .16), ramp=.05, hl=.40)
    o += (f'<circle cx="512" cy="512" r="330" fill="none" stroke="{shade(TINT, .26)}" stroke-width="40" opacity=".8"/>'
          f'<path d="M260 300A330 330 0 0 1 512 182" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="40" stroke-linecap="round"/>'
          f'<path d="M760 720A330 330 0 0 1 600 830" fill="none" stroke="{CAT["wolos"]["tint"]}" stroke-width="40" stroke-linecap="round"/>')
    cv.add(o)
    cv.begin_glyph()
    cv.add(raised(cv, f'<circle cx="512" cy="512" r="150" fill="{PAPER}"/>'
                      f'<circle cx="512" cy="512" r="150" fill="none" stroke="{shade(TINT, -.18)}" stroke-width="16"/>'
                      f'<circle cx="512" cy="512" r="64" fill="{shade(DEV, .10)}"/>', "#000000"))


def media_flash(cv):
    """A memory card: the slab with the cut corner and gold contacts, the label the emblem."""
    d = "M318 110H770Q850 110 850 190V830Q850 910 770 910H254Q174 910 174 830V280Z"
    o = pobj(cv, d, SLAB, ramp=.06, hl=.34)
    for i in range(5):
        o += f'<rect x="{360 + i * 84}" y="150" width="50" height="128" rx="14" fill="{CAT["store"]["body"]}"/>'
        o += f'<rect x="{360 + i * 84}" y="150" width="50" height="16" rx="8" fill="#fff" opacity=".45"/>'
    cv.add(o)
    cv.begin_glyph()
    lab = rrect(254, 380, 516, 420, 44)
    cv.add(raised(cv, f'<path d="{lab}" fill="{PAPER}"/>'
                      f'<rect x="306" y="440" width="300" height="34" rx="17" fill="{CAT["wolos"]["body"]}"/>'
                      f'<rect x="306" y="520" width="410" height="24" rx="12" fill="{shade(DEV, .25)}"/>'
                      f'<rect x="306" y="580" width="330" height="24" rx="12" fill="{shade(DEV, .25)}"/>', "#000000"))


def phone(cv):
    """A phone: the slab on its edge, the screen the emblem."""
    d = rrect(276, 86, 472, 852, 96)
    o = pobj(cv, d, SLAB, ramp=.06, hl=.34)
    o += f'<rect x="452" y="124" width="120" height="26" rx="13" fill="{shade(DEV, -.05)}"/>'
    cv.add(o)
    cv.begin_glyph()
    scr = rrect(320, 180, 384, 680, 52)
    cv.add(raised(cv, f'<path d="{scr}" fill="{cv.lin([(0, shade(TINT, .14)), (1, shade(TINT, -.06))])}"/>'
                      + "".join(f'<rect x="{360 + c * 120}" y="{240 + r * 130}" width="88" height="88" rx="24" fill="{PAPER}" opacity="{.95 if (r + c) % 2 else .7}"/>'
                                for r in range(3) for c in range(3))
                      + f'<rect x="360" y="660" width="304" height="140" rx="30" fill="{CAT["wolos"]["body"]}"/>', "#000000"))


def camera_photo(cv):
    """A camera: body, a raised top plate and a shutter button; the lens the emblem."""
    o = pobj(cv, rrect(300, 220, 260, 120, 30), shade(TINT, -.10), ramp=.05, hl=.3, ambient=False)
    body = rrect(110, 300, 804, 530, 90)
    o += pobj(cv, body, SLAB, ramp=.06, hl=.34)
    o += f'<rect x="700" y="236" width="120" height="70" rx="20" fill="{shade(TINT, -.10)}"/>'
    o += f'<rect x="170" y="380" width="96" height="56" rx="18" fill="{shade(DEV, -.05)}"/>'
    cv.add(o)
    cv.begin_glyph()
    cv.add(raised(cv, f'<circle cx="540" cy="566" r="210" fill="{PAPER}"/>'
                      f'<circle cx="540" cy="566" r="150" fill="{shade(DEV, .04)}"/>'
                      f'<circle cx="540" cy="566" r="88" fill="{shade(TINT, -.18)}"/>'
                      f'<circle cx="500" cy="526" r="30" fill="#fff" opacity=".8"/>', "#000000")
           + led(cv, 800, 400, 20, CAT["store"]["pop"]))


def printer(cv):
    """A printer: the slab, the paper tray behind, a sheet coming out the front (the emblem)."""
    tray = rrect(270, 96, 484, 300, 30)
    o = pobj(cv, tray, PAPER, ramp=.02, hl=.4)
    body = rrect(96, 300, 832, 420, 80)
    o += pobj(cv, body, SLAB, ramp=.06, hl=.34)
    o += f'<rect x="210" y="604" width="604" height="40" rx="20" fill="{shade(DEV, -.08)}"/>'
    cv.add(o)
    cv.begin_glyph()
    sheet = "M246 620H778L812 930H212Z"
    cv.add(raised(cv, f'<path d="{sheet}" fill="{PAPER}"/>'
                      f'<rect x="300" y="700" width="260" height="30" rx="15" fill="{CAT["wolos"]["body"]}"/>'
                      f'<rect x="300" y="770" width="424" height="22" rx="11" fill="{shade(DEV, .3)}"/>'
                      f'<rect x="300" y="830" width="350" height="22" rx="11" fill="{shade(DEV, .3)}"/>', "#000000")
           + led(cv, 790, 420, 22))


DEVICES = [("computer", computer), ("drive-optical", drive_optical), ("media-flash", media_flash),
           ("phone", phone), ("camera-photo", camera_photo), ("printer", printer)]


# ---- mimetypes (the page of paper_set.py, a new type band and emblem) -----------------------
def m_font(cv, c):
    t = tone("media")
    a = "M352 640L476 330H548L672 640H592L564 562H460L432 640ZM482 500H542L512 414Z"
    return raised(cv, f'<path d="{a}" fill="{t}"/>' + f'<rect x="420" y="600" width="184" height="40" rx="20" fill="{CAT["media"]["pop"]}"/>')


def m_html(cv, c):
    t = tone("web")
    return raised(cv, f'<path d="M424 372L322 474L424 576M600 372L702 474L600 576" fill="none" stroke="{t}" stroke-width="54" stroke-linecap="round" stroke-linejoin="round"/>'
                      f'<path d="M552 340L472 608" stroke="{CAT["web"]["pop"]}" stroke-width="46" stroke-linecap="round"/>')


def m_script(cv, c):
    t = tone("dev")
    br = ("M436 330Q372 330 372 390V430Q372 474 326 474Q372 474 372 518V558Q372 618 436 618",
          "M588 330Q652 330 652 390V430Q652 474 698 474Q652 474 652 518V558Q652 618 588 618")
    return raised(cv, "".join(f'<path d="{d}" fill="none" stroke="{t}" stroke-width="48" stroke-linecap="round" stroke-linejoin="round"/>' for d in br)
                  + f'<circle cx="512" cy="474" r="34" fill="{CAT["dev"]["pop"]}"/>')


def m_address_book(cv, c):
    t = tone("talk")
    return raised(cv, f'<rect x="306" y="320" width="412" height="316" rx="40" fill="{CAT["talk"]["tint"]}"/>'
                      f'<circle cx="420" cy="428" r="56" fill="{t}"/>'
                      f'<path d="M336 600A84 80 0 0 1 504 600Z" fill="{t}"/>'
                      f'<path d="M548 420H676M548 486H676M548 552H630" stroke="{t}" stroke-width="30" stroke-linecap="round"/>')


def m_calendar(cv, c):
    t = tone("talk")
    return raised(cv, f'<rect x="318" y="316" width="388" height="340" rx="36" fill="{PAPER}" stroke="{t}" stroke-width="36"/>'
                      f'<path d="M318 400H706" stroke="{t}" stroke-width="36"/>'
                      + "".join(f'<rect x="{372 + i * 98}" y="{456 + j * 84}" width="52" height="44" rx="12" fill="{CAT["talk"]["pop"] if (i, j) == (2, 1) else t}" opacity="{1 if (i, j) == (2, 1) else .55}"/>'
                                for i in range(3) for j in range(2))
                      + f'<path d="M410 276V340M614 276V340" stroke="{t}" stroke-width="34" stroke-linecap="round"/>')


def m_drawing(cv, c):
    t = tone("media")
    return raised(cv, f'<circle cx="426" cy="420" r="96" fill="{CAT["media"]["tint"]}" stroke="{t}" stroke-width="34"/>'
                      f'<rect x="484" y="452" width="200" height="180" rx="26" fill="{t}"/>'
                      f'<path d="M344 640L420 520L496 640Z" fill="{CAT["media"]["pop"]}" stroke="{CAT["media"]["pop"]}" stroke-width="20" stroke-linejoin="round"/>')


def m_cd_image(cv, c):
    t = tone("system")
    return raised(cv, f'<circle cx="512" cy="478" r="186" fill="{CAT["system"]["tint"]}"/>'
                      f'<circle cx="512" cy="478" r="186" fill="none" stroke="{t}" stroke-width="30"/>'
                      f'<path d="M398 372A150 150 0 0 1 512 324" fill="none" stroke="#fff" stroke-width="24" stroke-linecap="round" opacity=".9"/>'
                      f'<circle cx="512" cy="478" r="62" fill="{PAPER}" stroke="{t}" stroke-width="22"/>')


def m_addon(cv, c):
    t = tone("wolos")
    x0, y0, x1, y1, k, nk = 358, 344, 666, 652, 40, 30
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d = (f"M{x0} {y0}H{cx - nk}A{k} {k} 0 1 1 {cx + nk} {y0}H{x1}V{cy - nk}A{k} {k} 0 1 0 {x1} {cy + nk}V{y1}H{x0}"
         f"V{cy + nk}A{k} {k} 0 1 1 {x0} {cy - nk}Z")
    return raised(cv, f'<path d="{d}" fill="{t}" stroke="{t}" stroke-width="20" stroke-linejoin="round"/>'
                      f'<path d="M512 444V552M458 498H566" stroke="{CAT["wolos"]["pop"]}" stroke-width="34" stroke-linecap="round"/>')


MIMES = [("font-x-generic", "media", m_font), ("text-html", "web", m_html), ("text-x-script", "dev", m_script),
         ("x-office-address-book", "talk", m_address_book), ("x-office-calendar", "talk", m_calendar),
         ("x-office-drawing", "media", m_drawing), ("application-x-cd-image", "system", m_cd_image),
         ("application-x-addon", "wolos", m_addon)]
