"""cutest-picture-01 entry (Python 3.13, standard library + Pillow).

Draws Mochi, a chubby baby bunny holding a strawberry, entirely from
code: soft pastel sky, fluffy clouds, a grassy hill, big sparkly eyes,
pink cheeks, a floppy ear, a little bow and floating hearts.

Deterministic by construction: fixed constants only, no randomness, no
time, no network. Every run draws the same pixels and writes the same
PNG bytes to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
"""

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 1024
SS = 4  # supersample factor: draw at 4096, downscale for smooth edges
W = SIZE * SS

SKY_TOP = (174, 227, 255)
SKY_MID = (223, 243, 255)
SKY_BOT = (255, 233, 242)
SUN = (255, 217, 61)
SUN_HALO = (255, 236, 150)
CLOUD = (255, 255, 255)
GRASS = (168, 230, 161)
GRASS_DARK = (143, 214, 138)
CREAM = (255, 246, 236)
CREAM_SHADE = (250, 228, 205)
OUTLINE = (222, 178, 140)
EAR_PINK = (255, 179, 199)
EYE = (59, 42, 32)
BLUSH = (255, 158, 187)
NOSE = (255, 122, 158)
BOW = (255, 143, 176)
BOW_DARK = (240, 110, 150)
STRAW = (255, 90, 110)
STRAW_DARK = (230, 60, 85)
SEED = (255, 233, 168)
LEAF = (88, 179, 104)
LEAF_DARK = (66, 150, 84)
HEART = (255, 143, 176)
HEART_SOFT = (255, 183, 205)
WHITE = (255, 255, 255)


def s(v):
    """Scale a 1024-space coordinate to supersampled space."""
    return v * SS


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ell(d, cx, cy, rx, ry, fill, outline=None, width=0):
    d.ellipse([s(cx - rx), s(cy - ry), s(cx + rx), s(cy + ry)],
              fill=fill, outline=outline, width=s(width) if width else 1)


def circle(d, cx, cy, r, fill, outline=None, width=0):
    ell(d, cx, cy, r, r, fill, outline, width)


def poly(d, pts, fill, outline=None):
    d.polygon([(s(x), s(y)) for x, y in pts], fill=fill, outline=outline)


def heart(d, cx, cy, size, fill):
    """A heart centred at (cx, cy), size = half-width."""
    r = size * 0.52
    circle(d, cx - r, cy - size * 0.18, r, fill)
    circle(d, cx + r, cy - size * 0.18, r, fill)
    poly(d, [(cx - size, cy - size * 0.05), (cx + size, cy - size * 0.05),
             (cx, cy + size * 0.95)], fill)


def cloud(d, x, y, scale):
    circle(d, x, y, 46 * scale, CLOUD)
    circle(d, x + 48 * scale, y + 8 * scale, 38 * scale, CLOUD)
    circle(d, x - 48 * scale, y + 10 * scale, 34 * scale, CLOUD)
    ell(d, x, y + 14 * scale, 78 * scale, 26 * scale, CLOUD)


def flower(d, x, y, scale, petal, centre):
    for k in range(5):
        ang = -math.pi / 2 + k * 2 * math.pi / 5
        px = x + math.cos(ang) * 13 * scale
        py = y + math.sin(ang) * 13 * scale
        circle(d, px, py, 11 * scale, petal)
    circle(d, x, y, 9 * scale, centre)


def sparkle(d, x, y, size, fill):
    poly(d, [(x, y - size), (x + size * 0.28, y - size * 0.28),
             (x + size, y), (x + size * 0.28, y + size * 0.28),
             (x, y + size), (x - size * 0.28, y + size * 0.28),
             (x - size, y), (x - size * 0.28, y - size * 0.28)], fill)


def rotated_ellipse(img, cx, cy, rx, ry, angle, fill, outline, width):
    """Draw an ellipse on its own layer, rotate it, paste it back."""
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([s(cx - rx), s(cy - ry), s(cx + rx), s(cy + ry)],
               fill=fill + (255,),
               outline=(outline + (255,)) if outline else None,
               width=s(width) if width else 1)
    layer = layer.rotate(angle, center=(s(cx), s(cy)),
                         resample=Image.BICUBIC)
    img.alpha_composite(layer)


def draw_background(img):
    d = ImageDraw.Draw(img)
    for i in range(256):
        t = i / 255
        if t < 0.55:
            col = lerp(SKY_TOP, SKY_MID, t / 0.55)
        else:
            col = lerp(SKY_MID, SKY_BOT, (t - 0.55) / 0.45)
        d.rectangle([0, s(i * 4), W, s(i * 4 + 4)], fill=col)
    circle(d, 845, 150, 95, SUN_HALO)
    circle(d, 845, 150, 62, SUN)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1 = 845 + math.cos(rad) * 82
        y1 = 150 + math.sin(rad) * 82
        x2 = 845 + math.cos(rad) * 104
        y2 = 150 + math.sin(rad) * 104
        d.line([s(x1), s(y1), s(x2), s(y2)], fill=SUN, width=s(7))
    circle(d, 845, 150, 62, SUN)
    cloud(d, 210, 170, 1.0)
    cloud(d, 700, 90, 0.7)
    cloud(d, 120, 330, 0.6)
    cloud(d, 900, 330, 0.55)
    ell(d, 512, 1300, 820, 330, GRASS)
    ell(d, 512, 1292, 820, 330, GRASS_DARK)
    ell(d, 512, 1300, 820, 330, GRASS)


def draw_bunny(img):
    d = ImageDraw.Draw(img)
    # Ears (behind the head). Left ear stands up, right ear flops out.
    rotated_ellipse(img, 408, 215, 62, 165, -13, CREAM, OUTLINE, 5)
    rotated_ellipse(img, 408, 215, 34, 128, -13, EAR_PINK, None, 0)
    rotated_ellipse(img, 648, 262, 62, 165, -52, CREAM, OUTLINE, 5)
    rotated_ellipse(img, 648, 262, 34, 128, -52, EAR_PINK, None, 0)
    # Body and feet.
    ell(d, 512, 815, 265, 175, CREAM, OUTLINE, 5)
    ell(d, 512, 838, 200, 130, CREAM_SHADE)
    ell(d, 400, 945, 78, 42, CREAM, OUTLINE, 5)
    ell(d, 624, 945, 78, 42, CREAM, OUTLINE, 5)
    ell(d, 400, 952, 40, 16, EAR_PINK)
    ell(d, 624, 952, 40, 16, EAR_PINK)
    # Head.
    ell(d, 512, 470, 208, 188, CREAM, OUTLINE, 5)
    # Bow on the left ear base.
    poly(d, [(452, 296), (392, 258), (392, 330)], BOW)
    poly(d, [(452, 296), (512, 258), (512, 330)], BOW)
    circle(d, 452, 294, 17, BOW_DARK)
    # Eyes: big, bright, with two highlights each.
    for ex in (438, 586):
        ell(d, ex, 468, 36, 50, EYE)
        circle(d, ex - 12, 448, 14, WHITE)
        circle(d, ex + 13, 488, 7, WHITE)
        for dx, dy in ((-30, -38), (-38, -22), (-20, -48)):
            d.line([s(ex + dx), s(468 + dy), s(ex + dx - 10), s(468 + dy - 12)],
                   fill=EYE, width=s(5))
    # Blush, nose, mouth, whiskers.
    ell(d, 392, 548, 44, 25, BLUSH)
    ell(d, 632, 548, 44, 25, BLUSH)
    poly(d, [(498, 532), (526, 532), (512, 550)], NOSE)
    d.arc([s(478), s(548), s(512), s(578)], 0, 180, fill=OUTLINE, width=s(5))
    d.arc([s(512), s(548), s(546), s(578)], 0, 180, fill=OUTLINE, width=s(5))
    for sx, sy, ex, ey in ((330, 520, 268, 500), (330, 545, 266, 545),
                            (330, 570, 272, 592), (694, 520, 756, 500),
                            (694, 545, 758, 545), (694, 570, 752, 592)):
        d.line([s(sx), s(sy), s(ex), s(ey)], fill=(200, 170, 150), width=s(4))


def draw_strawberry(img):
    d = ImageDraw.Draw(img)
    # Strawberry held between the front paws.
    poly(d, [(470, 758), (512, 742), (554, 758), (540, 800),
             (512, 852), (484, 800)], STRAW)
    poly(d, [(470, 758), (512, 742), (554, 758), (540, 800),
             (512, 852), (484, 800)], STRAW)
    ell(d, 512, 782, 52, 44, STRAW)
    poly(d, [(512, 852), (484, 800), (540, 800)], STRAW_DARK)
    for sx, sy in ((492, 772), (532, 772), (512, 792), (496, 810),
                   (528, 810), (512, 828)):
        ell(d, sx, sy, 5, 8, SEED)
    poly(d, [(512, 748), (478, 730), (496, 756)], LEAF)
    poly(d, [(512, 748), (546, 730), (528, 756)], LEAF)
    poly(d, [(512, 748), (512, 722), (496, 748)], LEAF_DARK)
    d.line([s(512), s(748), s(512), s(716)], fill=LEAF_DARK, width=s(6))
    # Front paws hugging it.
    ell(d, 436, 812, 52, 38, CREAM, OUTLINE, 5)
    ell(d, 588, 812, 52, 38, CREAM, OUTLINE, 5)


def draw_extras(img):
    d = ImageDraw.Draw(img)
    heart(d, 245, 300, 26, HEART_SOFT)
    heart(d, 800, 285, 20, HEART)
    heart(d, 862, 470, 24, HEART_SOFT)
    heart(d, 168, 480, 18, HEART)
    heart(d, 748, 620, 16, HEART_SOFT)
    heart(d, 268, 640, 15, HEART)
    sparkle(d, 300, 210, 16, WHITE)
    sparkle(d, 730, 180, 13, WHITE)
    sparkle(d, 880, 600, 14, WHITE)
    sparkle(d, 150, 640, 12, WHITE)
    # Butterfly friend, right of the head.
    ell(d, 688, 388, 26, 34, (255, 183, 205))
    ell(d, 726, 388, 26, 34, (255, 143, 176))
    ell(d, 688, 396, 14, 20, (255, 213, 225))
    ell(d, 726, 396, 14, 20, (255, 183, 205))
    ell(d, 707, 392, 6, 26, (90, 70, 80))
    d.line([s(702), s(368), s(690), s(348)], fill=(90, 70, 80), width=s(4))
    d.line([s(712), s(368), s(724), s(348)], fill=(90, 70, 80), width=s(4))
    # Flowers on the grass.
    flower(d, 150, 968, 1.0, WHITE, (255, 217, 61))
    flower(d, 880, 962, 1.1, (255, 183, 205), (255, 217, 61))
    flower(d, 250, 1000, 0.8, (255, 213, 225), (255, 180, 90))
    flower(d, 790, 998, 0.8, WHITE, (255, 217, 61))
    flower(d, 60, 990, 0.7, (255, 183, 205), (255, 217, 61))
    flower(d, 965, 992, 0.7, (255, 213, 225), (255, 180, 90))


def draw():
    img = Image.new("RGBA", (W, W), SKY_TOP + (255,))
    draw_background(img)
    draw_bunny(img)
    draw_strawberry(img)
    draw_extras(img)
    return img.convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.png"
    draw().save(out_path, format="PNG")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
