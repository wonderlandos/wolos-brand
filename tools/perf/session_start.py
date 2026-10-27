#!/usr/bin/env python3
"""Login -> first full desktop: session_start.py SHELL_LOG -- SESSION_CMD...
Starts the session command (e.g. wol-session) with WOL_SHELL_TIMING=1, then waits for wol-shell's
stderr (SHELL_LOG) to report menu bar, dock and wallpaper mapped; prints ms from launch to the
last of them (CLOCK_MONOTONIC on both sides). Add one frame (~17 ms) for it to be on screen."""
import os, re, subprocess, sys, time

log, cmd = sys.argv[1], sys.argv[sys.argv.index('--') + 1:]
if os.path.exists(log):
    os.remove(log)
t0 = time.monotonic() * 1000
p = subprocess.Popen(cmd, env=dict(os.environ, WOL_SHELL_TIMING='1'),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
want = {'first map': 'menu bar', 'dock map': 'dock', 'wallpaper map': 'wallpaper'}
seen = {}
end = time.monotonic() + 30
while len(seen) < len(want) and time.monotonic() < end:
    time.sleep(0.02)
    try:
        for line in open(log):
            m = re.match(r'wol-shell: (.+?) [\d.]+\S+ at ([\d.]+)', line)
            if m and m.group(1) in want:
                seen[want[m.group(1)]] = float(m.group(2)) - t0
    except FileNotFoundError:
        pass
print(' '.join(f'{k} {v:.0f} ms' for k, v in sorted(seen.items(), key=lambda kv: kv[1])),
      f'| full desktop {max(seen.values()):.0f} ms' if len(seen) == len(want) else '| timed out')
