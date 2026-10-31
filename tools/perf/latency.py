#!/usr/bin/env python3
"""Input -> first visibly changed frame, per interaction, in a running session.
Run inside the session (in.sh / WAYLAND_DISPLAY set) with `dmg`, `vk`, `vp` from build.sh on PATH.
latency.py [RUNS] -> median and p95 ms.

`vk`/`vp` print the monotonic ms they send the input (STAMP=1); other commands are stamped at
spawn. `dmg X Y W H` prints a pixel hash of the region the surface appears in for every new
frame (Hyprland reports full damage per screencopy frame, so damage rects cannot be used).
Latency = first frame after the stamp whose region hash differs from the last one before it."""
import os, statistics, subprocess, sys, threading, time

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
env = dict(os.environ, STAMP='1')
sh = lambda *c: subprocess.run(list(c), capture_output=True)


class Region:
    def __init__(self, x, y, w, h):
        self.frames, self.lock = [], threading.Lock()
        self.p = subprocess.Popen(['dmg', str(x), str(y), str(w), str(h)], stdout=subprocess.PIPE, text=True)
        threading.Thread(target=self.read, daemon=True).start()

    def read(self):
        for line in self.p.stdout:
            t, h = line.split()
            with self.lock:
                self.frames.append((float(t), h))

    def latency(self, t, timeout=1.0):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            with self.lock:
                before = [h for f, h in self.frames if f <= t]
                after = [(f, h) for f, h in self.frames if f > t]
            base = before[-1] if before else None
            hit = [f for f, h in after if h != base]
            if hit:
                return hit[0] - t
            time.sleep(0.005)
        return None


def stamp(cmd):
    if cmd[0] in ('vk', 'vp'):
        return float(subprocess.run(cmd, env=env, capture_output=True, text=True).stderr.split()[0])
    t = time.monotonic() * 1000
    subprocess.run(cmd, capture_output=True)
    return t


def run(name, region, open_cmd, close, settle=0.6):
    r = Region(*region)
    time.sleep(0.5)
    xs = []
    for _ in range(RUNS):
        time.sleep(settle)
        d = r.latency(stamp(open_cmd))
        if d is not None:
            xs.append(d)
        time.sleep(0.3)
        close()
    r.p.kill()
    xs.sort()
    med = statistics.median(xs) if xs else float('nan')
    p95 = xs[min(len(xs) - 1, int(len(xs) * 0.95))] if xs else float('nan')
    print(f'{name:<22}{med:>8.1f}{p95:>8.1f}{len(xs):>5}/{RUNS}', flush=True)


print(f'{"interaction":<22}{"median":>8}{"p95":>8}{"n":>6}  (ms, input -> first changed frame)')
sh('vk', '-d', 'Super_L')
run('switcher Super+Tab', (340, 300, 600, 200), ['vk', '-k', 'Tab', 'super'],
    lambda: (sh('vk', '-u', 'Super_L'), time.sleep(0.3), sh('vk', '-d', 'Super_L')))
sh('vk', '-u', 'Super_L')
sh('vp', 'move', '1140', '14')  # park the pointer: motion repaints the software cursor
run('control center click', (800, 60, 440, 320), ['vp', 'click', '1140', '14'], lambda: sh('vk', '-k', 'Escape'), 1.0)
run('overview', (100, 100, 1080, 500), ['vk', '-k', 'Up', 'super'], lambda: sh('vk', '-k', 'Escape'), 1.0)
run('volume OSD', (515, 552, 250, 34), ['wol', 'shell', 'show', 'osd'], lambda: sh('wol', 'shell', 'hide', 'osd'), 2.0)
sh('vk', '-k', 'space', 'super')
time.sleep(1.5)
run('searchbar keystroke', (333, 270, 614, 360), ['vk', 't'], lambda: sh('vk', '-k', 'BackSpace'), 0.4)
sh('vk', '-k', 'Escape')
