# -*- coding: utf-8 -*-
"""Render the PDF build of the deck through Chrome's DevTools protocol.

Printing all 41 slides in one pass makes Chrome shrink-to-fit the whole document
(every page comes out at 86% with a white margin), so each slide is printed on
its own — one page load, one printToPDF per slide — and the pages are merged.
"""
import asyncio, base64, json, os, subprocess, sys, tempfile, shutil, urllib.request, time
import websockets
import fitz

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9333
HTML = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "CLUBE-parceiros-2026-PDF.html")
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "_raw.pdf")
SETTLE = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0

url = "file:///" + HTML.replace("\\", "/").replace(" ", "%20")
prof = tempfile.mkdtemp(prefix="chrpdf")
proc = subprocess.Popen(
    [CHROME, "--headless=new", "--disable-gpu", "--enable-unsafe-swiftshader",
     "--allow-file-access-from-files", "--hide-scrollbars", "--force-device-scale-factor=1",
     "--remote-debugging-port=%d" % PORT, "--user-data-dir=" + prof, "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ws_url = None
for _ in range(60):
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT, timeout=5) as r:
            for t in json.load(r):
                if t.get("type") == "page":
                    ws_url = t["webSocketDebuggerUrl"]; break
        if ws_url:
            break
    except Exception:
        pass
    time.sleep(0.5)
if not ws_url:
    proc.kill(); shutil.rmtree(prof, ignore_errors=True); raise SystemExit("Chrome não abriu")

PAGE = {"printBackground": True,
        "paperWidth": 1280 / 96.0, "paperHeight": 720 / 96.0,
        "marginTop": 0, "marginBottom": 0, "marginLeft": 0, "marginRight": 0,
        "preferCSSPageSize": False, "scale": 1, "transferMode": "ReturnAsBase64"}

async def run():
    pages = []
    async with websockets.connect(ws_url, max_size=None, ping_interval=None) as ws:
        n = 0
        async def cmd(method, params=None):
            nonlocal n
            n += 1
            await ws.send(json.dumps({"id": n, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == n:
                    if "error" in msg:
                        raise RuntimeError(method + ": " + json.dumps(msg["error"]))
                    return msg.get("result", {})

        async def js(expr):
            r = await cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            return r.get("result", {}).get("value")

        await cmd("Emulation.setDeviceMetricsOverride",
                  {"width": 1280, "height": 720, "deviceScaleFactor": 1, "mobile": False})
        await cmd("Page.enable")
        await cmd("Runtime.enable")
        await cmd("Page.navigate", {"url": url})
        await asyncio.sleep(SETTLE)

        total = await js("document.querySelectorAll('.slide').length")
        print("slides:", total, flush=True)
        for i in range(total):
            await js("(function(){var s=document.querySelectorAll('.slide');"
                     "for(var k=0;k<s.length;k++)s[k].style.display=(k===%d?'':'none');return 1})()" % i)
            await js("(window.__fitM17&&window.__fitM17(),window.__refit&&window.__refit(),1)")
            await asyncio.sleep(0.15)
            res = await cmd("Page.printToPDF", PAGE)
            pages.append(base64.b64decode(res["data"]))
            if (i + 1) % 10 == 0:
                print("  %d/%d" % (i + 1, total), flush=True)
    return pages

try:
    pages = asyncio.run(run())
finally:
    proc.kill(); shutil.rmtree(prof, ignore_errors=True)

doc = fitz.open()
for b in pages:
    one = fitz.open("pdf", b)
    doc.insert_pdf(one, from_page=0, to_page=0)   # one slide = one page
    one.close()
doc.save(OUT, garbage=3, deflate=True)
doc.close()

d = fitz.open(OUT)
print("%s  %d páginas  %.1f MB  página %s"
      % (OUT, d.page_count, os.path.getsize(OUT) / 1e6, [round(x) for x in d[0].rect[2:]]))
