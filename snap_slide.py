# -*- coding: utf-8 -*-
"""Captura um slide do deck em tamanho exato, via Chrome headless + DevTools.
uso: python snap_slide.py <id-do-slide> <largura> <altura> <saida.png> [url]"""
import asyncio, base64, json, os, subprocess, sys, tempfile, shutil, urllib.request, time
import websockets

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9344
SID, W, H, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), os.path.abspath(sys.argv[4])
URL = sys.argv[5] if len(sys.argv) > 5 else "http://localhost:8765/index.html"

prof = tempfile.mkdtemp(prefix="chrsnap")
proc = subprocess.Popen(
    [CHROME, "--headless=new", "--enable-unsafe-swiftshader", "--hide-scrollbars", "--force-device-scale-factor=1",
     "--remote-debugging-port=%d" % PORT, "--user-data-dir=" + prof, "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ws_url = None
for _ in range(60):
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT, timeout=5) as r:
            for t in json.load(r):
                if t.get("type") == "page": ws_url = t["webSocketDebuggerUrl"]; break
        if ws_url: break
    except Exception:
        pass
    time.sleep(0.4)
if not ws_url:
    proc.kill(); shutil.rmtree(prof, ignore_errors=True); raise SystemExit("Chrome não abriu")

GO = "const d=document.querySelector('.deck');d.style.scrollSnapType='none';d.style.scrollBehavior='auto';document.documentElement.style.scrollBehavior='auto';const s=document.getElementById(%s);const inner=d.scrollHeight>d.clientHeight+2;const top=inner?s.offsetTop:(s.getBoundingClientRect().top+window.scrollY);if(inner){d.scrollTop=top+(%s);}else{window.scrollTo(0,top+(%s));}"

JS = """
(async () => {
  const d = document.querySelector('.deck'); d.style.scrollBehavior = 'auto';
  const s = document.getElementById(%s); if (!s) return 'slide não encontrado';
  const st = document.createElement('style');
  st.textContent = '#' + s.id + ' .blk, #' + s.id + ' .head, #' + s.id + ' .h1 {opacity:1 !important; animation:none !important}';
  document.head.appendChild(st);
  s.querySelectorAll('img').forEach(i => { i.loading = 'eager'; });
  const inner = d.scrollHeight > d.clientHeight + 2;
  const go = () => { if (inner) d.scrollTop = s.offsetTop; else window.scrollTo(0, s.getBoundingClientRect().top + window.scrollY); };
  document.documentElement.style.scrollBehavior = 'auto'; d.style.scrollSnapType = 'none';
  go(); s.classList.add('entered');
  await Promise.all([...s.querySelectorAll('img')].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 6000); })));
  window.__fitM17 && window.__fitM17(); window.__refit && window.__refit();
  await new Promise(r => setTimeout(r, 2500));
  go(); await new Promise(r => setTimeout(r, 300));
  const r = s.getBoundingClientRect();
  const wide = [...s.querySelectorAll('*')].filter(e => e.getBoundingClientRect().right > innerWidth + 1 && getComputedStyle(e).position !== 'fixed').length;
  return JSON.stringify({vw: innerWidth, vh: innerHeight, slideH: Math.round(r.height), docScrollW: document.documentElement.scrollWidth, slideScrollW: s.scrollWidth, elementosVazando: wide});
})()
""" % json.dumps(SID)


async def run():
    async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
        n = 0
        async def cmd(method, params=None):
            nonlocal n
            n += 1
            await ws.send(json.dumps({"id": n, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == n:
                    if "error" in msg: raise RuntimeError(method + ": " + json.dumps(msg["error"]))
                    return msg.get("result", {})
        await cmd("Page.enable")
        await cmd("Emulation.setDeviceMetricsOverride", {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
        await cmd("Page.navigate", {"url": URL})
        await asyncio.sleep(3.5)
        r = await cmd("Runtime.evaluate", {"expression": JS, "awaitPromise": True, "returnByValue": True})
        val = r.get("result", {}).get("value"); print(val)
        try: sh = json.loads(val).get("slideH", H)
        except Exception: sh = H
        if sh > H + 4:                                   # slide mais alto que a janela (celular): fotografa em passos e costura
            from PIL import Image
            import io as _io
            partes, y = [], 0
            while True:
                await cmd("Runtime.evaluate", {"expression": "(()=>{" + GO % (json.dumps(SID), y, y) + "})()"})
                await asyncio.sleep(0.9)
                sh1 = await cmd("Page.captureScreenshot", {"format": "png"})
                partes.append((y, Image.open(_io.BytesIO(base64.b64decode(sh1["data"]))).convert("RGB")))
                if y + H >= sh: break
                y = min(y + H, int(sh) - H)
            full = Image.new("RGB", (W, int(sh)), "black")
            for yy, im in partes: full.paste(im, (0, yy))
            full.save(OUT); return
        shot = await cmd("Page.captureScreenshot", {"format": "png"})
        open(OUT, "wb").write(base64.b64decode(shot["data"]))

try:
    asyncio.run(run())
finally:
    proc.kill(); time.sleep(0.5); shutil.rmtree(prof, ignore_errors=True)
print("salvo:", OUT)
