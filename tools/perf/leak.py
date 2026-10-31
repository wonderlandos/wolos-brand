#!/usr/bin/env python3
"""Open/close loops -> RSS growth. Run inside the session (in.sh). leak.py [N=200]
Control Center and the switcher live in wol-shell: its RSS is compared before/after.
Search is a process per open: checks every instance exited (no accumulation)."""
import os, subprocess, sys, time

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
sh = lambda *c: subprocess.run(list(c), capture_output=True)


def pid(name):
    out = subprocess.run(['pgrep', '-x', name], capture_output=True, text=True).stdout.split()
    return out[0] if out else None


def rss(p):
    return next(int(l.split()[1]) for l in open(f'/proc/{p}/status') if l.startswith('VmRSS')) / 1024


shell = pid('wol-shell')
# Warm up once: first open allocates caches (CSS, icons) that are not leaks.
for verb in ('show', 'hide'):
    sh('wol', 'shell', verb, 'control-center'); sh('wol', 'shell', verb, 'switcher'); time.sleep(0.3)
time.sleep(1)
base = rss(shell)
for _ in range(N):
    sh('wol', 'shell', 'show', 'control-center'); time.sleep(0.05)
    sh('wol', 'shell', 'hide', 'control-center'); time.sleep(0.05)
time.sleep(2)
cc = rss(shell)
for _ in range(N):
    sh('wol', 'shell', 'show', 'switcher'); time.sleep(0.05)
    sh('wol', 'shell', 'hide', 'switcher'); time.sleep(0.05)
time.sleep(2)
sw = rss(shell)
alive = 0
for _ in range(N):
    p = subprocess.Popen(['wol-search'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.15)
    sh('vk', '-k', 'Escape')
    try:
        p.wait(2)
    except subprocess.TimeoutExpired:
        alive += 1
        p.kill()
print(f'wol-shell RSS MB: start {base:.1f}  after {N} control center {cc:.1f} (+{cc-base:.1f})'
      f'  after {N} switcher {sw:.1f} (+{sw-cc:.1f})')
print(f'searchbar: {N} launches, {alive} did not exit; leftover processes: {pid("wol-search") or 0}')
