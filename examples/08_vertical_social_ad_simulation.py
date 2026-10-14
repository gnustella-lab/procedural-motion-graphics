"""Example 08: Full-HD Vertical Mobile Social Ad Simulation (V4 Golden Standard).

15-second vertical mobile ad (1080x1920, 30 fps) demonstrating the V4 Desired Architecture.
100% procedural rendering in pure Python (Pillow + NumPy + SciPy) with zero external assets.

Timeline:
  0.00 - 3.05s  Hook      Kinetic type stack ("Breaking news. / Live sports. / Hot takes. / Big ideas.")
                          with live chip pulse -> Hero slam: "It's all happening." + underline sweep.
  3.05 - 7.55s  Feed      Native timeline feed, dynamic wrapping, live counters, procedural media
                          (rocket launch, soccer score, sunset), interactive like tap + confetti burst, FAB tap.
  7.55 - 10.05s Compose   Modal sheet slide-up over dimmed feed ("What's happening?"), live typing ticks,
                          character counter ring, and virtual QWERTY keyboard with active key pop magnification.
  10.05 - 12.05s Reaction Post detail screen, exponential view counter ramping (284K+), floating hearts,
                          3 incoming notification toasts, and bell badge climbing to "99+".
  12.05 - 15.00s End Card Brand X logo elastic reveal, dual shockwaves, precomputed radial glow map,
                          kinetic brand copy, tactile CTA button click (8% depression), and ripple.

Usage:
  python examples/08_vertical_social_ad_simulation.py                     # render x_ad_15s.mp4 (with soundtrack)
  python examples/08_vertical_social_ad_simulation.py --preview 1 5 9     # write PNG stills to previews/
"""

import argparse
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add root folder and scripts folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from scripts.motion_engine import (
    clamp, prog, lerp, lerpc, ease_out_cubic, ease_in_out_cubic,
    ease_out_back, ease_out_expo, button_click_press,
    vertical_push_transition
)

try:
    from scripts import x_ad_audio
except ImportError:
    import x_ad_audio

W, H, FPS, DUR = 1080, 1920, 30, 15.0
K = 1.5  # 1.5x super-sampling factor (virtual canvas 1620x2880)

# Authentic dark-mode palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEXT = (231, 233, 234)
GREY = (113, 118, 123)
BORDER = (47, 51, 54)
BLUE = (29, 155, 240)
PINK = (249, 24, 128)
GREEN = (0, 186, 124)
CARD = (22, 24, 28)
RED = (244, 33, 46)

# Scene timing (synchronized with procedural soundtrack in x_ad_audio.py)
S_HOOK, S_FEED, S_COMPOSE, S_REACT, S_END = 0.0, 3.05, 7.55, 10.05, 12.05

# ============================================================== cross-platform typography & font loader
FONT_FILES = {
    "black": [
        "C:/Windows/Fonts/seguibl.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
        "/usr/share/fonts/opentype/inter/Inter-Black.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "bold": [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "semibold": [
        "C:/Windows/Fonts/seguisb.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
        "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "regular": [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
}
_FONTS = {}


def font(px, w="regular"):
    px = max(1, int(round(px)))
    key = (px, w)
    if key not in _FONTS:
        for p in FONT_FILES.get(w, FONT_FILES["regular"]):
            if os.path.exists(p):
                _FONTS[key] = ImageFont.truetype(p, px)
                break
        else:
            _FONTS[key] = ImageFont.load_default()
    return _FONTS[key]


_MD = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def tw(s, size, w="regular"):
    return _MD.textlength(s, font=font(size * K, w)) / K


def wrap(text, size, w, maxw):
    lines, cur = [], ""
    for word in text.split(" "):
        test = word if not cur else cur + " " + word
        if tw(test, size, w) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_size(texts, w, maxw, max_size):
    s = max_size
    for t in texts:
        s = min(s, max_size * maxw / max(1.0, tw(t, max_size, w)))
    return s


def fmt(n):
    n = int(n)
    if n < 1000:
        return str(n)
    if n < 100_000:
        return f"{n / 1000:.1f}K".replace(".0K", "K")
    if n < 1_000_000:
        return f"{n / 1000:.0f}K"
    return f"{n / 1e6:.1f}M".replace(".0M", "M")


# ============================================================== canvas with 1-channel bounded alpha
class Canvas:
    """Super-sampled drawing surface; all coordinates are in output pixels."""

    def __init__(self, bg=BLACK, w=W, h=H):
        self.bg, self.w, self.h = bg, w, h
        self.im = Image.new("RGB", (int(w * K), int(h * K)), bg)
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x0, y0, x1, y1, fill=None, r=0, outline=None, width=1):
        if x1 <= x0 or y1 <= y0:
            return
        b = [x0 * K, y0 * K, x1 * K, y1 * K]
        wd = max(1, int(round(width * K)))
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        if r > 0:
            self.d.rounded_rectangle(b, radius=r * K, fill=fill, outline=outline, width=wd)
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=wd)

    def ell(self, cx, cy, r, fill=None, outline=None, width=1, ry=None):
        ry = r if ry is None else ry
        if r <= 0 or ry <= 0:
            return
        self.d.ellipse([(cx - r) * K, (cy - ry) * K, (cx + r) * K, (cy + ry) * K],
                       fill=fill, outline=outline, width=max(1, int(round(width * K))))

    def poly(self, pts, fill=None):
        self.d.polygon([(x * K, y * K) for x, y in pts], fill=fill)

    def line(self, pts, fill, width=1):
        self.d.line([(x * K, y * K) for x, y in pts], fill=fill,
                    width=max(1, int(round(width * K))), joint="curve")

    def txt(self, x, y, s, size, fill, anchor="lm", w="regular"):
        if size < 3:
            return
        self.d.text((x * K, y * K), s, font=font(size * K, w), fill=fill, anchor=anchor)

    # --- Bounded alpha blits: allocate small 1-channel "L" local masks only
    def _alpha(self, x0, y0, x1, y1, color, a, draw_fn):
        a = clamp(a)
        if a <= 0:
            return
        X0, Y0 = max(0, int(math.floor(x0 * K)) - 2), max(0, int(math.floor(y0 * K)) - 2)
        X1, Y1 = min(self.im.size[0], int(math.ceil(x1 * K)) + 2), min(self.im.size[1], int(math.ceil(y1 * K)) + 2)
        if X1 <= X0 or Y1 <= Y0:
            return
        m = Image.new("L", (X1 - X0, Y1 - Y0), 0)
        draw_fn(ImageDraw.Draw(m), X0, Y0, int(255 * a))
        self.im.paste(color, (X0, Y0, X1, Y1), m)

    def alpha_ell(self, cx, cy, r, color, a, width=None):
        def fn(md, X0, Y0, v):
            b = [(cx - r) * K - X0, (cy - r) * K - Y0, (cx + r) * K - X0, (cy + r) * K - Y0]
            if width:
                md.ellipse(b, outline=v, width=max(1, int(width * K)))
            else:
                md.ellipse(b, fill=v)
        self._alpha(cx - r, cy - r, cx + r, cy + r, color, a, fn)

    def alpha_rect(self, x0, y0, x1, y1, color, a, r=0):
        def fn(md, X0, Y0, v):
            md.rounded_rectangle([x0 * K - X0, y0 * K - Y0, x1 * K - X0, y1 * K - Y0],
                                 radius=r * K, fill=v)
        self._alpha(x0, y0, x1, y1, color, a, fn)

    def alpha_poly(self, pts, color, a):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]

        def fn(md, X0, Y0, v):
            md.polygon([(x * K - X0, y * K - Y0) for x, y in pts], fill=v)
        self._alpha(min(xs), min(ys), max(xs), max(ys), color, a, fn)

    def paste_rounded(self, sub, x0, y0, r):
        m = Image.new("L", sub.im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, sub.im.size[0] - 1, sub.im.size[1] - 1],
                                            radius=r * K, fill=255)
        self.im.paste(sub.im, (int(x0 * K), int(y0 * K)), m)

    def render(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def vgrad(c, stops):
    """Fill a canvas with a vertical multi-stop gradient. stops=[(pos, color), ...]."""
    hpx, wpx = c.im.size[1], c.im.size[0]
    y = np.linspace(0, 1, hpx)
    cols = np.zeros((hpx, 3), np.float32)
    for ch in range(3):
        cols[:, ch] = np.interp(y, [s[0] for s in stops], [s[1][ch] for s in stops])
    arr = np.repeat(cols[:, None, :], wpx, axis=1).astype(np.uint8)
    c.im.paste(Image.fromarray(arr))


# ============================================================== brand / icons
XL_OUT = [(18.244, 2.25), (21.552, 2.25), (14.325, 10.51), (22.827, 21.75), (16.17, 21.75),
          (10.956, 14.933), (4.99, 21.75), (1.68, 21.75), (9.41, 12.915), (1.254, 2.25),
          (8.08, 2.25), (12.793, 8.481)]
XL_HOLE = [(17.083, 19.77), (18.916, 19.77), (7.084, 4.126), (5.117, 4.126)]


def xlogo(c, cx, cy, size, col=WHITE, bg=BLACK):
    s = size / 21.6

    def f(p):
        return (cx + (p[0] - 12.04) * s, cy + (p[1] - 12.0) * s)
    c.poly([f(p) for p in XL_OUT], fill=col)
    c.poly([f(p) for p in XL_HOLE], fill=bg)


def heart_pts(cx, cy, s, n=64):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s / 34, cy + (y - 2.5) * s / 34))
    return pts


def ico_heart(c, cx, cy, s, col, wd=3.5, filled=False):
    pts = heart_pts(cx, cy, s)
    if filled:
        c.poly(pts, fill=col)
    else:
        c.line(pts + [pts[0], pts[1]], col, wd)


def ico_reply(c, cx, cy, s, col, wd=3.5):
    c.rect(cx - s * 0.48, cy - s * 0.40, cx + s * 0.48, cy + s * 0.28, outline=col, r=s * 0.30, width=wd)
    c.line([(cx - s * 0.20, cy + s * 0.27), (cx - s * 0.30, cy + s * 0.50), (cx + s * 0.02, cy + s * 0.27)], col, wd)


def ico_repost(c, cx, cy, s, col, wd=3.5):
    L, R, T, B = cx - s * 0.30, cx + s * 0.30, cy - s * 0.22, cy + s * 0.22
    c.line([(L, B + s * 0.04), (L, T), (cx + s * 0.14, T)], col, wd)
    c.poly([(L, T - s * 0.22), (L - s * 0.17, T + s * 0.02), (L + s * 0.17, T + s * 0.02)], col)
    c.line([(R, T - s * 0.04), (R, B), (cx - s * 0.14, B)], col, wd)
    c.poly([(R, B + s * 0.22), (R - s * 0.17, B - s * 0.02), (R + s * 0.17, B - s * 0.02)], col)


def ico_views(c, cx, cy, s, col, wd=3.5):
    base = cy + s * 0.36
    for dx, h in ((-0.32, 0.38), (-0.06, 0.78), (0.20, 0.56)):
        c.line([(cx + dx * s, base), (cx + dx * s, base - h * s)], col, wd)
    c.line([(cx + 0.42 * s, base), (cx + 0.42 * s, base - 0.18 * s)], col, wd)


def ico_share(c, cx, cy, s, col, wd=3.5):
    c.line([(cx, cy + s * 0.12), (cx, cy - s * 0.42)], col, wd)
    c.line([(cx - s * 0.2, cy - s * 0.22), (cx, cy - s * 0.42), (cx + s * 0.2, cy - s * 0.22)], col, wd)
    c.line([(cx - s * 0.38, cy - s * 0.02), (cx - s * 0.38, cy + s * 0.38),
            (cx + s * 0.38, cy + s * 0.38), (cx + s * 0.38, cy - s * 0.02)], col, wd)


def ico_bookmark(c, cx, cy, s, col, wd=3.5):
    c.line([(cx - s * 0.3, cy + s * 0.42), (cx - s * 0.3, cy - s * 0.42), (cx + s * 0.3, cy - s * 0.42),
            (cx + s * 0.3, cy + s * 0.42), (cx, cy + s * 0.18), (cx - s * 0.3, cy + s * 0.42)], col, wd)


def ico_person(c, cx, cy, s, col):
    c.ell(cx, cy - s * 0.22, s * 0.22, fill=col)
    c.d.pieslice([(cx - s * 0.42) * K, (cy + s * 0.06) * K, (cx + s * 0.42) * K, (cy + s * 0.86) * K],
                 180, 360, fill=col)


def badge(c, cx, cy, r, col=BLUE):
    pts = []
    for i in range(96):
        a = 2 * math.pi * i / 96
        rr = r * (1 + 0.09 * math.cos(8 * a))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    c.poly(pts, fill=col)
    c.line([(cx - r * 0.42, cy + r * 0.02), (cx - r * 0.12, cy + r * 0.32), (cx + r * 0.44, cy - r * 0.30)],
           WHITE, r * 0.24)


def avatar(c, cx, cy, r, col, letter):
    c.ell(cx, cy, r, fill=col)
    c.ell(cx + r * 0.35, cy - r * 0.35, r * 0.55, fill=lerpc(col, WHITE, 0.18))
    c.ell(cx, cy, r, outline=col, width=max(2, r * 0.06))
    c.txt(cx, cy + r * 0.02, letter, r * 0.95, WHITE, "mm", "bold")


def status_bar(c, col=WHITE):
    c.txt(100, 60, "9:41", 38, col, "mm", "semibold")
    for i in range(4):
        h = 10 + i * 7
        c.rect(840 + i * 14, 72 - h, 850 + i * 14, 72, fill=col, r=2)
    c.rect(914, 46, 978, 74, outline=col, r=8, width=3)
    c.rect(919, 51, 966, 69, fill=col, r=4)
    c.rect(981, 54, 986, 66, fill=col, r=2)


def tap(c, x, y, t, t_tap, col=WHITE, ripple=BLUE):
    """Touch indicator: soft finger dot that presses, then an expanding ripple."""
    a = min(prog(t, t_tap - 0.32, t_tap - 0.06), 1 - prog(t, t_tap + 0.12, t_tap + 0.42))
    if a > 0:
        press = clamp(prog(t, t_tap - 0.06, t_tap + 0.02) - prog(t, t_tap + 0.08, t_tap + 0.24))
        r = 46 * (1 - 0.22 * press)
        c.alpha_ell(x, y, r, col, 0.32 * a)
        c.alpha_ell(x, y, r, col, 0.55 * a, width=3)
    if t_tap < t < t_tap + 0.6:
        p = prog(t, t_tap, t_tap + 0.6)
        c.alpha_ell(x, y, 40 + ease_out_cubic(p) * 120, ripple, 0.9 * (1 - p), width=5)


def caption(c, cx, cy, text, lt, t_in, t_out=None, size=58, fill=BLUE, tcol=WHITE):
    e = ease_out_back(prog(lt, t_in, t_in + 0.4), 2.2)
    if t_out is not None:
        e *= 1 - ease_in_out_cubic(prog(lt, t_out, t_out + 0.22))
    if e <= 0.03:
        return
    w_ = tw(text, size, "black")
    pw, ph = (w_ + 90) * e, size * 1.85 * e
    c.rect(cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2, fill=fill, r=ph / 2)
    c.txt(cx, cy - size * 0.06 * e, text, size * e, tcol, "mm", "black")


# ============================================================== scene 1: hook
HOOK = [("Breaking news.", "Trending worldwide · 1.2M posts"),
        ("Live sports.", "Sports · Trending · 482K posts"),
        ("Hot takes.", "Trending in Tech · 96K posts"),
        ("Big ideas.", "Science · Trending · 58K posts")]
HOOK_T = [0.05, 0.55, 1.05, 1.55]
FINAL_T = 2.05
HOOK_SIZE = fit_size([h[0] for h in HOOK], "black", 900, 124)
FINAL_SIZE = fit_size(["It's all", "happening."], "black", 920, 170)


def scene_hook(t):
    c = Canvas()
    e0 = ease_out_cubic(prog(t, 0.0, 0.45))
    xlogo(c, 540, 200 - (1 - e0) * 24, 76, lerpc(BLACK, WHITE, e0))

    # "Happening now" live chip
    chip_w = tw("Happening now", 32, "bold") + 90
    cy = 318
    c.rect(540 - chip_w / 2, cy - 32, 540 + chip_w / 2, cy + 32, outline=lerpc(BLACK, BORDER, e0), r=32, width=2)
    pulse = 0.5 + 0.5 * math.sin(t * 9)
    c.alpha_ell(540 - chip_w / 2 + 40, cy, 10 + 8 * pulse, RED, 0.35 * e0 * (1 - pulse))
    c.ell(540 - chip_w / 2 + 40, cy, 9, fill=lerpc(BLACK, RED, e0))
    c.txt(540 - chip_w / 2 + 64, cy - 2, "Happening now", 32, lerpc(BLACK, TEXT, e0), "lm", "bold")

    exit_k = ease_in_out_cubic(prog(t, FINAL_T - 0.08, FINAL_T + 0.25))
    LHH, base_y = 178, 1020
    for i, (line, meta) in enumerate(HOOK):
        if t < HOOK_T[i]:
            continue
        e = ease_out_cubic(prog(t, HOOK_T[i], HOOK_T[i] + 0.26))
        pushes = sum(ease_out_cubic(prog(t, HOOK_T[j], HOOK_T[j] + 0.26)) for j in range(i + 1, len(HOOK)))
        y = base_y + (1 - e) * 110 - pushes * LHH - exit_k * 620
        age = clamp(pushes)
        col = lerpc(BLACK, WHITE, e)
        col = lerpc(col, (58, 61, 64), age)
        col = lerpc(col, BLACK, exit_k)
        c.txt(80, y, line, HOOK_SIZE, col, "lm", "black")
        mk = e * max(0.0, 1.0 - pushes * 3.5) * (1 - exit_k)
        if mk > 0.01:
            c.ell(92, y + 96, 7, fill=lerpc(BLACK, BLUE, mk))
            c.txt(112, y + 94, meta, 34, lerpc(BLACK, BLUE, mk), "lm", "semibold")

    # Final slam: "It's all / happening."
    for k, (word, col, dt) in enumerate((("It's all", WHITE, 0.0), ("happening.", BLUE, 0.12))):
        p = prog(t, FINAL_T + dt, FINAL_T + dt + 0.4)
        if p <= 0:
            continue
        s = 1 + 0.35 * (1 - ease_out_expo(p))
        fade = ease_out_cubic(prog(t, FINAL_T + dt, FINAL_T + dt + 0.12))
        y = 880 + k * FINAL_SIZE * 1.08
        c.txt(80, y, word, FINAL_SIZE * s, lerpc(BLACK, col, fade), "lm", "black")
    # underline sweep
    u = ease_in_out_cubic(prog(t, FINAL_T + 0.3, FINAL_T + 0.75))
    if u > 0:
        uw = tw("happening.", FINAL_SIZE, "black") * u
        uy = 880 + FINAL_SIZE * 1.08 + FINAL_SIZE * 0.62
        c.rect(84, uy, 84 + uw, uy + 14, fill=BLUE, r=7)
    return c.render()


# ============================================================== scene 2: feed
FX0, FX1 = 170, 1040
BODY, LH = 40, 54
MEDIA_H = 470
FEED_TOP = 253
NAV_Y = 1770
FABX, FABY = 950, 1645
LIKE_T, FAB_T = 1.95, 3.85

POSTS = [
    dict(name="Nova Space", handle="@novaspace", time="2m", verified=True, av=(98, 70, 230), letter="N",
         text="Liftoff confirmed. Stage separation nominal. Watching history happen live with all of you.",
         media="rocket", stats=[2400, 18300, 96200, 4100000], rate=[60, 400, 2600, 90000]),
    dict(name="Maya Chen", handle="@mayabuilds", time="14m", verified=False, av=(232, 92, 60), letter="M",
         text="hot take: the best ideas start as a single post at 2am", media=None,
         stats=[41, 126, 847, 22000], rate=[0, 0, 0, 400], likeable=True),
    dict(name="Goal Line", handle="@goalline", time="5m", verified=True, av=(0, 160, 110), letter="G",
         text="WHAT A FINISH. 94th minute winner and this stadium is SHAKING.", media="score",
         stats=[5100, 32000, 141000, 6200000], rate=[90, 700, 3100, 120000]),
    dict(name="Daily Frame", handle="@dailyframe", time="1h", verified=True, av=(220, 150, 20), letter="D",
         text="Your timeline, but make it art.", media="sunset",
         stats=[880, 4200, 39000, 1300000], rate=[5, 20, 300, 6000]),
    dict(name="Leo Park", handle="@leoparkdev", time="3h", verified=False, av=(60, 130, 240), letter="L",
         text="shipped it. no notes. thank you to everyone who helped along the way", media=None,
         stats=[96, 310, 2900, 81000], rate=[0, 0, 10, 300]),
]


def layout_post(p):
    lines = wrap(p["text"], BODY, "regular", FX1 - FX0)
    cur = 124 + (len(lines) - 1) * LH + 34
    media_y = None
    if p["media"]:
        media_y = cur + 14
        cur = media_y + MEDIA_H
    act = cur + 50
    return dict(lines=lines, media_y=media_y, act=act, h=act + 46)


LAY = []
_y = FEED_TOP
for _p in POSTS:
    _l = layout_post(_p)
    _l["top"] = _y
    _y += _l["h"]
    LAY.append(_l)

SCROLL1 = LAY[1]["top"] + LAY[1]["act"] - 1060
SCROLL2 = LAY[2]["top"] - FEED_TOP + 10


def feed_scroll(lt):
    return (SCROLL1 * ease_in_out_cubic(prog(lt, 0.55, 1.45))
            + (SCROLL2 - SCROLL1) * ease_in_out_cubic(prog(lt, 2.55, 3.45)))


def media_rocket(w, h, t):
    c = Canvas(w=w, h=h)
    vgrad(c, [(0, (6, 8, 26)), (0.55, (40, 24, 86)), (0.85, (190, 80, 70)), (1, (240, 140, 80))])
    rng = np.random.RandomState(3)
    for i in range(46):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h * 0.65), rng.uniform(1.2, 3.0)
        tw_ = 0.55 + 0.45 * math.sin(t * 5 + i)
        c.ell(x, y, r, fill=lerpc((30, 30, 60), WHITE, tw_))
    rise = 40 * t + 6 * t * t
    x, base = w * 0.55, h * 0.78 - rise
    for i in range(14):
        a = i / 13
        sx = x + math.sin(i * 1.7 + t * 2) * 30 * a + (i % 3 - 1) * 40 * a
        sy = h * 0.80 + (base - h * 0.78) * (1 - a) * 0.6 + 40 * a
        c.ell(sx, min(sy, h * 0.95), 30 + 70 * a, fill=lerpc((150, 130, 150), (70, 50, 80), a))
    fl = 90 + 22 * math.sin(t * 45) + 10 * math.sin(t * 71)
    c.poly([(x - 22, base), (x, base + fl), (x + 22, base)], fill=(255, 140, 40))
    c.poly([(x - 11, base), (x, base + fl * 0.6), (x + 11, base)], fill=(255, 235, 150))
    c.poly([(x - 26, base - 10), (x - 58, base + 24), (x - 26, base - 60)], fill=(170, 175, 190))
    c.poly([(x + 26, base - 10), (x + 58, base + 24), (x + 26, base - 60)], fill=(170, 175, 190))
    c.rect(x - 26, base - 230, x + 26, base, fill=(240, 242, 248), r=10)
    c.poly([(x - 26, base - 226), (x, base - 300), (x + 26, base - 226)], fill=(240, 242, 248))
    c.rect(x - 26, base - 120, x + 26, base - 108, fill=(29, 155, 240))
    c.ell(x, base - 170, 12, fill=(20, 30, 60))
    c.poly([(0, h), (0, h * 0.86), (w * 0.3, h * 0.82), (w * 0.7, h * 0.85), (w, h * 0.80), (w, h)], fill=(14, 10, 22))
    c.rect(w * 0.42, h * 0.40, w * 0.44, h * 0.84, fill=(30, 26, 40))
    c.rect(24, 24, 124, 70, fill=RED, r=10)
    c.txt(74, 46, "LIVE", 28, WHITE, "mm", "black")
    c.alpha_rect(136, 24, 136 + tw("1.2M watching", 26, "semibold") + 30, 70, BLACK, 0.55, r=10)
    c.txt(151, 46, "1.2M watching", 26, WHITE, "lm", "semibold")
    return c


def media_score(w, h, t):
    c = Canvas(w=w, h=h)
    vgrad(c, [(0, (20, 110, 58)), (1, (8, 60, 32))])
    for i in range(0, 8, 2):
        c.alpha_rect(i * w / 8, 0, (i + 1) * w / 8, h, WHITE, 0.05)
    c.alpha_ell(w / 2, h / 2, 120, WHITE, 0.25, width=4)
    c.alpha_rect(w / 2 - 2, 0, w / 2 + 2, h, WHITE, 0.25)
    rng = np.random.RandomState(11)
    for i in range(60):
        x0 = rng.uniform(0, w)
        sp = rng.uniform(60, 160)
        y = (rng.uniform(-h, h) + t * sp) % (h + 40) - 20
        x = x0 + math.sin(t * 3 + i) * 14
        col = [BLUE, WHITE, (255, 212, 0), PINK][i % 4]
        s = rng.uniform(4, 8)
        c.rect(x - s, y - s * 0.5, x + s, y + s * 0.5, fill=col, r=1)
    pw, ph = 700, 210
    c.alpha_rect(w / 2 - pw / 2, h / 2 - ph / 2, w / 2 + pw / 2, h / 2 + ph / 2, BLACK, 0.6, r=28)
    c.txt(w / 2 - 210, h / 2 - 8, "NORTH", 40, WHITE, "mm", "black")
    c.txt(w / 2 + 210, h / 2 - 8, "UNITED", 40, WHITE, "mm", "black")
    flash = 0.5 + 0.5 * math.sin(t * 8)
    c.txt(w / 2, h / 2 - 14, "2 - 1", 96, lerpc(WHITE, (255, 230, 120), flash * 0.6), "mm", "black")
    c.rect(w / 2 - 70, h / 2 + 48, w / 2 + 70, h / 2 + 88, fill=(255, 212, 0), r=20)
    c.txt(w / 2, h / 2 + 67, "FT · 94'", 26, BLACK, "mm", "black")
    return c


def media_sunset(w, h, t):
    c = Canvas(w=w, h=h)
    hz = h * 0.6
    vgrad(c, [(0, (60, 30, 130)), (0.35, (220, 80, 130)), (0.6, (255, 170, 90)), (0.6001, (40, 30, 90)),
              (1, (10, 10, 40))])
    c.ell(w / 2, hz, 110, fill=(255, 226, 160))
    sea = Canvas(w=w, h=int(h - hz) + 1)
    vgrad(sea, [(0, (50, 34, 96)), (1, (10, 10, 40))])
    c.im.paste(sea.im, (0, int(hz * K)))
    for i in range(9):
        y = hz + 14 + i * 20
        ww = (100 - i * 8) * (1 + 0.15 * math.sin(t * 4 + i))
        c.rect(w / 2 - ww, y, w / 2 + ww, y + 6, fill=lerpc((255, 210, 150), (60, 40, 100), i / 9), r=3)
    return c


MEDIA = {"rocket": media_rocket, "score": media_score, "sunset": media_sunset}


def action_row(c, y, vals, lt, liked=False, like_pop=1.0):
    gx = [FX0, FX0 + 215, FX0 + 430, FX0 + 645]
    s = 42
    ico_reply(c, gx[0] + 22, y, s, GREY)
    ico_repost(c, gx[1] + 22, y, s, GREY)
    if liked:
        ico_heart(c, gx[2] + 22, y, s * like_pop, PINK, filled=True)
    else:
        ico_heart(c, gx[2] + 22, y, s, GREY)
    ico_views(c, gx[3] + 22, y, s, GREY)
    ico_share(c, FX1 - 20, y, s, GREY)
    for i in range(4):
        col = PINK if (i == 2 and liked) else GREY
        c.txt(gx[i] + 54, y, fmt(vals[i]), 34, col, "lm", "regular")


def draw_post(c, i, y, lt):
    p, L = POSTS[i], LAY[i]
    avatar(c, 92, y + 84, 50, p["av"], p["letter"])
    c.txt(FX0, y + 60, p["name"], 40, WHITE, "lm", "bold")
    x = FX0 + tw(p["name"], 40, "bold") + 10
    if p["verified"]:
        badge(c, x + 19, y + 62, 19)
        x += 46
    c.txt(x + 4, y + 60, f'{p["handle"]} · {p["time"]}', 38, GREY, "lm", "regular")
    for k in range(3):
        c.ell(FX1 - 36 + k * 14, y + 62, 3.5, fill=GREY)
    for j, ln in enumerate(L["lines"]):
        c.txt(FX0, y + 124 + j * LH, ln, BODY, TEXT, "lm", "regular")
    if p["media"]:
        my = y + L["media_y"]
        if my < NAV_Y and my + MEDIA_H > 0:
            sub = MEDIA[p["media"]](FX1 - FX0, MEDIA_H, lt + i)
            c.paste_rounded(sub, FX0, my, 32)
            c.rect(FX0, my, FX1, my + MEDIA_H, outline=BORDER, r=32, width=2)
    vals = [p["stats"][k] + p["rate"][k] * lt for k in range(4)]
    liked = bool(p.get("likeable")) and lt >= LIKE_T + 0.03
    pop = 1.0
    ay = y + L["act"]
    if liked:
        vals[2] += 1
        q = prog(lt, LIKE_T + 0.03, LIKE_T + 0.35)
        pop = 0.4 + 0.6 * ease_out_back(q, 3.0)
        if q < 1:
            hx = FX0 + 430 + 22
            for k in range(8):
                a = k / 8 * 2 * math.pi
                rr = 24 + 46 * ease_out_cubic(q)
                col = [PINK, BLUE, GREEN, (255, 212, 0)][k % 4]
                c.ell(hx + math.cos(a) * rr, ay + math.sin(a) * rr, 7 * (1 - q), fill=col)
            c.alpha_ell(hx, ay, 20 + 40 * ease_out_cubic(q), PINK, 0.6 * (1 - q), width=4)
    action_row(c, ay, vals, lt, liked, pop)
    c.rect(0, y + L["h"] - 1, W, y + L["h"] + 1, fill=BORDER)


def top_bar(c):
    c.rect(0, 0, W, FEED_TOP, fill=BLACK)
    status_bar(c)
    avatar(c, 78, 150, 34, (60, 130, 240), "A")
    xlogo(c, 540, 150, 56)
    c.txt(270, 214, "For you", 38, WHITE, "mm", "bold")
    c.txt(810, 214, "Following", 38, GREY, "mm", "semibold")
    u = tw("For you", 38, "bold")
    c.rect(270 - u / 2, 244, 270 + u / 2, 252, fill=BLUE, r=4)
    c.rect(0, FEED_TOP - 2, W, FEED_TOP, fill=BORDER)


def bottom_nav(c, bell_badge=None):
    c.rect(0, NAV_Y, W, H, fill=BLACK)
    c.rect(0, NAV_Y, W, NAV_Y + 2, fill=BORDER)
    y = 1840
    x = 108
    c.poly([(x, y - 38), (x + 38, y - 6), (x + 28, y - 6), (x + 28, y + 30), (x - 28, y + 30),
            (x - 28, y - 6), (x - 38, y - 6)], fill=WHITE)
    x = 324
    c.ell(x - 6, y - 6, 22, outline=WHITE, width=5)
    c.line([(x + 10, y + 10), (x + 30, y + 30)], WHITE, 6)
    x = 540
    c.rect(x - 28, y - 28, x + 28, y + 28, outline=WHITE, r=10, width=5)
    c.line([(x - 14, y + 14), (x + 14, y - 14)], WHITE, 5)
    x = 756
    c.line([(x - 28, y + 16), (x - 20, y + 4), (x - 20, y - 10), (x - 10, y - 25), (x, y - 29), (x + 10, y - 25),
            (x + 20, y - 10), (x + 20, y + 4), (x + 28, y + 16), (x - 28, y + 16)], WHITE, 4.5)
    c.line([(x - 9, y + 27), (x + 9, y + 27)], WHITE, 5)
    if bell_badge:
        bw = max(40, tw(bell_badge, 26, "bold") + 22)
        c.rect(x + 4, y - 50, x + 4 + bw, y - 12, fill=BLUE, r=19)
        c.txt(x + 4 + bw / 2, y - 32, bell_badge, 26, WHITE, "mm", "bold")
    x = 972
    c.rect(x - 32, y - 24, x + 32, y + 24, outline=WHITE, r=6, width=4.5)
    c.line([(x - 28, y - 18), (x, y + 4), (x + 28, y - 18)], WHITE, 4.5)
    c.rect(470, 1892, 610, 1900, fill=WHITE, r=4)


def fab(c, lt, t_tap=None):
    s = button_click_press(lt, t_tap, 0.08, 0.18, 0.12) if t_tap is not None else 1.0
    c.ell(FABX, FABY, 76 * s, fill=BLUE)
    c.rect(FABX - 26 * s, FABY - 4 * s, FABX + 26 * s, FABY + 4 * s, fill=WHITE, r=3)
    c.rect(FABX - 4 * s, FABY - 26 * s, FABX + 4 * s, FABY + 26 * s, fill=WHITE, r=3)


def scene_feed(lt):
    c = Canvas()
    sc = feed_scroll(lt)
    for i in range(len(POSTS)):
        y = LAY[i]["top"] - sc
        if y > NAV_Y or y + LAY[i]["h"] < FEED_TOP:
            continue
        draw_post(c, i, y, lt)
    top_bar(c)
    bottom_nav(c)
    fab(c, lt, FAB_T)
    caption(c, 540, 1480, "See it first.", lt, 0.6, 2.3)
    tap(c, FX0 + 430 + 22, LAY[1]["top"] + LAY[1]["act"] - SCROLL1, lt, LIKE_T)
    tap(c, FABX, FABY, lt, FAB_T)
    return c.render()


# ============================================================== scene 3: compose
TYPED = "Hello, X. What's everyone talking about?"
TYPE_T0, TYPE_T1, POST_T = 0.45, 1.75, 2.1
TYPE_DT = (TYPE_T1 - TYPE_T0) / len(TYPED)
KB_TOP = 1250
KEY_W, KEY_H, KEY_G = 96, 104, 10
ROW_Y = [1272, 1396, 1520, 1644]


def build_keys():
    keys = {}
    for r, row in enumerate(["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]):
        total = len(row) * KEY_W + (len(row) - 1) * KEY_G
        x = (W - total) / 2
        for ch in row:
            keys[ch] = (x, ROW_Y[r], x + KEY_W, ROW_Y[r] + KEY_H)
            x += KEY_W + KEY_G
    keys[" "] = (230, ROW_Y[3], 840, ROW_Y[3] + KEY_H)
    return keys


KEYS = build_keys()
SPECIAL = [((15, ROW_Y[2], 145, ROW_Y[2] + KEY_H), "⇧"), ((935, ROW_Y[2], 1065, ROW_Y[2] + KEY_H), "⌫"),
           ((15, ROW_Y[3], 220, ROW_Y[3] + KEY_H), "123"), ((850, ROW_Y[3], 1065, ROW_Y[3] + KEY_H), "return")]


def typed_count(lt):
    if lt < TYPE_T0:
        return 0
    return min(len(TYPED), int((lt - TYPE_T0) / TYPE_DT) + 1)


def keyboard(c, lt):
    c.rect(0, KB_TOP, W, H, fill=(30, 30, 32))
    active, act_t = None, 0
    n = typed_count(lt)
    if n > 0:
        k = n - 1
        tk = TYPE_T0 + k * TYPE_DT
        if lt - tk < 0.1:
            active, act_t = TYPED[k].upper(), lt - tk
    for ch, (x0, y0, x1, y1) in KEYS.items():
        on = (ch == active)
        c.rect(x0, y0, x1, y1, fill=(140, 140, 146) if on else (74, 74, 78), r=14)
        if ch != " ":
            c.txt((x0 + x1) / 2, (y0 + y1) / 2 - 4, ch, 44, WHITE, "mm", "regular")
        else:
            c.txt((x0 + x1) / 2, (y0 + y1) / 2 - 2, "space", 34, WHITE, "mm", "regular")
    for (x0, y0, x1, y1), lab in SPECIAL:
        c.rect(x0, y0, x1, y1, fill=(48, 48, 52), r=14)
        if lab in ("⇧", "⌫"):
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if lab == "⇧":
                c.line([(cx - 20, cy + 2), (cx, cy - 20), (cx + 20, cy + 2), (cx + 9, cy + 2), (cx + 9, cy + 20),
                        (cx - 9, cy + 20), (cx - 9, cy + 2), (cx - 20, cy + 2)], WHITE, 3.5)
            else:
                c.line([(cx - 30, cy), (cx - 14, cy - 18), (cx + 26, cy - 18), (cx + 26, cy + 18), (cx - 14, cy + 18),
                        (cx - 30, cy)], WHITE, 3.5)
        else:
            c.txt((x0 + x1) / 2, (y0 + y1) / 2 - 3, lab, 34, WHITE, "mm", "regular")
    if active and active in KEYS and active != " ":
        x0, y0, x1, y1 = KEYS[active]
        s = ease_out_back(clamp(act_t / 0.05), 2.0)
        px0, px1 = x0 - 14 * s, x1 + 14 * s
        c.rect(px0, y0 - 128 * s, px1, y1, fill=(140, 140, 146), r=18)
        c.txt((x0 + x1) / 2, y0 - 62 * s, active, 70 * s, WHITE, "mm", "regular")
    c.rect(400, 1892, 680, 1900, fill=WHITE, r=4)


def scene_compose(lt):
    c = Canvas()
    status_bar(c)
    c.txt(60, 172, "Cancel", 40, TEXT, "lm", "regular")
    n = typed_count(lt)
    en = ease_out_cubic(prog(lt, TYPE_T0, TYPE_T0 + 0.2))
    s = button_click_press(lt, POST_T, 0.08, 0.18, 0.10)
    bw, bh, bx, by = 176 * s, 78 * s, 948, 172
    c.rect(bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2, fill=lerpc((14, 72, 112), BLUE, en), r=bh / 2)
    c.txt(bx, by - 2, "Post", 36 * s, lerpc((130, 130, 130), WHITE, en), "mm", "bold")
    if lt > POST_T:
        c.alpha_ell(bx, by, 60 + 90 * ease_out_cubic(prog(lt, POST_T, POST_T + 0.5)), BLUE,
                    0.9 * (1 - prog(lt, POST_T, POST_T + 0.5)), width=5)

    avatar(c, 100, 320, 52, (60, 130, 240), "A")
    c.rect(180, 270, 180 + tw("Everyone", 30, "bold") + 70, 322, outline=BLUE, r=26, width=2)
    c.txt(180 + 26, 295, "Everyone", 30, BLUE, "lm", "bold")
    cx_ = 180 + tw("Everyone", 30, "bold") + 44
    c.line([(cx_ - 8, 290), (cx_, 298), (cx_ + 8, 290)], BLUE, 3)

    size, lh, x0, y0 = 52, 70, 180, 400
    if n == 0:
        c.txt(x0, y0, "What's happening?", size, GREY, "lm", "regular")
        last_line, ly = "", y0
    else:
        lines = wrap(TYPED[:n], size, "regular", 850)
        for j, ln in enumerate(lines):
            c.txt(x0, y0 + j * lh, ln, size, TEXT, "lm", "regular")
        last_line, ly = lines[-1], y0 + (len(lines) - 1) * lh
    blink = (TYPE_T0 - 0.05 < lt < TYPE_T1 + 0.05) or int(lt * 3) % 2 == 0
    if blink and lt < POST_T + 0.05:
        cx = x0 + (tw(last_line, size, "regular") + 4 if last_line else 0)
        c.rect(cx, ly - 34, cx + 4, ly + 34, fill=BLUE)

    caption(c, 540, 860, "Say it your way.", lt, 0.4, 1.85)

    c.ell(76, 1110, 17, outline=BLUE, width=3)
    c.ell(76, 1110, 7, outline=BLUE, width=3, ry=17)
    c.line([(59, 1110), (93, 1110)], BLUE, 3)
    c.txt(108, 1108, "Everyone can reply", 32, BLUE, "lm", "bold")
    c.rect(0, 1150, W, 1152, fill=BORDER)
    tb = 1198
    c.rect(52, tb - 22, 96, tb + 22, outline=BLUE, r=6, width=3.5)
    c.poly([(56, tb + 18), (70, tb + 2), (80, tb + 12), (86, tb + 6), (92, tb + 18)], fill=BLUE)
    c.rect(132, tb - 22, 184, tb + 22, outline=BLUE, r=6, width=3.5)
    c.txt(158, tb, "GIF", 20, BLUE, "mm", "black")
    for k in range(3):
        c.rect(222, tb - 16 + k * 14, 222 + (40 - k * 10), tb - 10 + k * 14, fill=BLUE, r=3)
    c.ell(300, tb - 6, 14, outline=BLUE, width=3.5)
    c.poly([(288, tb + 2), (300, tb + 24), (312, tb + 2)], fill=BLUE)
    c.ell(990, tb, 24, outline=BORDER, width=4)
    if n:
        c.d.arc([(990 - 24) * K, (tb - 24) * K, (990 + 24) * K, (tb + 24) * K], -90, -90 + 360 * n / 280,
                fill=BLUE, width=int(4 * K))
    keyboard(c, lt)
    tap(c, bx, by, lt, POST_T)
    return c.render()


# ============================================================== scene 4: reaction
R_LINES = wrap(TYPED, 56, "regular", 980)
R_TEXT_Y = 470
R_META_Y = R_TEXT_Y + (len(R_LINES) - 1) * 76 + 92
R_STATS_Y = R_META_Y + 112
R_ACT_Y = R_STATS_Y + 120
TOASTS = [(0.35, "heart", "Maya Chen", " and 1,208 others liked your post"),
          (0.65, "repost", "Goal Line", " reposted your post"),
          (0.95, "person", "86", " new followers")]


def scene_reaction(lt):
    c = Canvas()
    status_bar(c)
    c.line([(84, 168), (44, 168)], WHITE, 4.5)
    c.line([(62, 148), (44, 168), (62, 188)], WHITE, 4.5)
    c.txt(130, 166, "Post", 44, WHITE, "lm", "bold")

    avatar(c, 102, 322, 56, (60, 130, 240), "A")
    c.txt(182, 300, "Alex Rivera", 42, WHITE, "lm", "bold")
    c.txt(182, 350, "@alexrivera", 38, GREY, "lm", "regular")
    for j, ln in enumerate(R_LINES):
        c.txt(50, R_TEXT_Y + j * 76, ln, 56, TEXT, "lm", "regular")

    g = ease_out_expo(prog(lt, 0.15, 1.7))
    views, reposts, quotes, likes, marks = 284000 * g, 1800 * g, 128 * g, 12400 * g, 1025 * g
    meta = "9:41 AM · Oct 12, 2026 · "
    c.txt(50, R_META_Y, meta, 34, GREY, "lm", "regular")
    x = 50 + tw(meta, 34, "regular")
    c.txt(x, R_META_Y, fmt(views), 34, WHITE, "lm", "bold")
    c.txt(x + tw(fmt(views), 34, "bold"), R_META_Y, " Views", 34, GREY, "lm", "regular")
    c.rect(0, R_META_Y + 54, W, R_META_Y + 56, fill=BORDER)
    x = 50
    for v, lab in ((reposts, " Reposts"), (quotes, " Quotes"), (likes, " Likes")):
        c.txt(x, R_STATS_Y, fmt(v), 36, WHITE, "lm", "bold")
        x += tw(fmt(v), 36, "bold")
        c.txt(x, R_STATS_Y, lab, 36, GREY, "lm", "regular")
        x += tw(lab, 36, "regular") + 34
    c.rect(0, R_STATS_Y + 58, W, R_STATS_Y + 60, fill=BORDER)

    ay = R_ACT_Y
    ico_reply(c, 110, ay, 50, GREY)
    ico_repost(c, 320, ay, 50, GREEN)
    pulse = 1 + 0.12 * max(0.0, math.sin(lt * 14)) * (1 - prog(lt, 1.2, 1.8))
    ico_heart(c, 540, ay, 50 * ease_out_back(prog(lt, 0.05, 0.35), 2.5) * pulse, PINK, filled=True)
    ico_bookmark(c, 760, ay, 46, GREY)
    ico_share(c, 970, ay, 50, GREY)
    c.rect(0, ay + 62, W, ay + 64, fill=BORDER)

    rng = np.random.RandomState(5)
    for k in range(10):
        ts = 0.15 + k * 0.11
        p = prog(lt, ts, ts + 1.0)
        if 0 < p < 1:
            dx = rng.uniform(-90, 90)
            hx = 540 + dx * p + math.sin(p * 7 + k) * 18
            hy = ay - 30 - 180 * ease_out_cubic(p)
            c.alpha_poly(heart_pts(hx, hy, 26 + 18 * p), PINK, 0.85 * (1 - p))
        else:
            rng.uniform(-90, 90)

    for k, (t_in, ico, bold, rest) in enumerate(TOASTS):
        e = ease_out_back(prog(lt, t_in, t_in + 0.4), 1.6)
        f = ease_out_cubic(prog(lt, t_in, t_in + 0.2))
        if f <= 0:
            continue
        cy = ay + 160 + k * 150
        dx = (1 - e) * 260
        c.rect(50 + dx, cy - 62, 1030 + dx, cy + 62, fill=lerpc(BLACK, CARD, f), r=30,
               outline=lerpc(BLACK, BORDER, f), width=2)
        ix = 116 + dx
        if ico == "heart":
            ico_heart(c, ix, cy, 46, lerpc(BLACK, PINK, f), filled=True)
        elif ico == "repost":
            ico_repost(c, ix, cy, 46, lerpc(BLACK, GREEN, f), 4.5)
        else:
            ico_person(c, ix, cy - 4, 50, lerpc(BLACK, BLUE, f))
        c.txt(170 + dx, cy, bold, 34, lerpc(BLACK, WHITE, f), "lm", "bold")
        c.txt(170 + dx + tw(bold, 34, "bold"), cy, rest, 34, lerpc(BLACK, TEXT, f), "lm", "regular")

    caption(c, 540, 1640, "Get heard.", lt, 0.9)
    badge_n = int(lerp(3, 99, ease_out_expo(prog(lt, 0.3, 1.6))))
    bottom_nav(c, bell_badge=f"{badge_n}+" if badge_n >= 99 else str(badge_n))
    return c.render()


# ============================================================== scene 5: end card
TAG = "Join the conversation."
TAG_SIZE = fit_size([TAG], "black", 940, 92)
LOGO_Y = 760
_GLOW = None


def glow_map():
    global _GLOW
    if _GLOW is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d2 = ((xx - 540) ** 2 + (yy - LOGO_Y) ** 2) / (430.0 ** 2)
        _GLOW = np.exp(-d2)[..., None] * np.array(BLUE, np.float32)
    return _GLOW


CTA_T = 1.7


def scene_end(lt):
    c = Canvas()
    e = ease_out_back(prog(lt, 0.0, 0.55), 2.0)
    if e > 0.01:
        xlogo(c, 540, LOGO_Y, 300 * e)
    p = prog(lt, 0.0, 0.7)
    if 0 < p < 1:
        c.alpha_ell(540, LOGO_Y, 160 + 420 * ease_out_cubic(p), BLUE, 0.8 * (1 - p), width=6)
        c.alpha_ell(540, LOGO_Y, 120 + 300 * ease_out_cubic(p), WHITE, 0.4 * (1 - p), width=3)

    f = ease_out_cubic(prog(lt, 0.45, 0.85))
    c.txt(540, 1090 + (1 - f) * 50, TAG, TAG_SIZE, lerpc(BLACK, WHITE, f), "mm", "black")

    b = ease_out_back(prog(lt, 0.75, 1.15), 2.0)
    if b > 0.02:
        s = b * button_click_press(lt, CTA_T, 0.08, 0.2, 0.08)
        bw, bh = 560 * s, 136 * s
        c.rect(540 - bw / 2, 1290 - bh / 2, 540 + bw / 2, 1290 + bh / 2, fill=WHITE, r=bh / 2)
        c.txt(540, 1286, "Get the app", 52 * s, BLACK, "mm", "black")
    g = ease_out_cubic(prog(lt, 1.0, 1.4))
    c.txt(540, 1440, "x.com", 42, lerpc(BLACK, GREY, g), "mm", "semibold")
    tap(c, 640, 1300, lt, CTA_T, col=BLUE, ripple=BLUE)

    arr = np.asarray(c.render()).astype(np.float32)
    gi = 0.22 * ease_out_cubic(prog(lt, 0.0, 0.8)) * (0.9 + 0.1 * math.sin(lt * 3))
    arr += glow_map() * gi
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


# ============================================================== timeline compositor
SCENES = [(S_HOOK, scene_hook), (S_FEED, scene_feed), (S_COMPOSE, scene_compose),
          (S_REACT, scene_reaction), (S_END, scene_end)]
TRANS = [None, ("push", 0.45), ("sheet_up", 0.40), ("sheet_down", 0.40), ("zoom", 0.35)]


def dim(img, k):
    if k <= 0:
        return img
    return Image.blend(img, Image.new("RGB", img.size, BLACK), clamp(k))


def apply_transition(kind, cur, prev, p):
    if kind == "push":
        return vertical_push_transition(cur, prev, p)
    if kind == "sheet_up":
        base = dim(prev, 0.6 * p)
        y_off = int((1 - ease_out_cubic(p)) * (H - 100))
        sheet = cur.crop((0, 100, W, H))
        base.paste(sheet, (0, 100 + y_off))
        c_top = Canvas(w=W, h=100)
        status_bar(c_top)
        base.paste(c_top.im.resize((W, 100), Image.LANCZOS), (0, 0))
        return base
    if kind == "sheet_down":
        base = cur.copy()
        y_off = int(ease_in_out_cubic(p) * (H - 100))
        if y_off < (H - 100):
            prev_dim = dim(prev, 0.4 * p)
            crop_prev = prev_dim.crop((0, 100, W, H))
            base.paste(crop_prev, (0, y_off + 100))
        c_top = Canvas(w=W, h=100)
        status_bar(c_top)
        base.paste(c_top.im.resize((W, 100), Image.LANCZOS), (0, 0))
        return base
    if kind == "zoom":
        z = 1 + 0.15 * ease_in_out_cubic(p)
        nw, nh = int(W * z), int(H * z)
        pz = prev.resize((nw, nh), Image.BICUBIC).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
        return Image.blend(pz, cur, ease_in_out_cubic(p))
    return cur


def frame_at(t):
    idx = max(i for i, (s, _) in enumerate(SCENES) if t >= s)
    s, fn = SCENES[idx]
    lt = t - s
    img = fn(lt)
    tr = TRANS[idx]
    if tr and lt < tr[1]:
        ps, pfn = SCENES[idx - 1]
        img = apply_transition(tr[0], img, pfn(t - ps), lt / tr[1])
    return img


def render_frame(i):
    return np.ascontiguousarray(np.asarray(frame_at(i / FPS), dtype=np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=float, nargs="*")
    ap.add_argument("--out", default="x_ad_15s.mp4")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2)))
    ap.add_argument("--no-audio", action="store_true")
    args = ap.parse_args()

    if args.preview is not None:
        os.makedirs("previews", exist_ok=True)
        for t in args.preview:
            path = f"previews/frame_{t:05.2f}.png"
            frame_at(t).save(path)
            print("wrote", path)
        return

    audio = None
    if not args.no_audio:
        audio = x_ad_audio.write_wav("x_ad_audio.wav")
        print("soundtrack:", audio)

    total = int(DUR * FPS)
    t0 = time.time()

    try:
        import imageio_ffmpeg
        out_params = ["-crf", "17", "-preset", "medium", "-movflags", "+faststart"]
        if audio:
            out_params += ["-b:a", "192k", "-shortest"]
        writer = imageio_ffmpeg.write_frames(args.out, (W, H), fps=FPS, codec="libx264", quality=None,
                                             macro_block_size=8, output_params=out_params,
                                             audio_path=audio, audio_codec="aac" if audio else None)
        writer.send(None)
        with Pool(args.workers) as pool:
            for i, fr in enumerate(pool.imap(render_frame, range(total), chunksize=3)):
                writer.send(fr)
                if i % 30 == 0:
                    print(f"  frame {i}/{total}  ({time.time() - t0:.1f}s)", flush=True)
        writer.close()
    except ImportError:
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
            "-i", "-",
        ]
        if audio:
            cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
        cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        with Pool(args.workers) as pool:
            for i, fr in enumerate(pool.imap(render_frame, range(total), chunksize=3)):
                proc.stdin.write(fr.tobytes())
                if i % 30 == 0:
                    print(f"  frame {i}/{total}  ({time.time() - t0:.1f}s)", flush=True)
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", errors="replace")
        if proc.wait() != 0:
            raise RuntimeError(f"ffmpeg failed:\n{err}")

    print(f"done -> {args.out}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
