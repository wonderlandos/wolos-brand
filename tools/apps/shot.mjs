// SPDX-License-Identifier: GPL-2.0-or-later
// Screenshot a broadway session with headless Chromium over CDP; optional click (focus/select) first.
// usage: CHROME=<chrome-headless-shell> node shot.mjs <url> <out.png> <w> <h> <waitms> [x,y | select-all ...]
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const [url, out, w, h, wait, ...clicks] = process.argv.slice(2);
const port = 9300 + Math.floor(Math.random() * 500);
const p = spawn(process.env.CHROME, ['--headless', '--disable-gpu', `--remote-debugging-port=${port}`, `--window-size=${w},${h}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let list;
for (let i = 0; i < 50; i++) { try { list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await sleep(100); } }
const ws = new WebSocket(list.find(x => x.type === 'page').webSocketDebuggerUrl);
await new Promise(r => (ws.onopen = r));
let id = 0; const pend = {};
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; } };
const call = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
await call('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: 1, mobile: false });
await call('Page.navigate', { url });
await sleep(+wait);
for (const c of clicks) {
  if (c === 'select-all') { // Ctrl+A
    for (const type of ['keyDown', 'keyUp'])
      await call('Input.dispatchKeyEvent', { type, modifiers: 2, key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65 });
    await sleep(800);
    continue;
  }
  const [x, y] = c.split(',').map(Number);
  for (const type of ['mousePressed', 'mouseReleased'])
    await call('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 });
  await sleep(800);
}
const r = await call('Page.captureScreenshot', { format: 'png' });
writeFileSync(out, Buffer.from(r.data, 'base64'));
ws.close(); p.kill(); process.exit(0);
