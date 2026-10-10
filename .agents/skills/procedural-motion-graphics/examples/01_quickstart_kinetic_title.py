"""Example 01: Quickstart Kinetic Title Sequence.
Renders a 3-second (90 frames) 1920x1080 kinetic text sequence with overshoot easing,
chromatic split extrusion, bloom glow, and camera push-in.
"""

import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.motion_engine import (
    ease_out_back, ease_in_expo, prog, lerp, get_font,
    apply_glow_bloom, apply_chromatic_aberration, precompute_vignette, precompute_grain
)

W, H, FPS, DUR = 1920, 1080, 30, 3.0
N = int(FPS * DUR)
cx, cy = W / 2, H / 2

BG = (10, 10, 18)
PINK = (255, 46, 136)
CYAN = (0, 229, 255)
WHITE = (245, 245, 250)

vignette = precompute_vignette(W, H)
grain = precompute_grain(W, H)

def render_frame(frame_idx):
    t = frame_idx / FPS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    word = "ANTIGRAVITY"
    font = get_font(180, bold=True)
    spacing = 140
    start_x = cx - spacing * (len(word) - 1) / 2

    for i, ch in enumerate(word):
        q = prog(t, 0.2 + i * 0.05, 0.9 + i * 0.05)
        out = prog(t, 2.3 + i * 0.03, 2.8)
        if q <= 0:
            continue
        y = lerp(-200, cy, ease_out_back(q, 2.0)) - ease_in_expo(out) * 800

        # Chromatic 3D offset extrusion
        draw.text((start_x + i * spacing + 6, y + 6), ch, font=font, fill=PINK + (160,), anchor="mm")
        draw.text((start_x + i * spacing - 6, y - 4), ch, font=font, fill=CYAN + (160,), anchor="mm")
        draw.text((start_x + i * spacing, y), ch, font=font, fill=WHITE, anchor="mm")

    # Composite over dark background
    bg = np.array(BG, np.float32)
    rgb = np.asarray(layer, np.float32)
    alpha = rgb[..., 3:4] / 255.0
    img = bg * (1.0 - alpha) + rgb[..., :3] * alpha

    # Post-processing passes
    img = apply_glow_bloom(img, threshold=80, intensity=0.5)
    img = apply_chromatic_aberration(img, offset_px=3)
    img = img * vignette + grain[frame_idx % len(grain)]
    return img.clip(0, 255).astype(np.uint8)

if __name__ == "__main__":
    out_file = "examples_output_title.mp4"
    print(f"Rendering {N} frames to {out_file}...")
    writer = imageio.get_writer(out_file, fps=FPS, codec="libx264", quality=9, pixelformat="yuv420p")
    for i in range(N):
        writer.append_data(render_frame(i))
    writer.close()
    print("Done:", out_file)
