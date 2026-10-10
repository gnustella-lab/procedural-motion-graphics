"""Example 05: Hyper-fast Rhythmic Cuts, Strobe Typography & Manga Speed Lines.
Demonstrates 4-frame hard cuts (7.5 cuts/sec), complementary palette switching,
procedural background patterns, and camera impact jitter.
"""

import sys, os, random, math
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.motion_engine import (
    lerp, rot_poly, get_font, apply_camera, apply_chromatic_aberration, precompute_vignette
)

W, H, FPS, DUR = 1920, 1080, 30, 2.0
N = int(FPS * DUR)
cx, cy = W / 2, H / 2

BG = (10, 10, 18)
WHITE = (245, 245, 250)
PAL = [(255, 46, 136), (0, 229, 255), (255, 214, 0), (124, 77, 255)]
WORDS = ["BOLD", "FAST", "LOUD", "SHARP", "CLEAN", "PUNCH", "FLOW", "IMPACT"]

vignette = precompute_vignette(W, H)

def render_frame(frame_idx):
    t = frame_idx / FPS
    # Cut every 4 frames (7.5 cuts per second)
    beat = frame_idx // 4
    local_subframe = (frame_idx % 4) / 4.0

    random.seed(beat)
    c1 = PAL[beat % len(PAL)]
    c2 = PAL[(beat + 2) % len(PAL)]

    layer = Image.new("RGBA", (W, H), c1 + (255,))
    draw = ImageDraw.Draw(layer)

    mode = beat % 3
    if mode == 0:  # Radial manga speed lines
        for _ in range(70):
            ang = random.uniform(0, 2.0 * math.pi)
            r0 = random.uniform(150, 400)
            draw.line(
                [cx + math.cos(ang) * r0, cy + math.sin(ang) * r0,
                 cx + math.cos(ang) * 2000, cy + math.sin(ang) * 2000],
                fill=c2, width=random.randint(2, 14)
            )
    elif mode == 1:  # Diagonal stripes
        offset = (t * 1500) % 160
        for x in range(-400, W + 400, 160):
            draw.polygon([(x + offset, 0), (x + offset + 70, 0), (x + offset - 330, H), (x + offset - 400, H)], fill=c2)
    else:  # Concentric spinning squares
        for i in range(12, 0, -1):
            draw.polygon(rot_poly(cx, cy, i * 90, 4, t * 3.0 + i * 0.15), fill=c2 if i % 2 == 1 else c1)

    word = WORDS[beat % len(WORDS)]
    font_size = int(lerp(280, 330, local_subframe))
    font = get_font(font_size, bold=True)

    # Offset drop shadow + hero text
    draw.text((cx + 12, cy + 12), word, font=font, fill=BG + (255,), anchor="mm")
    draw.text((cx, cy), word, font=font, fill=WHITE, anchor="mm")

    # Camera shake & chromatic glitch
    layer = apply_camera(layer, zoom=1.0 + 0.05 * local_subframe, shake_px=10.0, width=W, height=H)
    img = np.asarray(layer, np.float32)[..., :3]
    img = apply_chromatic_aberration(img, offset_px=8 if local_subframe < 0.25 else 2)
    img = img * vignette
    return img.clip(0, 255).astype(np.uint8)

if __name__ == "__main__":
    out_file = "examples_output_cuts.mp4"
    print(f"Rendering {N} frames to {out_file}...")
    writer = imageio.get_writer(out_file, fps=FPS, codec="libx264", quality=9, pixelformat="yuv420p")
    for i in range(N):
        writer.append_data(render_frame(i))
    writer.close()
    print("Done:", out_file)
