"""
Build PWA icons for the UAGLAX site.
Source: ../ScreenShot2022-10-23at9.28.28AM.webp  (golden bear + GOLDEN BEARS text
  on a checkered transparency-placeholder gray background)
Output: icon-{size}.png at standard PWA sizes, black background.
"""
from PIL import Image
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE.parent / "ScreenShot2022-10-23at9.28.28AM.webp"

# ---- 1. Load & key out the checker background ----
im = Image.open(SRC).convert("RGB")
px = im.load()
W, H = im.size

# Build an alpha mask: near-neutral light pixels (the checker) -> transparent.
# Foreground = gold (saturated), black (dark), and the thin highlights on top.
mask = Image.new("L", (W, H), 0)
mpx = mask.load()
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        mx = max(r, g, b); mn = min(r, g, b)
        sat = mx - mn
        # "Checker" pixels: near-grayscale (low sat) and bright.
        if sat < 18 and mx > 200:
            mpx[x, y] = 0
        else:
            mpx[x, y] = 255

rgba = im.convert("RGBA")
rgba.putalpha(mask)

# ---- 2. Tight crop to content bounding box ----
bbox = rgba.getbbox()
cropped = rgba.crop(bbox)
cw, ch = cropped.size

# ---- 3. Build square icons on black ----
SIZES = [72, 96, 128, 144, 152, 180, 192, 384, 512]
PAD_RATIO = 0.10  # 10% padding around the content

for size in SIZES:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    inner = int(size * (1 - 2 * PAD_RATIO))
    # Fit content inside the inner square while preserving aspect ratio.
    scale = min(inner / cw, inner / ch)
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch * scale))
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)
    ox = (size - new_w) // 2
    oy = (size - new_h) // 2
    canvas.paste(resized, (ox, oy), resized)
    out = HERE / f"icon-{size}.png"
    canvas.convert("RGB").save(out, "PNG", optimize=True)
    print(f"wrote {out.name}  {size}x{size}")

# Favicon (16 & 32)
for size in (16, 32):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    inner = int(size * (1 - 2 * PAD_RATIO))
    scale = min(inner / cw, inner / ch)
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch * scale))
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)
    ox = (size - new_w) // 2
    oy = (size - new_h) // 2
    canvas.paste(resized, (ox, oy), resized)
    canvas.convert("RGB").save(HERE / f"favicon-{size}.png", "PNG", optimize=True)
    print(f"wrote favicon-{size}.png")

print("done")
