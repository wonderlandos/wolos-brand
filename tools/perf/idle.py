#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Idle cost per process: idle.py SECONDS NAME... -> CPU ms/s, children ms/s, wakeups/s, RSS MB.
Children = cutime+cstime of reaped helper processes (pactl, nmcli, ...) the process spawned.
CPU = sum of /proc/PID/task/*/schedstat run time (ns). Wakeups = voluntary + involuntary
context switches of all threads (each switch-in after sleep is a wakeup). No input during the run."""
import os, sys, time


def pids(name):
    out = []
    for p in os.listdir('/proc'):
        if p.isdigit():
            try:
                if open(f'/proc/{p}/comm').read().strip() == name:
                    out.append(p)
            except OSError:
                pass
    return out


def sample(pid):
    cpu = sw = 0
    for t in os.listdir(f'/proc/{pid}/task'):
        try:
            cpu += int(open(f'/proc/{pid}/task/{t}/schedstat').read().split()[0])
            for l in open(f'/proc/{pid}/task/{t}/status'):
                if l.startswith(('voluntary_ctxt_switches', 'nonvoluntary_ctxt_switches')):
                    sw += int(l.split()[1])
        except OSError:
            pass
    rss = next(int(l.split()[1]) for l in open(f'/proc/{pid}/status') if l.startswith('VmRSS'))
    st = open(f'/proc/{pid}/stat').read().rsplit(')', 1)[1].split()
    kids = (int(st[13]) + int(st[14])) * 1000 // os.sysconf('SC_CLK_TCK')  # ms
    return cpu, sw, rss, kids


def main():
    secs = float(sys.argv[1])
    procs = {n: pids(n) for n in sys.argv[2:]}
    a = {p: sample(p) for ps in procs.values() for p in ps}
    time.sleep(secs)
    print(f'{"process":<20}{"cpu ms/s":>10}{"kids ms/s":>10}{"wakeups/s":>11}{"rss MB":>9}')
    for n, ps in procs.items():
        if not ps:
            print(f'{n:<20}{"not running":>30}')
        for p in ps:
            b = sample(p)
            print(f'{n:<20}{(b[0]-a[p][0])/1e6/secs:>10.2f}{(b[3]-a[p][3])/secs:>10.2f}{(b[1]-a[p][1])/secs:>11.2f}{b[2]/1024:>9.1f}')


main()
