# -*- coding: utf-8 -*-
"""Build the three deliverables from clube-apresentacao/.

Assets are inlined as data URIs. Two economies keep the files sane:
  * an image used on more than one slide is inlined ONCE — the repeats carry
    data-same and a three-line script copies the src across after parse;
  * the projection video is too big to inline at full quality, so the standalone
    file gets the 1200px encode from build-assets/ and the artifact keeps the
    1600px file as a separate published file.
"""
import re, io, base64, os, shutil

SRC = "clube-apresentacao"
VIDEOS = {"assets/projecao.mp4": "build-assets/projecao-lite.mp4",       # referenced in index.html -> lite for the standalone
          "assets/hero-cartao.mp4": "build-assets/hero-cartao-lite.mp4"}
VIDEO = "assets/projecao.mp4"

s = io.open(os.path.join(SRC, "index.html"), encoding="utf-8").read()

MT = {"webp": "image/webp", "jpg": "image/jpeg", "png": "image/png",
      "svg": "image/svg+xml", "woff2": "font/woff2", "mp4": "video/mp4"}

def data_uri(rel, path=None):
    ext = rel.rsplit(".", 1)[1]
    with open(path or os.path.join(SRC, rel), "rb") as f:
        return "data:%s;base64," % MT[ext] + base64.b64encode(f.read()).decode()

# --- mark repeated <img> so each file is inlined only once -----------------
seen = set()
def mark(m):
    tag, name = m.group(0), m.group(1)
    if name in seen:
        return re.sub(r'\s*src="assets/[^"]+"', ' data-same="%s"' % name, tag)
    seen.add(name)
    return tag.replace('src="assets/%s"' % name, 'src="assets/%s" data-a="%s"' % (name, name))

dedup = re.sub(r'<img [^>]*src="assets/([^"]+)"[^>]*>', mark, s)

RESTORE = ("<script>(function(){var q=document.querySelectorAll('img[data-same]');"
           "for(var i=0;i<q.length;i++){var o=document.querySelector('img[data-a=\"'+q[i].getAttribute('data-same')+'\"]');"
           "if(o)q[i].src=o.src;}})();</script>\n</body>")
assert "\n</body>" in dedup
dedup = dedup.replace("\n</body>", "\n" + RESTORE, 1)

ASSET_RE = r"(?<=['\"(])assets/([^'\")]+)(?=['\")])"

def inline(html, keep=(), swap=None):
    """keep: paths left as relative URLs. swap: {asset path: local file to use}."""
    def sub(m):
        rel = "assets/" + m.group(1)
        if rel in keep:
            return rel
        return data_uri(rel, (swap or {}).get(rel))
    out = re.sub(ASSET_RE, sub, html)
    return re.sub(r'<meta property="og:image" content="data:[^"]+">\n', '', out)

def strip_wrappers(html):
    return (re.sub(r'^.*?<head>', '', html, flags=re.S)
            .replace('<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n', '')
            .replace('</head>\n<body>', '').replace('</body>\n</html>', ''))

# 1. standalone single file — everything inlined, lighter video
standalone = inline(dedup, swap=VIDEOS)
io.open("CLUBE-parceiros-2026.html", "w", encoding="utf-8").write(standalone)

# 2. artifact body — video published alongside as its own file
artifact = strip_wrappers(inline(dedup, keep=set(VIDEOS)))
io.open("clube-apresentacao-artifact.html", "w", encoding="utf-8").write(artifact)

# 3. PDF version — frozen, one slide per page, galleries expanded.
#    The video never plays here, so its bytes are dropped and the poster stands in.
pdf_src = dedup.replace("<body>", '<body class="pdf">', 1)
for _v in VIDEOS: pdf_src = pdf_src.replace(' src="%s"' % _v, "")
pdf_html = inline(pdf_src)
io.open("CLUBE-parceiros-2026-PDF.html", "w", encoding="utf-8").write(pdf_html)

# 4. folder version
if os.path.exists("CLUBE-parceiros-2026-pasta.zip"):
    os.remove("CLUBE-parceiros-2026-pasta.zip")
# o zip vai para fora: nada de credenciais nem de configuração de deploy dentro dele
SKIP_DIRS = {".vercel", "card-lab", "__pycache__"}
SKIP_FILES = {".vercelignore", "vercel.json"}
import zipfile
with zipfile.ZipFile("CLUBE-parceiros-2026-pasta.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES or f.startswith(".env"):
                continue
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, SRC))

print("standalone %.2f MB | artifact %.2f MB (+ vídeo %.2f MB) | PDF-html %.2f MB | zip %.2f MB | %d imagens reaproveitadas"
      % (len(standalone.encode("utf-8")) / 1e6,
         len(artifact.encode("utf-8")) / 1e6,
         os.path.getsize(os.path.join(SRC, VIDEO)) / 1e6,
         len(pdf_html.encode("utf-8")) / 1e6,
         os.path.getsize("CLUBE-parceiros-2026-pasta.zip") / 1e6,
         len(re.findall(r'data-same=', dedup))))
