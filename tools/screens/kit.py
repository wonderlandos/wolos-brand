# SPDX-License-Identifier: GPL-2.0-or-later
"""The Kit sheet: every widget of kit.css once, drawn from a metrics table (K_CUR = shipped kit.css, K_NEW = brand).
Frame 960 x 640 = two columns of 420 on a 40 margin. The same function draws both, so the board compares like with like."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scene import Scene  # noqa: E402

K_CUR = dict(
    name="cur", ctl=24, ctl_r=6, btn_pad=12, field_r=6, switch=(30, 18, 2), row=40, card_r=10, card_sh="cur-card", sheet_sh="cur-sheet",
    sheet_pad=16, panel_r=16, panel_sh="cur-glass", seg_pad=2, seg_btn=20, seg_r=6, seg_in=4, badge=18, slider=(4, 16), type=dict(
        cap=(11, 16), body=(13, 20), head=(15, 22), title=(26, 34)), side_row=28, side_pitch=28, side_w=220, toolbar=36, gap=(4, 8, 12, 16, 24, 32),
    rim=True, gloss_lr=False, space=24)
K_NEW = dict(
    name="new", ctl=24, ctl_r=8, btn_pad=12, field_r=8, switch=(36, 24, 2), row=40, card_r=12, card_sh="e1", sheet_sh="e2",
    sheet_pad=16, panel_r=16, panel_sh="e2", seg_pad=4, seg_btn=24, seg_r=8, seg_in=4, badge=16, slider=(4, 16), type=dict(
        cap=(11, 16), body=(13, 20), head=(16, 24), title=(27, 40)), side_row=24, side_pitch=28, side_w=240, toolbar=40, gap=(4, 8, 12, 16, 24, 40),
    rim=True, gloss_lr=True, space=24)


def sheet(mode, M, tok, name="kit-sheet"):
    s = Scene(960, 640, mode, tok, name, backdrop=None)
    new = M["name"] == "new"
    s.panel(0, 0, 960, 640, 0, fill="surface", tree=False)
    root = s.panel(0, 0, 960, 640, 0, fill="surface", role="box")
    T = M["type"]
    x0, x1 = 40, 500
    # ---- left column: buttons, fields, switch, slider, segmented, badges ----
    s.text(root, x0, 24, 420, T["head"][1], "Buttons", T["head"][0], 600, "text", group="h")
    y = 24 + T["head"][1] + 8 + (4 if new else 0)
    bx = x0
    bw_ = (84, 84, 60, 60) if new else (72, 72, 64, 64)
    for (lab, kind), w in zip((("Cancel", "default"), ("Install", "primary"), ("Later", "plain"), ("Erase", "destructive")), bw_):
        s.button(root, bx, y, w, M["ctl"], lab, kind, r=M["ctl_r"], shadow="e1" if (new and kind == "primary") else None, group="btns")
        bx += w + (8 if new else 8)
    y += M["ctl"] + 24
    s.text(root, x0, y, 420, T["head"][1], "Fields", T["head"][0], 600, "text", group="h")
    y += T["head"][1] + 8
    s.field(root, x0, y, 420, M["ctl"], "", "Search", r=M["field_r"], trailing="system-search", group="fields")
    y += M["ctl"] + 8
    s.field(root, x0, y, 420, M["ctl"], "alice", "", r=M["field_r"], focus=True, group="fields")
    y += M["ctl"] + (8 if new else 8)
    # switch + slider + segmented
    sw, sh, sp = M["switch"]
    s.text(root, x0, y, 120, M["ctl"], "Wi-Fi", T["body"][0], 400, "text", group="ctl")
    s.switch(root, x0 + 140, y + (M["ctl"] - sh) // 2, sw, sh, on=True, pad=sp, group="sw")
    s.switch(root, x0 + 140 + sw + 12, y + (M["ctl"] - sh) // 2, sw, sh, on=False, pad=sp, group="sw")
    y += M["ctl"] + 8
    tr, th = M["slider"]
    s.panel(x0, y + (M["ctl"] - tr) // 2, 420, tr, tr // 2, fill="control", parent=root, group="slider")
    s.panel(x0, y + (M["ctl"] - tr) // 2, 190, tr, tr // 2, fill="accent", parent=root, group="slider")
    s.panel(x0 + 190 - th // 2, y + (M["ctl"] - th) // 2, th, th, th // 2, fill="#ffffff", parent=root, stroke="line", shadow="e1" if new else "cur-card", role="control")
    y += M["ctl"] + 8
    seg = M["seg_pad"] * 2 + M["seg_btn"]
    segw = 240 if new else 280
    sg = s.panel(x0, y, segw, seg, M["seg_r"], fill="control", parent=root, role="control", group="seg")
    for i, lab in enumerate(("Day", "Night", "Auto")):
        bw = (segw - 2 * M["seg_pad"]) // 3
        if i == 1:
            s.panel(M["seg_pad"] + i * bw, M["seg_pad"], bw, M["seg_btn"], M["seg_in"], fill="card", parent=sg, shadow=None, role="control", group="seg2")
        s.text(sg, M["seg_pad"] + i * bw, M["seg_pad"], bw, M["seg_btn"], lab, 13, 500 if i == 1 else 400, "text", "middle", tree=False)
    y += seg + 16
    # badges
    bx = x0
    for lab, col, w in (("New", "accent", 40), ("Verified", "success", 64), ("Beta", "warning", 40), ("Error", "danger", 44)):
        b = s.panel(bx, y, w, M["badge"], M["badge"] // 2, fill=col, parent=root, opacity=0.22, role="control", group="badges")
        s.text(b, 0, 0, w, M["badge"], lab, 11, 600, "text", "middle", tree=False)
        bx += w + 8
    y += M["badge"] + 16
    # toast
    tw = 336 if new else 300
    t = s.panel(x0, y, tw, 40 if new else 36, 20 if new else 18, fill="glass", opacity=0.9, parent=root, shadow=M["panel_sh"], stroke="line", role="control")
    s.text(t, 16, 0, 200, 40 if new else 36, "Settings saved", 13, 400, "text", tree=False)
    s.text(t, tw - 76, 0, 60, 40 if new else 36, "Undo", 13, 600, "accent_ink", "end", tree=False)
    # ---- right column: card list, sidebar, sheet, panel ----
    cl_h = 3 * M["row"]
    s.text(root, x1, 24, 420, T["head"][1], "Lists", T["head"][0], 600, "text", group="h2")
    cy = 24 + T["head"][1] + 8 + (4 if new else 0)
    cl = s.panel(x1, cy, 420, cl_h, M["card_r"], fill="card", parent=root, shadow=M["card_sh"], stroke="line", role="opening" if False else "box", group="cl")
    rows = [("Wi-Fi", "Wonderland", "chev"), ("Bluetooth", "", "sw"), ("Sound", "72%", "chev")]
    for i, (a, b, k) in enumerate(rows):
        ry = i * M["row"]
        if i:
            s.line(1, ry, 418, 1, "line", parent=cl)
        s.text(cl, 16 if not new else 16, ry, 200, M["row"], a, 13, 400, "text", group="rowt")
        if k == "sw":
            s.switch(cl, 420 - 16 - sw, ry + (M["row"] - sh) // 2, sw, sh, on=True, pad=sp)
        else:
            s.text(cl, 200, ry, 170, M["row"], b, 13, 400, "dim", "end", tree=False)
            s.sym(cl, 420 - 16 - 16 + 4, ry + (M["row"] - 16) // 2, 16, "go-next", "dim")
    # sidebar sample
    sy = cy + cl_h + 24
    s.text(root, x1, sy, 200, T["head"][1], "Sidebar", T["head"][0], 600, "text", group="h2")
    sy += T["head"][1] + 8
    sb = s.panel(x1, sy, 200, 5 * M["side_pitch"] + 16 - (M["side_pitch"] - M["side_row"]), M["card_r"], fill="sidebar", parent=root, role="box", stroke="line")
    for i, (lab, ic) in enumerate((("Wi-Fi", "network-wireless"), ("Bluetooth", "bluetooth-active"), ("Network", "network-workgroup"), ("Sound", "audio-volume-high"), ("Battery", "battery-good"))):
        ry = 8 + i * M["side_pitch"]
        if i == 1:
            s.panel(8, ry, 200 - 16, M["side_row"], 8 if new else 6, fill="accent", parent=sb, opacity=0.18, role="control", group="side")
        s.sym(sb, 16, ry + (M["side_row"] - 16) // 2, 16, ic, "accent_ink")
        s.text(sb, 40, ry, 140, M["side_row"], lab, 13, 500 if i == 1 else 400, "text", group="sidet")
    # sheet + panel
    px = x1 + 220
    s.text(root, px, sy - T["head"][1] - 8, 200, T["head"][1], "Sheet", T["head"][0], 600, "text", group="h2")
    sh_h = 5 * M["side_pitch"] + 16 - (M["side_pitch"] - M["side_row"])
    sp_ = s.panel(px, sy, 200, sh_h, M["card_r"], fill="card", parent=root, shadow=M["sheet_sh"], stroke="line", role="box")
    s.text(sp_, M["sheet_pad"], M["sheet_pad"], 168, T["head"][1], "Erase disk?", T["head"][0], 600, "text")
    s.text(sp_, M["sheet_pad"], M["sheet_pad"] + T["head"][1] + 4, 168, T["body"][1] * 2, "", 13, 400, "dim", lines=["Everything on it", "is removed."], lh=T["body"][1])
    s.button(sp_, 200 - M["sheet_pad"] - 72, sh_h - M["sheet_pad"] - M["ctl"], 72, M["ctl"], "Erase", "destructive", r=M["ctl_r"])
    s.button(sp_, 200 - M["sheet_pad"] - 72 - 8 - 64, sh_h - M["sheet_pad"] - M["ctl"], 64, M["ctl"], "Keep", "default", r=M["ctl_r"])
    # glass panel: a popover-like surface with a heading, a switch row and a slider (right, bottom)
    gh = 168 if new else 160
    gy = 640 - 24 - gh
    gp = s.panel(x1, gy, 420, gh, M["panel_r"], fill="glass", opacity=0.85, parent=root, shadow=M["panel_sh"], stroke="line", rim=M["rim"], role="box")
    s.text(gp, 16, 16, 300, T["head"][1], "Display", T["head"][0], 600, "text")
    s.text(gp, 16, 16 + T["head"][1], 300, T["cap"][1], "Night Light warms the screen after dusk", T["cap"][0], 400, "dim")
    s.switch(gp, 420 - 16 - sw, 16 + (T["head"][1] + T["cap"][1] - sh) // 2, sw, sh, on=True, pad=sp)
    yy = 16 + T["head"][1] + T["cap"][1] + 16
    s.panel(16, yy + (M["ctl"] - tr) // 2, 388, tr, tr // 2, fill="control", parent=gp)
    s.panel(16, yy + (M["ctl"] - tr) // 2, 250, tr, tr // 2, fill="accent", parent=gp)
    s.panel(16 + 250 - th // 2, yy + (M["ctl"] - th) // 2, th, th, th // 2, fill="#ffffff", parent=gp, stroke="line", shadow="e1" if new else "cur-card", role="control")
    # type ladder (left, bottom)
    ty = y + (40 if new else 36) + 24
    s.text(root, x0, ty, 200, T["head"][1], "Type", T["head"][0], 600, "text", group="h")
    ty += T["head"][1] + 8
    for lab, (sz, lh), wt in (("Large title", T["title"], 700), ("Heading", T["head"], 600), ("Body text, the default size", T["body"], 400), ("Caption, secondary", T["cap"], 400)):
        s.text(root, x0, ty, 420, lh, lab, sz, wt, "text" if "Caption" not in lab else "dim", group="ladder")
        ty += lh + 4
    return s
