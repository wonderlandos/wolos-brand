# SPDX-License-Identifier: GPL-2.0-or-later
"""The shell's symbolic icons on the UI stroke grammar (tools/ui/pen.py, docs/adr/brand-ui.md section 1).

Master grid: 24 fen, centre (12, 12), art box 21 fen (outer 1.5..22.5).  Every function takes a Pen and
returns layers (a contour list, or (opacity, contour list)).  Boxes are given by OUTER edges, strokes by
their centre line, rings by OUTER radius, arcs by centre-line radius.  Lines end one fen inside the art
box (the cap adds it back).
"""
import math

from pen import OLD, _sample

ICONS = {}
DIM = 0.35            # G6: the second leaf, an inactive level
DOT = 2.0             # a dot is 4 fen across (a named length)
SLOPE = (1, 2)        # G5: rain, rays and drops fall along the shadow vector 1:2


def icon(*names):
    def deco(fn):
        for n in names:
            ICONS[n] = fn
        return fn
    return deco


def pol(cx, cy, r, a):
    t = math.radians(a)
    return cx + r * math.cos(t), cy + r * math.sin(t)


def sample_curve(pts, n=8):
    return _sample(pts, False, n)


def mirror(half):
    """left half from the axis (x = 12) at the top to the axis at the bottom -> closed figure"""
    return list(half) + [(24 - x, y) for x, y in reversed(half[1:-1])]


def head(tip, direction, size=4.2, spread=42):
    """arrow head: tip, pointing along `direction` degrees"""
    a, b = (math.radians(direction + 180 + spread), math.radians(direction + 180 - spread))
    return [(tip[0] + size * math.cos(a), tip[1] + size * math.sin(a)), tip,
            (tip[0] + size * math.cos(b), tip[1] + size * math.sin(b))]


# ================================================================ navigation and marks
def chev(p, d, size=8, half=8, cx=12, cy=12):
    pts = {"r": [(cx - size / 2, cy - half), (cx + size / 2, cy), (cx - size / 2, cy + half)],
           "l": [(cx + size / 2, cy - half), (cx - size / 2, cy), (cx + size / 2, cy + half)]}[d]
    return p.P(pts)


@icon("go-next")
def go_next(p): return [chev(p, "r", 8, 8)]


@icon("go-previous")
def go_previous(p): return [chev(p, "l", 8, 8)]


@icon("pan-end")
def pan_end(p): return [chev(p, "r", 4.5, 5)]


@icon("pan-start")
def pan_start(p): return [chev(p, "l", 4.5, 5)]


@icon("window-close")
def window_close(p): return [p.L(6.5, 6.5, 17.5, 17.5) + p.L(17.5, 6.5, 6.5, 17.5)]


@icon("list-add")
def list_add(p): return [p.L(12, 5, 12, 19) + p.L(5, 12, 19, 12)]


@icon("list-remove")
def list_remove(p): return [p.L(5, 12, 19, 12)]


@icon("zoom-in")
def zoom_in(p):
    return [p.ring(9.5, 9.5, 8) + p.L(15.4, 15.4, 20.5, 20.5), p.L(6.5, 9.5, 12.5, 9.5) + p.L(9.5, 6.5, 9.5, 12.5)]


@icon("object-select")
def object_select(p): return [p.P([(5, 12.5), (10, 17.5), (19, 7)])]


@icon("emblem-default")
def emblem_default(p): return [p.ring(12, 12, 10.5) + p.P([(7.5, 12.5), (10.8, 15.8), (16.5, 8.8)])]


@icon("view-more")
def view_more(p): return [p.dot(5, 12, 1.8) + p.dot(12, 12, 1.8) + p.dot(19, 12, 1.8)]


def refresh_arc(p, tip_at=352, start=70):
    # an open ring whose gap faces the lower right (G5); the head lands there
    tip = pol(12, 12, 8.5, tip_at)
    return p.arc(12, 12, 8.5, start, tip_at) + p.P(head(tip, tip_at + 90, 4.4, 40))


@icon("view-refresh")
def view_refresh(p): return [refresh_arc(p)]


@icon("view-reveal")
def view_reveal(p):
    up = p.juzhe_pts(2.5, 12, 12, 5, 3, .12)
    dn = p.juzhe_pts(2.5, 12, 12, 19, 3, .12)
    up = up + [(24 - x, y) for x, y in reversed(up[:-1])]
    dn = dn + [(24 - x, y) for x, y in reversed(dn[:-1])]
    return [p.P(up) + p.P(dn) + p.dot(12, 12, 3)]


@icon("view-pin")
def view_pin(p):
    return [p.L(8, 3.5, 16, 3.5) + p.P([(9.5, 3.5), (9.5, 10), (6.5, 14), (17.5, 14), (14.5, 10), (14.5, 3.5)], r=1.5) + p.L(12, 14, 12, 21)]


@icon("view-grid")
def view_grid(p): return [p.box(1.5, 1.5, 9, 9, 2.5) + p.box(13.5, 1.5, 9, 9, 2.5) + p.box(1.5, 13.5, 9, 9, 2.5) + p.box(13.5, 13.5, 9, 9, 2.5)]


@icon("view-app-grid")
def view_app_grid(p):
    out = []
    for r in range(3):
        for c in range(3):
            out += p.slab(1.5 + c * 8, 1.5 + r * 8, 5, 5, 1.5)
    return [out]


@icon("edit-undo")
def edit_undo(p):
    return [p.P([(9, 4.5), (4.5, 9), (9, 13.5)]) + p.L(4.5, 9, 13.5, 9) + p.arc(13.5, 14, 5, 270, 450)]


@icon("edit-delete")
def edit_delete(p):
    body = [(5.5, 9.6), (6.8, 19.5), (8, 21), (16, 21), (17.2, 19.5), (18.5, 9.6)]
    return [p.L(3.5, 6, 20.5, 6) + p.P([(9, 6), (9, 3.5), (15, 3.5), (15, 6)], r=1) + p.P(body, r=1.5) + p.L(10, 12.4, 10, 17.4) + p.L(14, 12.4, 14, 17.4)]


@icon("edit-paste")
def edit_paste(p):
    return [p.box(4.5, 3.5, 15, 19, 3) + p.pslab(8, 1.5, 8, 4), p.L(8.5, 12, 15.5, 12) + p.L(8.5, 16.5, 13, 16.5)]


@icon("document-edit")
def document_edit(p):
    return [p.poly([(15.5, 4), (20, 8.5), (9, 19.5), (4.5, 19.5), (4.5, 15)]), p.L(13, 6.5, 17.5, 11)]


@icon("starred")
def starred(p):
    return [p.poly([pol(12, 12.8, 9.4 if k % 2 == 0 else 4.4, -90 + 36 * k) for k in range(10)])]


@icon("mark-location")
def mark_location(p):
    half = [(12, 2.5)] + [pol(12, 9.5, 7, a) for a in range(-80, -200, -20)] + [(5.6, 13.5), (12, 21.5)]
    return [p.P(mirror(half), r=1.2) + p.ring(12, 9.5, 3.4)]


@icon("system-search")
def system_search(p): return [p.ring(9.5, 9.5, 8) + p.L(15.4, 15.4, 20.5, 20.5)]


# ================================================================ status
@icon("dialog-warning")
def dialog_warning(p):
    return [p.P([(12, 3.5), (21, 19.5), (3, 19.5)], r=2, closed=True), p.L(12, 9.5, 12, 14.2) + p.dot(12, 17, 1.2)]


@icon("software-update-available")
def sw_update(p):
    return [p.ring(12, 12, 10.5) + p.L(12, 6.5, 12, 15.5) + p.P([(8, 11.8), (12, 16), (16, 11.8)])]


@icon("software-update-urgent")
def sw_update_urgent(p):
    # the ring opens toward the lower right, where the badge lands (G5)
    return [p.arc(12, 12, 9.5, 80, 370) + p.L(12, 6.5, 12, 15) + p.P([(8.2, 11.4), (12, 15.4), (15.8, 11.4)]), p.dot(18.4, 18.4, 2.7)]


@icon("help-about")
def help_about(p): return [p.ring(12, 12, 10.5) + p.L(12, 11, 12, 17), p.dot(12, 7.4, 1.3)]


@icon("security-high")
def security_high(p):
    slope = p.juzhe_pts(12, 3.2, 3.5, 6, 3, .06)
    side = sample_curve([(3.5, 6), (3.5, 11.2), (6.4, 16.2), (12, 21.2)], 8)
    half = slope + side[1:]
    return [p.P(mirror(half), closed=True) + p.P([(8.3, 11.5), (11, 14.2), (15.8, 8.8)])]


@icon("channel-secure", "system-lock-screen")
def lock(p):
    return [p.box(4.5, 10.5, 15, 12, 3) + p.arc(12, 9.8, 4.8, 180, 360) + p.L(7.2, 9.8, 7.2, 11) + p.L(16.8, 9.8, 16.8, 11), p.dot(12, 16.5, 1.7)]


@icon("user-available")
def user_available(p): return [p.ring(12, 12, 10.5), p.dot(12, 12, 3.8)]


def person(p, cx=12, top=3, scale=1.0):
    return p.ring(cx, top + 5 * scale, 4.6 * scale) + p.arc(cx, top + 22 * scale, 10.5 * scale, 232, 308)


@icon("avatar-default")
def avatar_default(p):
    return [p.ring(12, 7.5, 4.8) + p.arc(12, 24, 9.5, 222, 318)]


@icon("system-users")
def system_users(p):
    return [p.ring(9, 8, 4.2) + p.arc(9, 22, 8.5, 225, 315) + p.ring(17.3, 9, 3.2) + p.arc(17.3, 20.5, 6.3, 235, 305)]


def gear(p, cx, cy, ro, ri, teeth):
    pts = []
    for k in range(teeth):
        b = 360 * k / teeth
        for da, rad in ((-0.30, ri), (-0.15, ro - 1), (0.15, ro - 1), (0.30, ri)):
            pts.append(pol(cx, cy, rad, b + da * 360 / teeth))
    return p.P(pts, r=0.8, closed=True)


@icon("emblem-system")
def emblem_system(p): return [gear(p, 12, 12, 11, 7.8, 8) + p.ring(12, 12, 3.9)]


# ================================================================ power
@icon("system-shutdown")
def system_shutdown(p): return [p.arc(12, 13, 8, -55, 235) + p.L(12, 3.5, 12, 12)]


@icon("system-reboot")
def system_reboot(p): return [refresh_arc(p), p.dot(12, 12, 1.8)]


@icon("system-log-out")
def system_log_out(p):
    return [p.P([(10, 3.5), (5.5, 3.5), (3.5, 5.5), (3.5, 18.5), (5.5, 20.5), (10, 20.5)], r=1.5) + p.L(9, 12, 20, 12) + p.P([(16, 8), (20, 12), (16, 16)])]


@icon("power-profile-balanced")
def power_balanced(p):
    return [p.arc(12, 17, 9, 180, 360) + p.L(3, 17, 21, 17), p.L(12, 17, 16.4, 10.4) + p.dot(12, 17, 2.2)]


# ================================================================ network
def wifi(p, level, dim=DIM):
    out = [(1.0 if level >= 0 else dim, p.dot(12, 19, 1.9))]
    for i, (r, a) in enumerate(((6, 45), (10.5, 45), (15, 42))):
        out.append((1.0 if level > i else dim, p.arc(12, 19.5, r, 270 - a, 270 + a)))
    return out


@icon("network-wireless", "network-wireless-signal-excellent")
def net_wireless(p): return wifi(p, 3)


@icon("network-wireless-signal-good")
def net_good(p): return wifi(p, 2)


@icon("network-wireless-signal-ok")
def net_ok(p): return wifi(p, 1)


@icon("network-wireless-signal-weak")
def net_weak(p): return wifi(p, 0)


@icon("network-wireless-offline", "network-offline")
def net_off(p): return wifi(p, -1) + [p.L(4, 4, 20, 20)]


def arc_outside_rect(p, cx, cy, r, a0, a1, rect, gap=2.2):
    """arc a0..a1 without the runs that fall inside rect (x0, y0, x1, y1) grown by gap"""
    x0, y0, x1, y1 = rect[0] - gap, rect[1] - gap, rect[2] + gap, rect[3] + gap
    out, run = [], None
    steps = max(2, int(abs(a1 - a0)))
    for j in range(steps + 1):
        a = a0 + (a1 - a0) * j / steps
        x, y = pol(cx, cy, r, a)
        hidden = x0 <= x <= x1 and y0 <= y <= y1
        if not hidden and run is None:
            run = a
        if (hidden or j == steps) and run is not None:
            end = a if not hidden else a0 + (a1 - a0) * (j - 1) / steps
            if abs(end - run) > 6:
                out += p.arc(cx, cy, r, run, end)
            run = None
    return out


@icon("network-wireless-encrypted")
def net_enc(p):
    rect = (13, 13.5, 22, 22.5)
    out = p.dot(8, 19.5, 1.9)
    for r, a in ((6, 45), (10.5, 45), (15, 42)):
        out += arc_outside_rect(p, 8, 19.5, r, 270 - a, 270 + a, rect)
    return [out, p.slab(13, 15, 9, 7.5, 1.8) + p.arc(17.5, 15, 2.4, 180, 360) + p.L(15.1, 15, 15.1, 16) + p.L(19.9, 15, 19.9, 16)]


@icon("network-wired")
def network_wired(p):
    return [p.box(8, 1.5, 8, 6.5, 2) + p.L(12, 8, 12, 14) + p.L(4.5, 14, 19.5, 14) + p.L(4.5, 14, 4.5, 16) + p.L(19.5, 14, 19.5, 16),
            p.box(1.5, 16, 6, 6.5, 2) + p.box(9, 16, 6, 6.5, 2) + p.box(16.5, 16, 6, 6.5, 2) if False else p.box(1.5, 16, 6, 6.5, 2) + p.box(16.5, 16, 6, 6.5, 2) + p.L(12, 14, 12, 16.5)]


@icon("network-server")
def network_server(p):
    return [p.box(2.5, 2.5, 19, 8.5, 3) + p.box(2.5, 13, 19, 8.5, 3), p.dot(17, 6.8, 1.2) + p.dot(17, 17.3, 1.2)]


def bt(p):
    return p.P([(6.5, 7.5), (17, 16.5), (12, 21), (12, 3), (17, 7.5), (6.5, 16.5)])


@icon("bluetooth-active")
def bluetooth_active(p): return [bt(p)]


@icon("bluetooth-disabled")
def bluetooth_disabled(p): return [(DIM, bt(p)), p.L(4, 4, 20, 20)]


# ================================================================ audio
def spk(p):
    return p.poly([(2.5, 9.4), (5.6, 9.4), (8.8, 6.2), (8.8, 17.8), (5.6, 14.6), (2.5, 14.6)])


@icon("audio-volume-muted")
def vol_muted(p): return [spk(p), p.L(15, 9.5, 21, 14.5) + p.L(21, 9.5, 15, 14.5) if False else p.L(15.2, 9.2, 21, 14.8) + p.L(21, 9.2, 15.2, 14.8)]


def vol(p, n):
    return [spk(p)] + [p.arc(7.5, 12, r, -44, 44) for r in (5.8, 9.6, 13.4)[:n]]


@icon("audio-volume-low")
def vol_low(p): return vol(p, 1)


@icon("audio-volume-medium")
def vol_med(p): return vol(p, 2)


@icon("audio-volume-high")
def vol_high(p): return vol(p, 3)


@icon("audio-input-microphone", "microphone-sensitivity-high")
def mic(p): return [p.box(8, 1.5, 8, 13.5, 4) + p.arc(12, 11, 7.8, 5, 175) + p.L(12, 19, 12, 21.5)]


@icon("microphone-sensitivity-muted")
def mic_muted(p): return [mic(p)[0], p.L(4, 4, 20, 20)]


@icon("audio-headphones")
def headphones(p):
    return [p.arc(12, 13, 8.8, 180, 360) + p.L(3.2, 13, 3.2, 14), p.slab(2, 12.5, 5.5, 8.5, 2.5) + p.slab(16.5, 12.5, 5.5, 8.5, 2.5)]


@icon("audio-headset")
def headset(p):
    return [p.arc(12, 11.5, 8.8, 180, 360) + p.L(3.2, 11.5, 3.2, 13), p.slab(2, 12, 5.5, 8, 2.5) + p.slab(16.5, 12, 5.5, 8, 2.5) + p.P([(20.8, 16), (20.8, 20), (14, 21.2)], r=2)]


@icon("audio-speakers")
def speakers(p): return [p.box(5, 1.5, 14, 21, 3) + p.ring(12, 15.6, 3.9), p.dot(12, 6.4, 1.6)]


@icon("audio-x-generic")
def audio_generic(p):
    return [p.L(9, 17, 9, 5.5) + p.L(9, 5.5, 20, 3.5) + p.L(20, 3.5, 20, 15.5), p.ring(6, 18, 3.7) + p.ring(17, 16.5, 3.7) if False else p.slab(2.5, 14.5, 7, 7, 3.5) + p.slab(13.5, 13, 7, 7, 3.5)]


# ================================================================ media
@icon("media-playback-start")
def play(p): return [p.poly([(6.5, 4), (20, 12), (6.5, 20)])]


@icon("media-playback-pause")
def pause(p): return [p.slab(5, 3, 5.5, 18, 2.5) + p.slab(13.5, 3, 5.5, 18, 2.5)]


@icon("media-skip-forward")
def skip_fwd(p): return [p.poly([(4.5, 5), (16, 12), (4.5, 19)]) + p.slab(17.5, 3.5, 3.5, 17, 1.75)]


@icon("media-skip-backward")
def skip_back(p): return [p.poly([(19.5, 5), (8, 12), (19.5, 19)]) + p.slab(3, 3.5, 3.5, 17, 1.75)]


@icon("media-record")
def record(p): return [p.disc(12, 12, 8.5)]


# ================================================================ display and light
@icon("display-brightness")
def brightness(p):
    rays = []
    for k in range(8):
        x1, y1 = pol(12, 12, 8.4, 45 * k)
        x2, y2 = pol(12, 12, 10.2, 45 * k)
        rays += p.L(x1, y1, x2, y2)
    return [p.ring(12, 12, 5.8) + rays]


@icon("keyboard-brightness")
def kbd_brightness(p):
    rays = []
    for k in range(3):
        a = 215 + 55 * k
        x1, y1 = pol(12, 14.5, 5.6, a)
        x2, y2 = pol(12, 14.5, 8.6, a)
        rays += p.L(x1, y1, x2, y2)
    return [p.box(1.5, 13.5, 21, 9, 3) + p.L(7, 18, 17, 18) + rays]


@icon("night-light")
def night_light(p): return [p.moon_arcs(11.5, 12.5, 8.6, 4.4, -4.0, 7.3)]


@icon("video-display")
def video_display(p): return [p.box(1.5, 3, 21, 14.5, 3) + p.L(12, 17.5, 12, 20.5) + p.L(7, 20.5, 17, 20.5)]


@icon("computer")
def computer(p): return [p.box(2.5, 3.5, 19, 13.5, 3) + p.L(9, 21, 15, 21)]


@icon("camera-photo")
def camera(p):
    return [p.P([(2.5, 8.5), (2.5, 18), (4.5, 20.5), (19.5, 20.5), (21.5, 18), (21.5, 8.5), (19.5, 6.5), (16, 6.5), (14.5, 3.8), (9.5, 3.8), (8, 6.5), (4.5, 6.5)], r=1.8, closed=True) + p.ring(12, 13.5, 4.8)]


@icon("printer")
def printer(p):
    return [p.P([(7, 7), (7, 3.5), (17, 3.5), (17, 7)], r=1.5) + p.box(1.5, 7, 21, 10.5, 3) + p.box(6.5, 13.5, 11, 8.5, 1.5)]


@icon("phone")
def phone(p): return [p.box(6, 1.5, 12, 21, 3) + p.L(10.5, 4.8, 13.5, 4.8), p.dot(12, 18.6, 1.3)]


@icon("input-keyboard")
def input_keyboard(p):
    ks = []
    for y in (8.6, 12.2):
        for c in range(5):
            ks += p.dot(6 + c * 3, y, 0.9)
    return [p.box(1.5, 3.5, 21, 17, 3) + p.L(8, 16.2, 16, 16.2), ks]


@icon("input-mouse")
def input_mouse(p): return [p.box(5.5, 1.5, 13, 21, 6.5) + p.L(12, 3, 12, 10)]


@icon("input-touchpad")
def input_touchpad(p): return [p.box(2.5, 3.5, 19, 17, 3) + p.L(3, 15, 21, 15) + p.L(12, 15, 12, 20)]


@icon("input-tablet")
def input_tablet(p): return [p.box(1.5, 4, 21, 16, 3), p.dot(18.4, 12, 1.3)]


@icon("input-gaming", "applications-games")
def input_gaming(p):
    body = [(7, 6), (17, 6), (20.5, 8), (22, 15), (19.5, 18.5), (16, 15), (8, 15), (4.5, 18.5), (2, 15), (3.5, 8)]
    return [p.P(body, r=2, closed=True) + p.L(6.5, 10.5, 10.5, 10.5) + p.L(8.5, 8.5, 8.5, 12.5), p.dot(16, 9.8, 1.3) + p.dot(18.6, 12.4, 1.3)]


@icon("drive-harddisk")
def drive_hd(p): return [p.box(1.5, 6.5, 21, 11, 3) + p.L(6, 12, 11, 12), p.dot(17.2, 12, 1.4)]


@icon("drive-multidisk")
def drive_multi(p): return [p.box(1.5, 10.5, 21, 11, 3) + p.P([(5, 5.5), (19, 5.5)]), p.L(6, 16, 11, 16) + p.dot(17.2, 16, 1.4)]


# ================================================================ files, apps
@icon("folder")
def folder(p):
    tab = p.juzhe_pts(9.2, 4.5, 13.2, 7.8, 3, .15, 6)
    mid = [(x, y, 0) for x, y in tab[1:-1]]
    pts = [(2.5, 20.5, 3), (2.5, 4.5, 3), (tab[0][0], tab[0][1], 1.4)] + mid + [(tab[-1][0], tab[-1][1], 1.4), (21.5, 7.8, 3), (21.5, 20.5, 3)]
    return [p.P(pts, closed=True)]


@icon("folder-publicshare")
def folder_share(p):
    return [folder(p)[0], p.dot(12, 12.2, 1.6) + p.arc(12, 19.5, 4.5, 235, 305)]


@icon("image-x-generic")
def image_generic(p):
    return [p.box(1.5, 3.5, 21, 17, 3) + p.P([(5, 17), (9.5, 11.5), (13, 15), (15.5, 12.5), (19, 17)], r=0.5), p.dot(16.5, 8, 1.5)]


@icon("package-x-generic")
def package_generic(p):
    return [p.P([(12, 3), (20.5, 7.5), (20.5, 16.5), (12, 21), (3.5, 16.5), (3.5, 7.5)], r=1.2, closed=True) + p.L(4, 8, 12, 12.3) + p.L(20, 8, 12, 12.3) + p.L(12, 12.3, 12, 20.5)]


@icon("x-office-calendar")
def calendar(p):
    return [p.box(2.5, 4, 19, 18, 3) + p.L(3, 10, 21, 10) + p.L(8, 1.8, 8, 5.5) + p.L(16, 1.8, 16, 5.5), p.dot(15.6, 16, 1.7)]


@icon("applications-graphics")
def apps_graphics(p):
    pts = [(12, 2.5), (6, 6.5), (3, 12), (4.5, 17.5), (9, 21), (13.5, 21), (14.5, 18), (13.5, 16), (15, 14.5), (19, 14.5), (21, 12), (20, 7.5), (16.5, 4)]
    return [p.P(pts, r=1.5, closed=True), p.dot(7.8, 10.6, 1.1) + p.dot(10.6, 6.8, 1.1) + p.dot(15.6, 7.2, 1.1) + p.dot(7.8, 15.6, 1.1)]


@icon("applications-office")
def apps_office(p):
    return [p.P([(15, 2.5), (6.5, 2.5), (4.5, 4.5), (4.5, 19.5), (6.5, 21.5), (17.5, 21.5), (19.5, 19.5), (19.5, 7), (15, 2.5)], r=1.2) + p.P([(15, 2.5), (15, 7), (19.5, 7)], r=0.5) + p.L(8.5, 12, 15.5, 12) + p.L(8.5, 16, 14, 16)]


@icon("applications-engineering")
def apps_eng(p): return [p.P([(7.5, 7.5), (3, 12), (7.5, 16.5)]) + p.P([(16.5, 7.5), (21, 12), (16.5, 16.5)]) + p.L(13.5, 5.5, 10.5, 18.5)]


# ================================================================ preferences
@icon("preferences-system-time")
def pref_time(p): return [p.ring(12, 12, 10.5) + p.P([(12, 6), (12, 12), (16, 14.5)])]


def lens(cx, a, y0, y1, n=20):
    pts = []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        pts.append((cx + a * math.sqrt(max(0.0, 1 - ((y - 12) / ((y1 - y0) / 2)) ** 2)), y))
    return pts


@icon("preferences-desktop-locale")
def pref_locale(p):
    return [p.ring(12, 12, 10.5) + p.L(3, 12, 21, 12) + p.P(lens(12, 4.4, 2.8, 21.2)) + p.P(lens(12, -4.4, 2.8, 21.2))]


@icon("preferences-desktop-appearance")
def pref_appearance(p):
    return [p.ring(12, 12, 10.5), p.dot(8.2, 10.6, 1.4) + p.dot(12.6, 7.8, 1.4) + p.dot(16.2, 11.8, 1.4) + p.dot(10, 15.4, 1.4)]


@icon("wolos-contrast")
def contrast(p): return [p.ring(12, 12, 10.5), p.pie(12, 12, 8.4 if p.N == 24 else 8.6, 90, 270)]


@icon("preferences-desktop-accessibility")
def pref_access(p):
    return [p.P([(3.5, 8.5), (12, 10), (20.5, 8.5)]) + p.L(12, 10, 12, 14.5) + p.L(12, 14.5, 7.8, 21) + p.L(12, 14.5, 16.2, 21), p.dot(12, 4.6, 2)]


@icon("preferences-desktop-wallpaper")
def pref_wall(p):
    return [p.box(1.5, 3, 21, 14.5, 3) + p.L(8, 21, 16, 21) + p.P([(5.5, 14), (9.5, 9.5), (13, 12.5), (15, 10.5), (18.5, 14)], r=0.5), p.dot(16.8, 7.2, 1.3)]


def bell(p):
    dome = [pol(12, 9.8, 6.4, a) for a in range(270, 178, -6)]
    flare = p.juzhe_pts(dome[-1][0], dome[-1][1], 3.6, 16.5, 3, .12)
    half = [(12, 3.4)] + dome[1:] + flare[1:] + [(12, 16.5)]
    return p.P(mirror(half), r=0.8, closed=True) + p.dot(12, 20.6, 1.5)


@icon("preferences-system-notifications")
def pref_notif(p): return [bell(p)]


# ================================================================ battery
def battery(p, frac, charging=False, missing=False):
    out = [p.box(1.5, 6, 19, 12, 3) + p.slab(20, 9.8, 2.5, 4.4, 1.25)]
    if charging:
        out.append(p.poly([(13.2, 9.4), (8.8, 12.4), (11.6, 12.4), (10.8, 14.8), (15.2, 11.6), (12.4, 11.6)], round_=False))
        if frac > 0:
            out.append((DIM, p.slab(3.5, 7.6, 15 * frac, 8.8, 1.2)))
    elif frac > 0:
        out.append(p.slab(3.5, 7.6, 15 * frac, 8.8, 1.2))
    if missing:
        out.append(p.L(4, 4, 20, 20))
    return out


for _n, _f, _c in (("battery-full", 1.0, 0), ("battery-full-charged", 1.0, 0), ("battery-good", .66, 0), ("battery-low", .33, 0), ("battery-caution", .17, 0),
                   ("battery-full-charging", 1.0, 1), ("battery-good-charging", .66, 1), ("battery-low-charging", .33, 1), ("battery-caution-charging", .17, 1)):
    ICONS[_n] = (lambda f, c: (lambda p: battery(p, f, charging=bool(c))))(_f, _c)
ICONS["battery-missing"] = lambda p: battery(p, 0, missing=True)


# ================================================================ weather
def cloud(p, lobes, base):
    """cloud outline from lobes (x, y, centre-line radius) standing on the line y = base"""
    out, ints = [], []
    for (x1, y1, r1), (x2, y2, r2) in zip(lobes, lobes[1:]):
        d = math.hypot(x2 - x1, y2 - y1)
        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
        hh = math.sqrt(max(r1 * r1 - a * a, 0))
        px, py = x1 + a * (x2 - x1) / d, y1 + a * (y2 - y1) / d
        c = [(px + hh * (y2 - y1) / d, py - hh * (x2 - x1) / d), (px - hh * (y2 - y1) / d, py + hh * (x2 - x1) / d)]
        ints.append(min(c, key=lambda q: q[1]))
    for i, (x, y, r) in enumerate(lobes):
        ang = lambda q: math.degrees(math.atan2(q[1] - y, q[0] - x))
        a0 = 90 if i == 0 else ang(ints[i - 1]) % 360
        a1 = 450 if i == len(lobes) - 1 else ang(ints[i])
        while a1 <= a0:
            a1 += 360
        out += p.arc(x, y, r, a0, a1)
    out += p.L(lobes[0][0], base, lobes[-1][0], base)
    return out


def cl(dx=0.0, dy=0.0, s=1.0):
    lobes = [(6.4, 11.4, 3.4), (12.1, 9.4, 5.4), (17.4, 12.0, 3.2)]
    return [(12 + (x - 12) * s + dx, 12 + (y - 12) * s + dy, r * s) for x, y, r in lobes], 12 + (15.0 - 12) * s + dy


def rain(p, n=3, dy=0.0):
    out = []
    for i in range(n):
        x = 7 + i * 5
        out += p.L(x, 18 + dy, x - 1.6, 21.2 + dy)         # falls along the shadow vector (G5)
    return out


@icon("weather-overcast")
def w_over(p):
    lobes, base = cl(0, 1.4, 1.0)
    return [cloud(p, lobes, base)]


@icon("weather-fog")
def w_fog(p):
    lobes, base = cl(0, -2.5)
    return [cloud(p, lobes, base) + p.L(4, 16.6, 20, 16.6) + p.L(7, 20.6, 17, 20.6)]


@icon("weather-showers")
def w_showers(p):
    lobes, base = cl(0, -2.5)
    return [cloud(p, lobes, base) + rain(p)]


@icon("weather-showers-scattered")
def w_showers_s(p):
    lobes, base = cl(0, -2.5)
    return [cloud(p, lobes, base) + p.L(7, 18, 5.4, 21.2) + p.L(17, 18, 15.4, 21.2), p.dot(12, 19.8, 1.1)]


@icon("weather-snow")
def w_snow(p):
    lobes, base = cl(0, -2.5)
    return [cloud(p, lobes, base), p.dot(7.5, 19.5, 1.2) + p.dot(12, 21, 1.2) + p.dot(16.5, 19.5, 1.2)]


@icon("weather-storm")
def w_storm(p):
    lobes, base = cl(0, -2.5)
    return [cloud(p, lobes, base), p.poly([(13.4, 15.6), (9, 19.4), (12, 19.4), (10.6, 22), (15.4, 18), (12.4, 18)], round_=True)]


@icon("weather-clear")
def w_clear(p):
    rays = []
    for k in range(8):
        x1, y1 = pol(12, 12, 8.6, 45 * k)
        x2, y2 = pol(12, 12, 10.4, 45 * k)
        rays += p.L(x1, y1, x2, y2)
    return [p.ring(12, 12, 5.8) + rays]


@icon("weather-clear-night")
def w_clear_night(p): return [p.moon_arcs(11.5, 12.5, 8.6, 4.4, -4.0, 7.3)]


def arc_outside(p, cx, cy, r, a0, a1, discs, gap=2.4):
    out, run = [], None
    steps = max(2, int(abs(a1 - a0)))
    for j in range(steps + 1):
        a = a0 + (a1 - a0) * j / steps
        x, y = pol(cx, cy, r, a)
        hidden = any(math.hypot(x - dx, y - dy) < dr + gap for dx, dy, dr in discs)
        if not hidden and run is None:
            run = a
        if (hidden or j == steps) and run is not None:
            end = a if not hidden else a0 + (a1 - a0) * (j - 1) / steps
            if abs(end - run) > 6:
                out += p.arc(cx, cy, r, run, end)
            run = None
    return out


def behind_cloud():
    lobes, base = cl(3.4, 4.4, 0.76)
    discs = [(x, y, r + 1) for x, y, r in lobes] + [(lobes[0][0], base - 2, 6), (lobes[1][0], base - 2, 7), (lobes[2][0], base - 2, 6)]
    return lobes, base, discs


@icon("weather-few-clouds")
def w_few(p):
    lobes, base, discs = behind_cloud()
    sun = arc_outside(p, 8, 8, 3.8, 0, 360, discs)
    for k in range(8):
        a = 45 * k
        x1, y1 = pol(8, 8, 6.6, a)
        x2, y2 = pol(8, 8, 8.4, a)
        if not any(math.hypot(x - dx, y - dy) < dr + 1 for (x, y) in ((x1, y1), (x2, y2)) for dx, dy, dr in discs) and x2 > 0.5 and y2 > 0.5:
            sun += p.L(x1, y1, x2, y2)
    return [sun + cloud(p, lobes, base)]


@icon("weather-few-clouds-night")
def w_few_night(p):
    lobes, base, discs = behind_cloud()
    (c1, r1, o), (c2, r2, i) = OLD.moon_arcs(9, 9, 7, 3.8, -3.2, 6)
    m = arc_outside(p, c1[0], c1[1], r1, o[0], o[1], discs) + arc_outside(p, c2[0], c2[1], r2, i[0], i[1], discs)
    return [m + cloud(p, lobes, base)]


# ================================================================ WolOS
@icon("wolos-widgets")
def wolos_widgets(p):
    return [p.box(1.5, 1.5, 9, 9, 2.5) + p.box(13.5, 1.5, 9, 9, 2.5) + p.box(1.5, 13.5, 21, 9, 3)]


@icon("wolos-chip")
def wolos_chip(p):
    pins = []
    for k in (9.2, 14.8):
        pins += p.L(k, 1.8, k, 5.2) + p.L(k, 18.8, k, 22.2) + p.L(1.8, k, 5.2, k) + p.L(18.8, k, 22.2, k)
    return [p.box(5.5, 5.5, 13, 13, 2.5) + pins, p.slab(10, 10, 4, 4, 1.2)]


def spark(p, cx, cy, r, waist=0.2, n=7):
    """four-point spark, each side a juzhe-like concave fold toward the centre"""
    pts = []
    for q in range(4):
        a0 = -90 + 90 * q
        t0, t1 = pol(cx, cy, r, a0), pol(cx, cy, r, a0 + 90)
        c = pol(cx, cy, r * waist, a0 + 45)
        for i in range(n):
            t = i / n
            pts.append(((1 - t) ** 2 * t0[0] + 2 * (1 - t) * t * c[0] + t * t * t1[0], (1 - t) ** 2 * t0[1] + 2 * (1 - t) * t * c[1] + t * t * t1[1]))
    return p.poly(pts, round_=True)


@icon("wolos-assistant")
def wolos_assistant(p): return [spark(p, 10.5, 13.5, 9.3, .12), spark(p, 19, 5.2, 3.6, .1, 5)]


@icon("wolos-effects")
def wolos_effects(p):
    return [p.L(4, 20, 14, 10), spark(p, 17.5, 6.5, 5, .1, 6), p.dot(6.5, 7, 1) + p.dot(19.2, 16, 1)]


def brackets(p, arm=5):
    out = []
    for (x, y, sx, sy) in ((2.5, 2.5, 1, 1), (21.5, 2.5, -1, 1), (21.5, 21.5, -1, -1), (2.5, 21.5, 1, -1)):
        out += p.P([(x, y + sy * arm), (x, y), (x + sx * arm, y)], r=1.5)
    return out


def dashed(p, x, y, w, h, dash=3.2, gap=3.0):
    out = []
    for (x1, y1, x2, y2) in ((x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)):
        n = math.hypot(x2 - x1, y2 - y1)
        k = max(1, round((n + gap) / (dash + gap)))
        step = n / k
        for j in range(k):
            s = j * step + (0 if j == 0 else gap / 2)
            e = (j + 1) * step - (0 if j == k - 1 else gap / 2)
            out += p.L(x1 + (x2 - x1) * s / n, y1 + (y2 - y1) * s / n, x1 + (x2 - x1) * e / n, y1 + (y2 - y1) * e / n)
    return out


@icon("wolos-capture-screen")
def cap_screen(p): return [brackets(p), p.slab(8.5, 9.5, 7, 5, 2)]


@icon("wolos-capture-window")
def cap_window(p): return [brackets(p), p.box(7.5, 8.5, 9, 7, 2)]


@icon("wolos-capture-selection")
def cap_selection(p): return [dashed(p, 3, 3, 18, 18)]


@icon("wolos-record-screen")
def rec_screen(p): return [p.box(1.5, 3.5, 21, 17, 3.5), p.disc(12, 12, 3.6)]


@icon("wolos-record-selection")
def rec_selection(p): return [dashed(p, 3, 3, 18, 18), p.disc(12, 12, 3.6)]


@icon("wolos-restore")
def wolos_restore(p):
    tip = pol(12, 12, 8.6, 218)
    return [p.arc(12, 12, 8.6, 218, 520) + p.P(head(tip, 218 - 90, 4.4, 40)) + p.P([(12, 7), (12, 12), (15.5, 14)])]


@icon("wolos-reduce-motion")
def wolos_reduce(p):
    return [p.ring(16, 12, 6.5) + p.L(2.5, 7, 7, 7) + p.L(2.5, 12, 6, 12) + p.L(2.5, 17, 7, 17)]


@icon("wolos-dock")
def wolos_dock(p): return [p.box(1.5, 3, 21, 18, 3.5), p.pslab(7.5, 13.2, 9, 3)]


@icon("wolos-dark-mode")
def wolos_dark(p): return [p.moon_solid(11.5, 12.5, 9.2, 4.6, -4.2, 7.8)]


@icon("wolos-control-center")
def wolos_cc(p):
    # two toggles (the A2 control-center): the one that is on is solid with its knob cut out, lower right lands
    top = p.pslab(1.5, 3, 21, 9)
    knob = p.hole(OLD.D(p.pos(17.2), p.pos(7.5), p.ln(2.2)))
    return [top + knob, p.pill(1.5, 13.5, 21, 9) + p.disc(6.8, 18, 2.2)]
