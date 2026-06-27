#!/usr/bin/env python3
"""
Generate og-image.png (1200x630) — the Daxchain Open Graph / Twitter social card.

Paths resolve relative to the repo root, so it can be run from anywhere:

    python3 -m venv .venv && .venv/bin/pip install Pillow
    .venv/bin/python scripts/gen_og.py

Reads logo.png (the Daxchain cube) and writes og-image.png in the repo root.
Re-run this whenever the project chips or headline change, then commit the PNG.

Note: uses macOS system fonts (Helvetica Neue, Menlo). On other platforms, point
HN / MEN below at equivalent .ttf/.ttc files.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, "logo.png")
OUT = os.path.join(ROOT, "og-image.png")

W, H = 1200, 630
MARGIN = 72

# Palette (from index.html :root)
BG      = (5, 6, 7)
FG      = (246, 248, 237)
MUTED   = (154, 165, 147)
QUIET   = (104, 114, 99)
GREEN   = (140, 255, 153)
BLUE    = (98, 215, 255)
YELLOW  = (247, 213, 107)
ORANGE  = (247, 147, 26)

HN  = "/System/Library/Fonts/HelveticaNeue.ttc"
MEN = "/System/Library/Fonts/Menlo.ttc"

def find_face(path, want, avoid=()):
    """Return a TTC face index whose name matches `want` and avoids `avoid`."""
    for i in range(20):
        try:
            f = ImageFont.truetype(path, 16, index=i)
        except Exception:
            break
        name = " ".join(x for x in f.getname()).lower()
        if want in name and all(a not in name for a in avoid):
            return i
    return 0

HN_BOLD = find_face(HN, "bold", avoid=("condensed", "italic", "light"))
HN_REG  = find_face(HN, "helvetica neue", avoid=("bold", "italic", "light", "condensed", "medium"))
MEN_BOLD = find_face(MEN, "bold", avoid=("italic",))
MEN_REG  = find_face(MEN, "regular", avoid=("bold", "italic"))

def hn_bold(sz):  return ImageFont.truetype(HN, sz, index=HN_BOLD)
def hn_reg(sz):   return ImageFont.truetype(HN, sz, index=HN_REG)
def men_bold(sz): return ImageFont.truetype(MEN, sz, index=MEN_BOLD)
def men_reg(sz):  return ImageFont.truetype(MEN, sz, index=MEN_REG)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img, "RGBA")

# --- faint 42px grid ---
for x in range(0, W, 42):
    draw.line([(x, 0), (x, H)], fill=(140, 255, 153, 8), width=1)
for y in range(0, H, 42):
    draw.line([(0, y), (W, y)], fill=(98, 215, 255, 7), width=1)

# --- soft radial glows (blurred ellipses on an overlay) ---
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-160, -200, 520, 380], fill=(140, 255, 153, 60))    # green, top-left
gd.ellipse([820, 300, 1400, 820], fill=(247, 213, 107, 42))     # yellow, bottom-right
glow = glow.filter(ImageFilter.GaussianBlur(120))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# --- brand cube logo ---
logo = Image.open(LOGO).convert("RGBA")

def faded(im, factor):
    r, g, b, a = im.split()
    a = a.point(lambda v: int(v * factor))
    return Image.merge("RGBA", (r, g, b, a))

# large watermark cube, upper-right, sitting above the headline
big = logo.resize((250, 250), Image.LANCZOS)
img.paste(faded(big, 0.9), (905, 18), faded(big, 0.9))
draw = ImageDraw.Draw(img, "RGBA")

# --- diagonal blue trace ---
draw.line([(int(W*0.50), int(H*0.30)), (int(W*0.62), int(H*0.20))],
          fill=(98, 215, 255, 70), width=2)
draw.ellipse([int(W*0.50)-6, int(H*0.30)-6, int(W*0.50)+6, int(H*0.30)+6],
             fill=(140, 255, 153, 230))

# --- header: cube mark + wordmark ---
mark = 60
mx, my = MARGIN, MARGIN
small = logo.resize((mark, mark), Image.LANCZOS)
img.paste(small, (mx, my), small)
draw = ImageDraw.Draw(img, "RGBA")

tx = mx + mark + 20
draw.text((tx, my + 6), "Daxchain", font=hn_bold(30), fill=FG)
draw.text((tx, my + 38), "O N - C H A I N   T O O L S", font=men_bold(14), fill=QUIET)

# --- headline (two lines) ---
hf = hn_bold(106)
hy = 214
draw.text((MARGIN, hy), "Small lab.", font=hf, fill=FG)
draw.text((MARGIN, hy + 112), "Sharp tools.", font=hf, fill=FG)

# --- intro ---
intro = "Practical Ethereum tooling and token experiments"
draw.text((MARGIN, hy + 232), intro, font=hn_reg(29), fill=MUTED)

# --- project chips along the bottom (last one muted = deprecated) ---
projects = [
    ("Daxie", GREEN, FG),
    ("Daxib", ORANGE, FG),
    ("EVM Tools", YELLOW, FG),
    ("NZT-48", BLUE, FG),
    ("Blockchain Exporter", QUIET, MUTED),
]
pf = men_bold(20)
sf = men_reg(20)
px = MARGIN
py = H - MARGIN - 14
for i, (name, dotc, textc) in enumerate(projects):
    if i:
        draw.text((px, py), "/", font=sf, fill=QUIET)
        px += draw.textlength("/", font=sf) + 13
    r = 5
    cy = py + 12
    draw.ellipse([px, cy-r, px+2*r, cy+r], fill=dotc)
    px += 2*r + 10
    draw.text((px, py), name, font=pf, fill=textc)
    px += draw.textlength(name, font=pf) + 17

# --- domain, bottom-right ---
df = men_bold(20)
dom = "daxchain.io"
dw = draw.textlength(dom, font=df)
draw.text((W - MARGIN - dw, py), dom, font=df, fill=GREEN)

img.save(OUT, "PNG")
print("wrote", OUT, img.size)
