# -*- coding: utf-8 -*-
"""Chrome writes every image into the PDF as lossless PNG. Re-encode them at the
resolution they are actually drawn at, keeping text and vectors untouched."""
import io, sys, os
import fitz
from PIL import Image

SRC, DST = sys.argv[1], sys.argv[2]
DPI = 170.0          # plenty for a 16:9 slide on screen or in print
Q = 82

doc = fitz.open(SRC)

# how large is each image actually drawn, in points?
drawn = {}
owner = {}
for pno, page in enumerate(doc):
    for info in page.get_image_info(xrefs=True):
        x = info.get("xref")
        if not x:
            continue
        r = fitz.Rect(info["bbox"])
        drawn[x] = max(drawn.get(x, 0), r.width)
        owner.setdefault(x, pno)

done = saved = 0
for xref, wpt in drawn.items():
    try:
        info = doc.extract_image(xref)
    except Exception:
        continue
    raw = info["image"]
    before = len(raw)
    if before < 60_000:                      # small assets aren't worth touching
        continue
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except Exception:
        continue

    has_alpha = im.mode in ("RGBA", "LA", "P") or info.get("smask", 0)
    target_w = max(320, int(wpt / 72.0 * DPI))
    if im.width > target_w:
        im = im.resize((target_w, max(1, round(im.height * target_w / im.width))), Image.LANCZOS)

    buf = io.BytesIO()
    if has_alpha:
        im.convert("RGBA").save(buf, "PNG", optimize=True)
    else:
        im.convert("RGB").save(buf, "JPEG", quality=Q, optimize=True, progressive=True)
    new = buf.getvalue()
    if len(new) >= before:
        continue
    try:
        doc[owner[xref]].replace_image(xref, stream=new)
        done += 1
        saved += before - len(new)
    except Exception as e:
        print("  ! xref", xref, e)

doc.save(DST, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, clean=True)
doc.close()
print("%d imagens recomprimidas, -%.1f MB | %.2f MB -> %.2f MB"
      % (done, saved / 1e6, os.path.getsize(SRC) / 1e6, os.path.getsize(DST) / 1e6))
