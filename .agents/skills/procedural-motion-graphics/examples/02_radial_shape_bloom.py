"""Example 02: Procedural Radial Shape Grid & Geometric Morphing.
Demonstrates distance-based staggered entry, traveling sine wave ripples,
and real-time vertex count morphing (triangle -> square -> hexagon -> circle).
"""

import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.motion_engine import (
    ease_out_back, ease_in_expo, prog, lerpc, rot_poly,
    apply_glow_bloom, precompute_vignette
)

W, H, FPS, DUR = 1920, 1080, 30, 3.0
N = int(FPS * DUR)
cx, cy = W / 2, H / 2

BG = (10, 10, 18)
PINK = (255, 46, 136)
CYAN = (0, 229, 255)
YEL = (255, 214, 0)
VIO = (124, 77, 255)

vignette = precompute_vignette(W, H)

def render_frame(frame_idx):
    t = frame_idx / FPS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    cols, rows, s = 16, 9, 120
    ox, oy = (W - cols * s) / 2 + s / 2, (H - rows * s) / 2 + s / 2

    for j in range(rows):
        for i in range(cols):
            x, y = ox + i * s, oy + j * s
            dist = math.hypot(i - cols / 2, j - rows / 2)
            delay = dist * 0.06

            scale_in = ease_out_back(prog(t, delay, delay + 0.5))
            scale_out = ease_in_expo(prog(t, 2.2 + (cols - i) * 0.02, 2.8))
            total_scale = scale_in * (1.0 - scale_out)

            if total_scale <= 0:
                continue

            wave = 0.5 + 0.5 * math.sin(t * 5.0 - dist * 0.8)
            r = s * 0.38 * total_scale * (0.55 + 0.45 * wave)
            n_vertices = [3, 4, 6, 36][int((t * 1.6 + dist * 0.15)) % 4]
            ang = t * 2.0 + dist * 0.3
            color = lerpc(PINK, CYAN, wave) if (i + j) % 2 == 0 else lerpc(VIO, YEL, wave)

            poly = rot_poly(x, y, r, n_vertices, ang)
            if (i * 7 + j * 3) % 5 == 0:
                draw.polygon(poly, outline=color, width=4)
            else:
                draw.polygon(poly, fill=color)

    bg = np.array(BG, np.float32)
    rgb = np.asarray(layer, np.float32)
    alpha = rgb[..., 3:4] / 255.0
    img = bg * (1.0 - alpha) + rgb[..., :3] * alpha
    img = apply_glow_bloom(img, threshold=85, intensity=0.55)
    img = img * vignette
    return img.clip(0, 255).astype(np.uint8)

if __name__ == "__main__":
    out_file = "examples_output_grid.mp4"
    print(f"Rendering {N} frames to {out_file}...")
    writer = imageio.get_writer(out_file, fps=FPS, codec="libx264", quality=9, pixelformat="yuv420p")
    for i in range(N):
        writer.append_data(render_frame(i))
    writer.close()
    print("Done:", out_file)
