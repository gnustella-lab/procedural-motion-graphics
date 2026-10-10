"""Example 04: Vector Stroke Reveal ("Trim Paths") & Elastic Pop.
Demonstrates procedural line-drawing along polygon vertices,
spring-damped elastic secondary animation, and masked title reveals.
"""

import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.motion_engine import (
    ease_in_out_cubic, ease_out_elastic, ease_out_expo, prog, clamp, lerp, rot_poly,
    get_font, apply_glow_bloom, precompute_vignette
)

W, H, FPS, DUR = 1920, 1080, 30, 3.0
N = int(FPS * DUR)
cx, cy = W / 2, H / 2

BG = (10, 10, 18)
PINK = (255, 46, 136)
CYAN = (0, 229, 255)
WHITE = (245, 245, 250)
vignette = precompute_vignette(W, H)

def render_frame(frame_idx):
    t = frame_idx / FPS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # 1. Stroke reveal (trim paths) hexagon
    p = ease_in_out_cubic(prog(t, 0.2, 1.2))
    hex_verts = rot_poly(cx, cy - 60, 140, 6, -math.pi / 2)
    hex_verts.append(hex_verts[0])  # Close loop

    segs = p * 6.0
    for i in range(int(segs) + 1):
        if i >= 6:
            break
        f_seg = clamp(segs - i)
        a, b = hex_verts[i], hex_verts[i + 1]
        draw.line([a, (lerp(a[0], b[0], f_seg), lerp(a[1], b[1], f_seg))], fill=CYAN, width=12)

    # 2. Inner triangle elastic pop
    tri_scale = ease_out_elastic(prog(t, 0.8, 2.0))
    if tri_scale > 0:
        tri_pts = rot_poly(cx, cy - 60, 75 * tri_scale, 3, -math.pi / 2 + (1.0 - tri_scale) * 2.0)
        draw.polygon(tri_pts, fill=PINK)

    # 3. Title reveal
    title = "PROCEDURAL MOTION"
    font = get_font(90, bold=True)
    title_w = draw.textlength(title, font=font)
    start_x = cx - title_w / 2

    cur_x = start_x
    for i, ch in enumerate(title):
        q = ease_out_expo(prog(t, 1.0 + i * 0.025, 1.8 + i * 0.025))
        if q > 0:
            y = cy + 150 + (1.0 - q) * 60
            draw.text((cur_x, y), ch, font=font, fill=WHITE + (int(255 * q),), anchor="ls")
        cur_x += draw.textlength(ch, font=font)

    bg = np.array(BG, np.float32)
    rgb = np.asarray(layer, np.float32)
    alpha = rgb[..., 3:4] / 255.0
    img = bg * (1.0 - alpha) + rgb[..., :3] * alpha
    img = apply_glow_bloom(img, threshold=85, intensity=0.5)
    img = img * vignette
    return img.clip(0, 255).astype(np.uint8)

if __name__ == "__main__":
    out_file = "examples_output_logo.mp4"
    print(f"Rendering {N} frames to {out_file}...")
    writer = imageio.get_writer(out_file, fps=FPS, codec="libx264", quality=9, pixelformat="yuv420p")
    for i in range(N):
        writer.append_data(render_frame(i))
    writer.close()
    print("Done:", out_file)
