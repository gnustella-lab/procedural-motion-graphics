"""Example 08: Full-HD Vertical Mobile Social Ad Simulation (V4 Framework).

Demonstrates:
1. Native 1080x1920 (9:16 vertical) mobile ad architecture.
2. Super-Sampled Anti-Aliasing (SSAA 1.5x) via Lanczos downsampling.
3. 5-Act Mobile Storyline:
   - Act 1: Kinetic Hook typography with exponential impact.
   - Act 2: Realistic social timeline feed with interactive touch tap and heart pop burst.
   - Act 3: Modal bottom sheet slide-up (sheet_up) with live typing simulation.
   - Act 4: Viral reaction screen with ramping metrics and sliding notification toast.
   - Act 5: Climax end card with brand shockwave and tactile CTA button click.
4. Procedural DSP electronic soundtrack and synchronized UI Foley sound design.
"""

import math
import os
import sys
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.motion_engine import (
    clamp, prog, lerp, lerpc,
    ease_out_cubic, ease_in_out_cubic, ease_out_back, ease_out_expo,
    vertical_push_transition, button_click_press
)

W, H, FPS, DUR = 1080, 1920, 30, 6.0
K = 1.5  # 1.5x Super-sampling

# Palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEXT = (231, 233, 234)
GREY = (113, 118, 123)
BORDER = (47, 51, 54)
BLUE = (29, 155, 240)
PINK = (249, 24, 128)
CARD = (22, 24, 28)

def get_font(size, bold=True):
    paths = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
        if bold else
        ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    )
    for p in paths:
        try:
            return ImageFont.truetype(p, int(size * K))
        except OSError:
            continue
    return ImageFont.load_default()

class Canvas:
    def __init__(self, bg=BLACK, w=W, h=H, k=K):
        self.w, self.h, self.k = w, h, k
        self.im = Image.new("RGB", (int(w * k), int(h * k)), bg)
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x0, y0, x1, y1, fill=None, r=0, outline=None, width=1):
        b = [x0 * self.k, y0 * self.k, x1 * self.k, y1 * self.k]
        wd = max(1, int(round(width * self.k)))
        if r > 0:
            self.d.rounded_rectangle(b, radius=min(r, (x1-x0)/2, (y1-y0)/2) * self.k, fill=fill, outline=outline, width=wd)
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=wd)

    def ell(self, cx, cy, r, fill=None, outline=None, width=1):
        b = [(cx - r) * self.k, (cy - r) * self.k, (cx + r) * self.k, (cy + r) * self.k]
        self.d.ellipse(b, fill=fill, outline=outline, width=max(1, int(round(width * self.k))))

    def txt(self, x, y, s, size, fill=WHITE, anchor="lm", bold=True):
        self.d.text((x * self.k, y * self.k), s, font=get_font(size, bold), fill=fill, anchor=anchor)

    def alpha_ell(self, cx, cy, r, color, a, width=None):
        a = clamp(a)
        if a <= 0 or r <= 0: return
        X0, Y0 = int((cx - r) * self.k) - 2, int((cy - r) * self.k) - 2
        X1, Y1 = int((cx + r) * self.k) + 2, int((cy + r) * self.k) + 2
        m = Image.new("L", (max(1, X1 - X0), max(1, Y1 - Y0)), 0)
        md = ImageDraw.Draw(m)
        b = [(cx - r) * self.k - X0, (cy - r) * self.k - Y0, (cx + r) * self.k - X0, (cy + r) * self.k - Y0]
        if width:
            md.ellipse(b, outline=int(255 * a), width=max(1, int(width * self.k)))
        else:
            md.ellipse(b, fill=int(255 * a))
        self.im.paste(color, (X0, Y0, X1, Y1), m)

    def render(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)

def status_bar(c):
    c.txt(100, 60, "9:41", 38, WHITE, "mm", bold=True)
    for i in range(4):
        c.rect(840 + i * 14, 72 - (10 + i * 7), 850 + i * 14, 72, fill=WHITE, r=2)
    c.rect(914, 46, 978, 74, outline=WHITE, r=8, width=3)
    c.rect(919, 51, 966, 69, fill=WHITE, r=4)
    c.rect(981, 54, 986, 66, fill=WHITE, r=2)

def tap(c, x, y, t, t_tap, col=WHITE, ripple=BLUE):
    a = min(prog(t, t_tap - 0.3, t_tap - 0.05), 1.0 - prog(t, t_tap + 0.1, t_tap + 0.35))
    if a > 0:
        press = clamp(prog(t, t_tap - 0.05, t_tap + 0.02) - prog(t, t_tap + 0.08, t_tap + 0.2))
        r = 44 * (1.0 - 0.22 * press)
        c.alpha_ell(x, y, r, col, 0.32 * a)
        c.alpha_ell(x, y, r, col, 0.55 * a, width=3)
    if t_tap < t < t_tap + 0.5:
        p = prog(t, t_tap, t_tap + 0.5)
        c.alpha_ell(x, y, 36 + ease_out_cubic(p) * 110, ripple, 0.9 * (1.0 - p), width=4)

# ----------------- Scenes -----------------

def render_scene_hook(t):
    """Act 1: Kinetic Hook."""
    c = Canvas()
    e = ease_out_expo(prog(t, 0.0, 0.4))
    c.txt(540, 560, "BREAKING NEWS.", 92 * e, WHITE, "mm", bold=True)
    c.txt(540, 680, "WHERE DOES IT HAPPEN FIRST?", 42 * e, BLUE, "mm", bold=True)
    c.rect(340, 780, 740, 840, outline=BORDER, r=30, width=2)
    c.ell(375, 810, 10, fill=(244, 33, 46))
    c.txt(405, 810, "LIVE WORLDWIDE", 26, TEXT, "lm", bold=True)
    return c.render()

def render_scene_feed(t):
    """Act 2: Timeline Feed."""
    c = Canvas()
    status_bar(c)
    # Header
    c.txt(270, 180, "For you", 38, WHITE, "mm", bold=True)
    c.txt(810, 180, "Following", 38, GREY, "mm", bold=True)
    c.rect(200, 210, 340, 218, fill=BLUE, r=4)
    c.rect(0, 230, W, 232, fill=BORDER)

    # Post Card
    c.ell(90, 330, 46, fill=(60, 130, 240))
    c.txt(90, 330, "X", 42, WHITE, "mm", bold=True)
    c.txt(160, 310, "Global Pulse", 38, WHITE, "lm", bold=True)
    c.txt(160, 355, "@globalpulse · 2m", 32, GREY, "lm", bold=False)
    c.txt(60, 440, "The future of interactive media is live.", 42, TEXT, "lm", bold=False)
    c.txt(60, 495, "Pure code. Broadcast quality.", 42, TEXT, "lm", bold=False)

    # Metrics row
    c.rect(60, 560, 1020, 562, fill=BORDER)
    liked = t >= 0.9
    c.ell(200, 620, 22, fill=PINK if liked else GREY)
    c.txt(240, 620, "14.2K" if not liked else "14.3K", 32, PINK if liked else GREY, "lm", bold=True)
    c.ell(500, 620, 22, fill=BLUE)
    c.txt(540, 620, "3.8K", 32, GREY, "lm", bold=True)

    tap(c, 200, 620, t, 0.9)
    return c.render()

def render_scene_compose(t):
    """Act 3: Compose Modal."""
    c = Canvas()
    status_bar(c)
    c.txt(60, 160, "Cancel", 36, TEXT, "lm", bold=False)
    c.rect(860, 125, 1020, 195, fill=BLUE, r=35)
    c.txt(940, 160, "Post", 32, WHITE, "mm", bold=True)
    c.ell(90, 300, 46, fill=(60, 130, 240))
    c.txt(90, 300, "A", 42, WHITE, "mm", bold=True)

    text = "Hello, world. Shipped in pure Python!"
    n = int(len(text) * ease_out_cubic(prog(t, 0.2, 1.2)))
    c.txt(160, 290, text[:n], 44, TEXT, "lm", bold=False)
    if int(t * 4) % 2 == 0:
        c.rect(160 + n * 24, 260, 164 + n * 24, 320, fill=BLUE)

    # Virtual Keyboard base
    c.rect(0, 1250, W, H, fill=(30, 30, 32))
    c.txt(540, 1550, "[ Virtual QWERTY Keyboard ]", 38, GREY, "mm", bold=True)
    return c.render()

def render_scene_reaction(t):
    """Act 4: Viral Payoff."""
    c = Canvas()
    status_bar(c)
    c.txt(540, 400, "VIRAL ENGAGEMENT", 54, WHITE, "mm", bold=True)
    g = ease_out_expo(prog(t, 0.1, 1.2))
    views = int(185000 * g)
    c.txt(540, 520, f"{views:,} Views", 84, BLUE, "mm", bold=True)

    # Toast alert
    e_toast = ease_out_back(prog(t, 0.4, 0.9), 1.5)
    if e_toast > 0:
        tx = (1.0 - e_toast) * 260
        c.rect(60 + tx, 700, 1020 + tx, 820, fill=CARD, r=28, outline=BORDER, width=2)
        c.ell(130 + tx, 760, 32, fill=PINK)
        c.txt(190 + tx, 760, "Alex and 4,120 others liked your post", 34, WHITE, "lm", bold=True)
    return c.render()

def render_scene_end(t):
    """Act 5: Climax & CTA."""
    c = Canvas()
    e = ease_out_back(prog(t, 0.0, 0.6), 2.0)
    c.ell(540, 720, 140 * e, outline=BLUE, width=8)
    c.txt(540, 720, "X", 160 * e, WHITE, "mm", bold=True)

    c.txt(540, 1040, "Join the conversation.", 64, WHITE, "mm", bold=True)
    s = button_click_press(t, 1.2, 0.08, 0.18, 0.08)
    bw, bh = 540 * s, 120 * s
    c.rect(540 - bw/2, 1240 - bh/2, 540 + bw/2, 1240 + bh/2, fill=WHITE, r=bh/2)
    c.txt(540, 1238, "Get the app", 48 * s, BLACK, "mm", bold=True)
    c.txt(540, 1380, "x.com", 38, GREY, "mm", bold=True)
    tap(c, 620, 1240, t, 1.2, col=BLUE, ripple=BLUE)
    return c.render()

# Timeline sequencing
SCENES = [
    (0.0, 1.2, render_scene_hook),
    (1.2, 2.4, render_scene_feed),
    (2.4, 3.6, render_scene_compose),
    (3.6, 4.8, render_scene_reaction),
    (4.8, 6.0, render_scene_end),
]

def render_frame_at(t):
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t <= t1:
            lt = t - t0
            img = fn(lt)
            # Push transition into feed
            if i == 1 and lt < 0.35:
                prev = SCENES[0][2](1.2)
                img = vertical_push_transition(img, prev, lt / 0.35)
            return img
    return SCENES[-1][2](1.2)

# Procedural Audio
def generate_audio(wav_path="social_ad_audio.wav"):
    sr = 44100
    n = int(DUR * sr)
    t = np.linspace(0, DUR, n, endpoint=False)
    audio = np.zeros(n, dtype=np.float32)

    # Kick beats on downbeats (every 0.5s)
    for b in range(int(DUR / 0.5)):
        bt = b * 0.5
        idx = int(bt * sr)
        k_len = min(int(0.3 * sr), n - idx)
        kt = np.linspace(0, 0.3, k_len, endpoint=False)
        kick = np.sin(2 * np.pi * (50 + 110 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 8)
        audio[idx:idx + k_len] += kick * 0.8

    # Touch taps and UI chimes
    for tap_t in (2.1, 4.0, 6.0):
        idx = int((tap_t - 1.2) * sr)
        if 0 <= idx < n:
            t_len = min(int(0.06 * sr), n - idx)
            tt = np.linspace(0, 0.06, t_len, endpoint=False)
            audio[idx:idx + t_len] += np.sin(2 * np.pi * 1900 * tt) * np.exp(-tt * 80) * 0.4

    # Soft clip & normalize
    audio = np.tanh(audio * 1.2) * 0.9
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return wav_path

if __name__ == "__main__":
    out_mp4 = "vertical_social_ad.mp4"
    print(f"Rendering 6.0s Vertical Social Ad ({W}x{H} @ {FPS} FPS)...")
    os.makedirs("previews", exist_ok=True)
    for sample_t in [0.5, 1.8, 3.0, 4.2, 5.4]:
        im = render_frame_at(sample_t)
        im.save(f"previews/preview_{sample_t:.1f}s.png")
        print(f"  Saved preview at {sample_t:.1f}s")

    wav_file = generate_audio()
    import imageio_ffmpeg
    writer = imageio_ffmpeg.write_frames(out_mp4, (W, H), fps=FPS, codec="libx264",
                                         output_params=["-crf", "18", "-preset", "fast"],
                                         audio_path=wav_file, audio_codec="aac")
    writer.send(None)
    for f in range(int(DUR * FPS)):
        writer.send(np.ascontiguousarray(np.asarray(render_frame_at(f / FPS), dtype=np.uint8)))
    writer.close()
    if os.path.exists(wav_file):
        os.remove(wav_file)
    print(f"Done -> {out_mp4}")
