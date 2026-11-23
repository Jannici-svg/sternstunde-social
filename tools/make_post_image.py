#!/usr/bin/env python3
"""Erzeugt eine Beitragsgrafik (1200x900 PNG) im Sternstunde-Rechenheft-Design.

Aufruf:
  python3 tools/make_post_image.py OUT.png "Zeile 1 Titel" "Zeile 2 Titel (gelb markiert)" \
      --bullets "Punkt 1" "Punkt 2" "Punkt 3"

Benötigt Pillow und die Schrift Poppins (Bold/Medium/Regular). Fallback: DejaVu Sans.
"""
import argparse
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 900
NAVY = "#16255A"
BLUE = "#2747B8"
YELLOW = "#FFD43B"
PAPER = "#F2F5FF"
GRID = "#D3DDF7"
MARGIN_RED = "#E4533F"

FONT_DIRS = ["/usr/share/fonts/truetype/google-fonts", os.path.join(os.path.dirname(__file__), "fonts")]


def font(name, size):
    for d in FONT_DIRS:
        p = os.path.join(d, f"Poppins-{name}.ttf")
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if name == "Bold" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(fb, size)


def star(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def fit(draw, text, name, size, max_w):
    while size > 20:
        f = font(name, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(name, size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("title1")
    ap.add_argument("title2")
    ap.add_argument("--bullets", nargs="*", default=[])
    a = ap.parse_args()

    S = 2  # supersampling
    img = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)

    # Karopapier
    step = 30 * S
    for x in range(0, W * S, step):
        d.line([(x, 0), (x, H * S)], fill=GRID, width=S)
    for y in range(0, H * S, step):
        d.line([(0, y), (W * S, y)], fill=GRID, width=S)
    # roter Heftrand
    d.line([(95 * S, 0), (95 * S, H * S)], fill=MARGIN_RED, width=3 * S)

    x0 = 140 * S

    # Logo: Stern mit Uhrzeigern + Wortmarke
    cx, cy = x0 + 42 * S, 110 * S
    d.polygon(star(cx, cy, 46 * S, 20 * S), fill=YELLOW, outline=NAVY, width=5 * S)
    d.line([(cx, cy + 2 * S), (cx, cy - 20 * S)], fill=NAVY, width=5 * S)
    d.line([(cx, cy + 2 * S), (cx + 14 * S, cy + 10 * S)], fill=NAVY, width=5 * S)
    d.text((x0 + 105 * S, cy), "Sternstunde", font=font("Bold", 52 * S), fill=NAVY, anchor="lm")
    d.text((x0 + 108 * S, cy + 42 * S), "NACHHILFE WIEN", font=font("Medium", 22 * S), fill=BLUE, anchor="lm")

    max_w = (W - 140 - 70) * S

    # Titel
    y = 250 * S
    f1 = fit(d, a.title1, "Bold", 64 * S, max_w)
    d.text((x0, y), a.title1, font=f1, fill=NAVY, anchor="lt")
    y += f1.size + 22 * S
    f2 = fit(d, a.title2, "Bold", 64 * S, max_w - 30 * S)
    tw = d.textlength(a.title2, font=f2)
    d.rounded_rectangle([x0 - 14 * S, y - 6 * S, x0 + tw + 14 * S, y + f2.size + 16 * S], radius=10 * S, fill=YELLOW)
    d.text((x0, y), a.title2, font=f2, fill=NAVY, anchor="lt")
    y += f2.size + 70 * S

    # Punkte
    fb = font("Medium", 38 * S)
    for b in a.bullets[:4]:
        r = 17 * S
        bx, by = x0 + r, y + 26 * S
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=BLUE)
        d.line([(bx - 8 * S, by), (bx - 2 * S, by + 7 * S), (bx + 9 * S, by - 7 * S)], fill="white", width=5 * S, joint="curve")
        d.text((x0 + 55 * S, by), b, font=fit(d, b, "Medium", 38 * S, max_w - 60 * S), fill=NAVY, anchor="lm")
        y += 72 * S

    # Fußband
    d.rectangle([0, (H - 120) * S, W * S, H * S], fill=NAVY)
    d.text((x0, (H - 60) * S), "Damit du wieder an dich glaubst.", font=font("Medium", 34 * S), fill="white", anchor="lm")
    d.text(((W - 60) * S, (H - 60) * S), "stern-stunde.at", font=font("Bold", 34 * S), fill=YELLOW, anchor="rm")

    img = img.resize((W, H), Image.LANCZOS)
    img.save(a.out, "PNG", optimize=True)
    print(a.out)


if __name__ == "__main__":
    main()
